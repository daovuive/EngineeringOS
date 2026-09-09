from __future__ import annotations

import json
import math
import os
import tempfile
import threading
from contextlib import contextmanager
from datetime import date, timedelta
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any, Protocol

import fcntl


EmbeddingContract = dict[str, Any]
KNOWLEDGE_SOURCE = "knowledge"
MEMORY_SOURCE = "memory"
AUTHORITATIVE_AUTHORITY = "authoritative"
CONTEXTUAL_AUTHORITY = "contextual"
_LAST_UPDATED_PATTERN = re.compile(
    r"^\s*Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$", re.IGNORECASE | re.MULTILINE
)


class EmbeddingRuntime(Protocol):
    def embed(self, text: str) -> list[float]:
        """Create one embedding vector for text."""


class KnowledgeIndexError(RuntimeError):
    """Raised when a knowledge index cannot be loaded or queried."""


@dataclass(frozen=True)
class KnowledgeChunk:
    path: str
    heading: str
    text: str
    embedding: list[float]
    source_type: str = KNOWLEDGE_SOURCE
    last_updated: str | None = None
    authority: str = AUTHORITATIVE_AUTHORITY


@dataclass(frozen=True)
class IndexUpdateResult:
    path: str
    chunk_count: int
    changed: bool


_INDEX_THREAD_LOCK = threading.RLock()


def discover_markdown(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def read_markdown_chunks(path: Path, root: Path) -> list[tuple[str, str]]:
    relative_path = path.relative_to(root).as_posix()
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("<!-- eos-ingestion-")
        and not line.startswith("<!-- eos-ingested-at:")
    ]
    heading = path.stem
    sections: list[tuple[str, list[str]]] = []

    for line in lines:
        if line.startswith("#") and line.lstrip("#").startswith(" "):
            if sections and "\n".join(sections[-1][1]).strip():
                sections[-1][1].append("")
            heading = line.lstrip("#").strip()
            sections.append((heading, []))
        elif not sections:
            sections.append((heading, []))
        else:
            sections[-1][1].append(line)

    chunks = []
    for section_heading, section_lines in sections:
        text = "\n".join(section_lines).strip()
        if text:
            chunks.append((f"{relative_path}#{section_heading}", text))
    return chunks


def build_index(
    root: Path,
    runtime: EmbeddingRuntime,
    *,
    source_type: str = KNOWLEDGE_SOURCE,
    path_root: Path | None = None,
) -> list[KnowledgeChunk]:
    if source_type not in {KNOWLEDGE_SOURCE, MEMORY_SOURCE}:
        raise KnowledgeIndexError(f"Unsupported source type: {source_type}")

    chunks: list[KnowledgeChunk] = []
    relative_root = path_root or root
    for path in discover_markdown(root):
        last_updated = extract_last_updated(path) if source_type == MEMORY_SOURCE else None
        authority = (
            CONTEXTUAL_AUTHORITY
            if source_type == MEMORY_SOURCE
            else AUTHORITATIVE_AUTHORITY
        )
        for heading, text in read_markdown_chunks(path, relative_root):
            embedding = runtime.embed(text)
            if not embedding:
                raise KnowledgeIndexError(f"Empty embedding returned for {heading}.")
            path_value, heading_value = heading.split("#", 1)
            chunks.append(
                KnowledgeChunk(
                    path_value,
                    heading_value,
                    text,
                    embedding,
                    source_type,
                    last_updated,
                    authority,
                )
            )
    return chunks


def extract_last_updated(path: Path) -> str | None:
    """Read the repository date metadata used for memory freshness checks."""
    match = _LAST_UPDATED_PATTERN.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def is_stale_memory(
    chunk: KnowledgeChunk,
    *,
    max_age_days: int,
    today: date | None = None,
) -> bool:
    if chunk.source_type != MEMORY_SOURCE:
        return False
    if max_age_days < 0:
        raise KnowledgeIndexError("Memory max_age_days must not be negative.")
    if not chunk.last_updated:
        return True
    try:
        updated = date.fromisoformat(chunk.last_updated)
    except ValueError:
        return True
    return (today or date.today()) - updated > timedelta(days=max_age_days)


def select_retrieval_chunks(
    chunks: list[KnowledgeChunk],
    *,
    include_memory: bool = False,
    memory_max_age_days: int = 90,
    today: date | None = None,
) -> list[KnowledgeChunk]:
    """Select authoritative knowledge plus explicitly requested fresh memory."""
    selected: list[KnowledgeChunk] = []
    for chunk in chunks:
        if chunk.source_type != MEMORY_SOURCE:
            selected.append(chunk)
        elif include_memory and not is_stale_memory(
            chunk, max_age_days=memory_max_age_days, today=today
        ):
            selected.append(chunk)
    return selected


def save_index(
    path: Path,
    chunks: list[KnowledgeChunk],
    *,
    embedding_contract: EmbeddingContract,
) -> None:
    _validate_embedding_contract(embedding_contract)
    with index_write_lock(path):
        _save_index_atomic(path, chunks, embedding_contract=embedding_contract)


def rebuild_index(
    index_path: Path,
    sources: list[tuple[Path, str, Path | None]],
    runtime: EmbeddingRuntime,
    *,
    embedding_contract: EmbeddingContract,
) -> list[KnowledgeChunk]:
    """Rebuild all configured sources without racing incremental writers."""
    _validate_embedding_contract(embedding_contract)
    with index_write_lock(index_path):
        chunks: list[KnowledgeChunk] = []
        for root, source_type, path_root in sources:
            chunks.extend(
                build_index(
                    root,
                    runtime,
                    source_type=source_type,
                    path_root=path_root,
                )
            )
        _save_index_atomic(index_path, chunks, embedding_contract=embedding_contract)
        return chunks


