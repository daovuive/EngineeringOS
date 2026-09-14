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

from engineering_os.chunking import ChunkingConfig, read_markdown_chunk_drafts
from engineering_os.lexical import build_lexical_index, validate_lexical_index
from engineering_os.pdf import read_pdf_chunk_drafts
from engineering_os.log_ingestion import (
    LogIngestionConfig,
    discover_allowed_logs,
    read_log_chunk_drafts,
)


EmbeddingContract = dict[str, Any]
KNOWLEDGE_SOURCE = "knowledge"
MEMORY_SOURCE = "memory"
LOG_SOURCE = "log"
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
    heading_path: tuple[str, ...] = ()
    document_type: str = "markdown"
    language: str | None = None
    project: str | None = None
    version: str | None = None
    tags: tuple[str, ...] = ()
    document_id: str = ""
    chunk_id: str = ""
    chunk_index: int = 0
    page_start: int | None = None
    page_end: int | None = None
    source_timestamp: str | None = None
    document_title: str | None = None
    document_author: str | None = None


@dataclass(frozen=True)
class IndexUpdateResult:
    path: str
    chunk_count: int
    changed: bool


@dataclass(frozen=True)
class KnowledgeIndex:
    """Loaded vector chunks plus the matching persisted lexical corpus."""

    chunks: list[KnowledgeChunk]
    lexical: dict[str, Any]
    schema_version: str


_INDEX_THREAD_LOCK = threading.RLock()


