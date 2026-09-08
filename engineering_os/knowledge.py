from __future__ import annotations

import json
import math
from datetime import date, timedelta
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any, Protocol


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


def discover_markdown(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def read_markdown_chunks(path: Path, root: Path) -> list[tuple[str, str]]:
    relative_path = path.relative_to(root).as_posix()
    lines = path.read_text(encoding="utf-8").splitlines()
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
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": "1.1",
        "embedding": dict(embedding_contract),
        "chunks": [asdict(chunk) for chunk in chunks],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


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