def update_document_index(
    index_path: Path,
    document_path: Path,
    knowledge_root: Path,
    runtime: EmbeddingRuntime,
    *,
    embedding_contract: EmbeddingContract,
) -> IndexUpdateResult:
    """Incrementally replace one document's chunks under a coordinated lock."""
    index_path = index_path.resolve()
    document_path = document_path.resolve()
    knowledge_root = knowledge_root.resolve()
    try:
        relative_path = document_path.relative_to(knowledge_root).as_posix()
    except ValueError as error:
        raise KnowledgeIndexError("Indexed document must be inside the knowledge root.") from error
    if document_path.suffix.lower() != ".md" or not document_path.is_file():
        raise KnowledgeIndexError("Indexed document must be an existing Markdown file.")
    _validate_embedding_contract(embedding_contract)

    sections = read_markdown_chunks(document_path, knowledge_root)
    if not sections:
        raise KnowledgeIndexError("Saved document contains no indexable Markdown content.")

    with index_write_lock(index_path):
        chunks = (
            load_index(index_path, embedding_contract=embedding_contract)
            if index_path.exists()
            else []
        )
        current = [chunk for chunk in chunks if chunk.path == relative_path]
        expected = [(heading.split("#", 1)[1], text) for heading, text in sections]
        observed = [(chunk.heading, chunk.text) for chunk in current]
        if observed == expected:
            return IndexUpdateResult(relative_path, len(current), False)

        replacements: list[KnowledgeChunk] = []
        for heading, text in sections:
            embedding = runtime.embed(text)
            if not embedding:
                raise KnowledgeIndexError(f"Empty embedding returned for {heading}.")
            if len(embedding) != embedding_contract["dimensions"]:
                raise KnowledgeIndexError(
                    "Embedding dimensions do not match the configured contract: "
                    f"expected {embedding_contract['dimensions']}, got {len(embedding)}."
                )
            path_value, heading_value = heading.split("#", 1)
            replacements.append(
                KnowledgeChunk(path_value, heading_value, text, embedding)
            )
        retained = [chunk for chunk in chunks if chunk.path != relative_path]
        _save_index_atomic(
            index_path,
            retained + replacements,
            embedding_contract=embedding_contract,
        )
        return IndexUpdateResult(relative_path, len(replacements), True)


@contextmanager
def index_write_lock(index_path: Path):
    """Serialize index writers across threads and local processes."""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = index_path.with_suffix(index_path.suffix + ".lock")
    with _INDEX_THREAD_LOCK:
        with lock_path.open("a+b") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _save_index_atomic(
    path: Path,
    chunks: list[KnowledgeChunk],
    *,
    embedding_contract: EmbeddingContract,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": "1.1",
        "embedding": dict(embedding_contract),
        "chunks": [asdict(chunk) for chunk in chunks],
    }
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            json.dump(payload, temporary, indent=2)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def load_index(
    path: Path,
    *,
    embedding_contract: EmbeddingContract,
) -> list[KnowledgeChunk]:
    if not path.exists():
        raise KnowledgeIndexError(f"Knowledge index not found: {path}")
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise KnowledgeIndexError(f"Knowledge index is invalid JSON: {path}") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("chunks"), list):
        raise KnowledgeIndexError("Knowledge index has an unexpected format.")
    _validate_embedding_contract(embedding_contract)
    stored_contract = payload.get("embedding")
    if not isinstance(stored_contract, dict):
        raise KnowledgeIndexError(
            "Knowledge index is missing embedding compatibility metadata; "
            "rebuild the index."
        )
    if stored_contract != embedding_contract:
        raise KnowledgeIndexError(
            "Knowledge index embedding contract mismatch: "
            f"stored={stored_contract!r}, expected={embedding_contract!r}. "
            "Rebuild the index."
        )
    try:
        return [KnowledgeChunk(**item) for item in payload["chunks"]]
    except (TypeError, ValueError) as error:
        raise KnowledgeIndexError("Knowledge index contains an invalid chunk.") from error


def search_index(
    chunks: list[KnowledgeChunk],
    query: str,
    runtime: EmbeddingRuntime,
    *,
    limit: int = 5,
) -> list[tuple[float, KnowledgeChunk]]:
    if limit < 1:
        raise KnowledgeIndexError("Search limit must be positive.")
    query_vector = runtime.embed(query)
    results = [(cosine_similarity(query_vector, chunk.embedding), chunk) for chunk in chunks]
    return sorted(results, key=lambda item: item[0], reverse=True)[:limit]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left or not right:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def _validate_embedding_contract(contract: EmbeddingContract) -> None:
    required = {"contractVersion", "provider", "model", "dimensions"}
    if set(contract) != required:
        raise KnowledgeIndexError(
            "Embedding contract must contain exactly: "
            "contractVersion, provider, model, dimensions."
        )
    if not all(isinstance(contract[key], str) and contract[key] for key in (
        "contractVersion",
        "provider",
        "model",
    )):
        raise KnowledgeIndexError("Embedding contract identifiers must be non-empty strings.")
    if (
        not isinstance(contract["dimensions"], int)
        or isinstance(contract["dimensions"], bool)
        or contract["dimensions"] < 1
    ):
        raise KnowledgeIndexError("Embedding contract dimensions must be a positive integer.")