def discover_markdown(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def discover_documents(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and path.suffix.lower() in {".md", ".pdf"}
    )


def read_document_chunk_drafts(
    path: Path,
    root: Path,
    *,
    chunking: ChunkingConfig | None = None,
    default_language: str | None = None,
):
    if path.suffix.lower() == ".pdf":
        return read_pdf_chunk_drafts(
            path, root, config=chunking, default_language=default_language
        )
    return read_markdown_chunk_drafts(
        path, root, config=chunking, default_language=default_language
    )


def read_markdown_chunks(path: Path, root: Path) -> list[tuple[str, str]]:
    """Backward-compatible tuple view over token-aware Markdown chunks."""
    return [
        (f"{draft.path}#{draft.heading}", draft.text)
        for draft in read_markdown_chunk_drafts(path, root)
    ]


def build_index(
    root: Path,
    runtime: EmbeddingRuntime,
    *,
    source_type: str = KNOWLEDGE_SOURCE,
    path_root: Path | None = None,
    chunking: ChunkingConfig | None = None,
    default_language: str | None = None,
    pdf_enabled: bool = True,
) -> list[KnowledgeChunk]:
    if source_type not in {KNOWLEDGE_SOURCE, MEMORY_SOURCE}:
        raise KnowledgeIndexError(f"Unsupported source type: {source_type}")

    chunks: list[KnowledgeChunk] = []
    relative_root = path_root or root
    for path in discover_documents(root):
        if path.suffix.lower() == ".pdf" and not pdf_enabled:
            continue
        if source_type == MEMORY_SOURCE and path.suffix.lower() != ".md":
            continue
        last_updated = extract_last_updated(path) if source_type == MEMORY_SOURCE else None
        authority = (
            CONTEXTUAL_AUTHORITY
            if source_type == MEMORY_SOURCE
            else AUTHORITATIVE_AUTHORITY
        )
        for draft in read_document_chunk_drafts(
            path,
            relative_root,
            chunking=chunking,
            default_language=default_language,
        ):
            embedding = runtime.embed(draft.text)
            if not embedding:
                raise KnowledgeIndexError(
                    f"Empty embedding returned for {draft.path}#{draft.heading}."
                )
            chunks.append(
                KnowledgeChunk(
                    draft.path,
                    draft.heading,
                    draft.text,
                    embedding,
                    source_type,
                    last_updated,
                    authority,
                    draft.heading_path,
                    draft.document_type,
                    draft.language,
                    draft.project,
                    draft.version,
                    draft.tags,
                    draft.document_id,
                    draft.chunk_id,
                    draft.chunk_index,
                    getattr(draft, "page_start", None),
                    getattr(draft, "page_end", None),
                    getattr(draft, "source_timestamp", None),
                    getattr(draft, "document_title", None),
                    getattr(draft, "document_author", None),
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
    chunking: ChunkingConfig | None = None,
    default_language: str | None = None,
    pdf_enabled: bool = True,
    log_config: LogIngestionConfig | None = None,
    project_root: Path | None = None,
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
                    chunking=chunking,
                    default_language=default_language,
                    pdf_enabled=pdf_enabled,
                )
            )
        if log_config is not None and log_config.enabled:
            if project_root is None:
                raise KnowledgeIndexError("Project root is required for log ingestion.")
            for log_path in discover_allowed_logs(project_root, log_config):
                for draft in read_log_chunk_drafts(
                    log_path,
                    project_root,
                    config=chunking,
                    default_language=default_language,
                ):
                    embedding = runtime.embed(draft.text)
                    if not embedding:
                        raise KnowledgeIndexError(
                            f"Empty embedding returned for {draft.path}#{draft.heading}."
                        )
                    chunks.append(
                        KnowledgeChunk(
                            draft.path,
                            draft.heading,
                            draft.text,
                            embedding,
                            LOG_SOURCE,
                            None,
                            CONTEXTUAL_AUTHORITY,
                            draft.heading_path,
                            draft.document_type,
                            draft.language,
                            draft.project,
                            draft.version,
                            draft.tags,
                            draft.document_id,
                            draft.chunk_id,
                            draft.chunk_index,
                            None,
                            None,
                            draft.source_timestamp,
                            None,
                            None,
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
    chunking: ChunkingConfig | None = None,
    default_language: str | None = None,
) -> IndexUpdateResult:
    """Incrementally replace one document's chunks under a coordinated lock."""
    index_path = index_path.resolve()
    document_path = document_path.resolve()
    knowledge_root = knowledge_root.resolve()
    try:
        relative_path = document_path.relative_to(knowledge_root).as_posix()
    except ValueError as error:
        raise KnowledgeIndexError("Indexed document must be inside the knowledge root.") from error
    if document_path.suffix.lower() not in {".md", ".pdf"} or not document_path.is_file():
        raise KnowledgeIndexError("Indexed document must be an existing Markdown or PDF file.")
    _validate_embedding_contract(embedding_contract)

    drafts = read_document_chunk_drafts(
        document_path,
        knowledge_root,
        chunking=chunking,
        default_language=default_language,
    )
    if not drafts:
        raise KnowledgeIndexError("Saved document contains no indexable content.")

    with index_write_lock(index_path):
        chunks = (
            load_index(index_path, embedding_contract=embedding_contract)
            if index_path.exists()
            else []
        )
        current = [chunk for chunk in chunks if chunk.path == relative_path]
        expected = [(draft.chunk_id, draft.text) for draft in drafts]
        observed = [(chunk.chunk_id, chunk.text) for chunk in current]
        if current and not all(chunk.chunk_id for chunk in current):
            observed = []
        if observed == expected:
            return IndexUpdateResult(relative_path, len(current), False)

        replacements: list[KnowledgeChunk] = []
        for draft in drafts:
            embedding = runtime.embed(draft.text)
            if not embedding:
                raise KnowledgeIndexError(
                    f"Empty embedding returned for {draft.path}#{draft.heading}."
                )
            if len(embedding) != embedding_contract["dimensions"]:
                raise KnowledgeIndexError(
                    "Embedding dimensions do not match the configured contract: "
                    f"expected {embedding_contract['dimensions']}, got {len(embedding)}."
                )
            replacements.append(
                KnowledgeChunk(
                    draft.path,
                    draft.heading,
                    draft.text,
                    embedding,
                    KNOWLEDGE_SOURCE,
                    None,
                    AUTHORITATIVE_AUTHORITY,
                    draft.heading_path,
                    draft.document_type,
                    draft.language,
                    draft.project,
                    draft.version,
                    draft.tags,
                    draft.document_id,
                    draft.chunk_id,
                    draft.chunk_index,
                    getattr(draft, "page_start", None),
                    getattr(draft, "page_end", None),
                    getattr(draft, "source_timestamp", None),
                    getattr(draft, "document_title", None),
                    getattr(draft, "document_author", None),
                )
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
        "schemaVersion": "2.0",
        "embedding": dict(embedding_contract),
        "chunks": [asdict(chunk) for chunk in chunks],
        "lexical": build_lexical_index(chunks),
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
    """Load chunks while preserving the pre-2.0 public API."""
    return load_knowledge_index(path, embedding_contract=embedding_contract).chunks


def load_knowledge_index(
    path: Path,
    *,
    embedding_contract: EmbeddingContract,
) -> KnowledgeIndex:
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
    _validate_embedding_contract(stored_contract)
    if not _embedding_contracts_match(stored_contract, embedding_contract):
        raise KnowledgeIndexError(
            "Knowledge index embedding contract mismatch: "
            f"stored={stored_contract!r}, expected={embedding_contract!r}. "
            "Rebuild the index."
        )
    schema_version = payload.get("schemaVersion")
    if schema_version not in {"1.1", "2.0"}:
        raise KnowledgeIndexError(
            f"Unsupported knowledge index schema {schema_version!r}; rebuild the index."
        )
    try:
        chunks = [_chunk_from_payload(item) for item in payload["chunks"]]
    except (TypeError, ValueError) as error:
        raise KnowledgeIndexError("Knowledge index contains an invalid chunk.") from error
    lexical = validate_lexical_index(payload.get("lexical"), chunks)
    return KnowledgeIndex(chunks, lexical, schema_version)


def _chunk_from_payload(item: Any) -> KnowledgeChunk:
    if not isinstance(item, dict):
        raise TypeError("chunk must be an object")
    normalized = dict(item)
    for key in ("heading_path", "tags"):
        value = normalized.get(key)
        if isinstance(value, list):
            normalized[key] = tuple(value)
    return KnowledgeChunk(**normalized)


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


def _embedding_contracts_match(
    stored: EmbeddingContract,
    expected: EmbeddingContract,
) -> bool:
    """Compare v1 contracts while accepting the legacy Ollama ``:latest`` alias.

    Older indexes may persist ``model:latest`` while current runtime contracts
    canonicalize the same Ollama reference to ``model``. All other contract
    fields remain exact compatibility boundaries.
    """
    if stored == expected:
        return True
    if any(
        stored[key] != expected[key]
        for key in ("contractVersion", "provider", "dimensions")
    ):
        return False
    stored_model = stored["model"]
    expected_model = expected["model"]
    return stored_model.removesuffix(":latest") == expected_model.removesuffix(
        ":latest"
    )
