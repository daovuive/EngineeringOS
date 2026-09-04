from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol


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


def build_index(root: Path, runtime: EmbeddingRuntime) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for path in discover_markdown(root):
        for heading, text in read_markdown_chunks(path, root):
            embedding = runtime.embed(text)
            if not embedding:
                raise KnowledgeIndexError(f"Empty embedding returned for {heading}.")
            path_value, heading_value = heading.split("#", 1)
            chunks.append(KnowledgeChunk(path_value, heading_value, text, embedding))
    return chunks


def save_index(path: Path, chunks: list[KnowledgeChunk]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schemaVersion": "1.0", "chunks": [asdict(chunk) for chunk in chunks]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_index(path: Path) -> list[KnowledgeChunk]:
    if not path.exists():
        raise KnowledgeIndexError(f"Knowledge index not found: {path}")
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise KnowledgeIndexError(f"Knowledge index is invalid JSON: {path}") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("chunks"), list):
        raise KnowledgeIndexError("Knowledge index has an unexpected format.")
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
