"""Deterministic token-aware Markdown chunking and metadata extraction."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MAX_TOKENS = 500
DEFAULT_OVERLAP_TOKENS = 80
DEFAULT_MIN_TOKENS = 80
_TOKEN_PATTERN = re.compile(r"[\w]+|[^\w\s]", re.UNICODE)
_FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


class ChunkingError(RuntimeError):
    """Raised when chunking configuration or input is invalid."""


@dataclass(frozen=True)
class ChunkingConfig:
    max_tokens: int = DEFAULT_MAX_TOKENS
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS
    min_tokens: int = DEFAULT_MIN_TOKENS

    @classmethod
    def from_settings(cls, settings: dict[str, Any]) -> "ChunkingConfig":
        knowledge = settings.get("knowledge", {})
        if not isinstance(knowledge, dict):
            raise ChunkingError("knowledge settings must be an object.")
        values = knowledge.get("chunking", {})
        if not isinstance(values, dict):
            raise ChunkingError("knowledge.chunking must be an object.")
        config = cls(
            max_tokens=_positive_int(values, "maxTokens", DEFAULT_MAX_TOKENS),
            overlap_tokens=_non_negative_int(
                values, "overlapTokens", DEFAULT_OVERLAP_TOKENS
            ),
            min_tokens=_positive_int(values, "minTokens", DEFAULT_MIN_TOKENS),
        )
        if config.overlap_tokens >= config.max_tokens:
            raise ChunkingError("chunk overlap must be smaller than maxTokens.")
        if config.min_tokens > config.max_tokens:
            raise ChunkingError("chunk minTokens must not exceed maxTokens.")
        return config


@dataclass(frozen=True)
class MarkdownChunkDraft:
    path: str
    heading: str
    heading_path: tuple[str, ...]
    text: str
    document_type: str
    language: str | None
    project: str | None
    version: str | None
    tags: tuple[str, ...]
    document_id: str
    chunk_id: str
    chunk_index: int


def estimate_tokens(text: str) -> int:
    """Return a deterministic local approximation suitable for chunk bounds."""
    return len(_TOKEN_PATTERN.findall(text))


def split_text(text: str, config: ChunkingConfig | None = None) -> list[str]:
    """Split normalized non-Markdown text with the shared token policy."""
    return _split_section(text.strip(), config or ChunkingConfig()) if text.strip() else []


def read_markdown_chunk_drafts(
    path: Path,
    root: Path,
    *,
    config: ChunkingConfig | None = None,
    default_language: str | None = None,
) -> list[MarkdownChunkDraft]:
    config = config or ChunkingConfig()
    relative_path = path.relative_to(root).as_posix()
    raw = path.read_text(encoding="utf-8")
    raw = "\n".join(
        line
        for line in raw.splitlines()
        if not line.startswith("<!-- eos-ingestion-")
        and not line.startswith("<!-- eos-ingested-at:")
    )
    metadata, content = _frontmatter(raw)
    language = _optional_text(metadata.get("language")) or default_language
    project = _optional_text(metadata.get("project")) or _project_from_path(relative_path)
    version = _optional_text(metadata.get("version"))
    tags = _tags(metadata.get("tags"))
    document_type = _optional_text(metadata.get("document_type")) or "markdown"
    document_id = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:24]

    drafts: list[MarkdownChunkDraft] = []
    chunk_index = 0
    for heading, heading_path, section in _markdown_sections(path.stem, content):
        for piece in _split_section(section, config):
            identity = "\0".join(
                (document_id, "/".join(heading_path), str(chunk_index), piece)
            )
            drafts.append(
                MarkdownChunkDraft(
                    relative_path,
                    heading,
                    heading_path,
                    piece,
                    document_type,
                    language,
                    project,
                    version,
                    tags,
                    document_id,
                    hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32],
                    chunk_index,
                )
            )
            chunk_index += 1
    return drafts


def _markdown_sections(
    fallback_heading: str, content: str
) -> list[tuple[str, tuple[str, ...], str]]:
    hierarchy: list[str] = []
    heading = fallback_heading
    heading_path = (fallback_heading,)
    body: list[str] = []
    sections: list[tuple[str, tuple[str, ...], str]] = []
    in_fence = False

    def flush() -> None:
        text = "\n".join(body).strip()
        if text:
            sections.append((heading, heading_path, text))

    for line in content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        match = None if in_fence else re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            flush()
            body = []
            level = len(match.group(1))
            title = match.group(2).strip()
            hierarchy = hierarchy[: level - 1]
            hierarchy.append(title)
            heading = title
            heading_path = tuple(hierarchy)
        else:
            body.append(line)
    flush()
    return sections


def _split_section(text: str, config: ChunkingConfig) -> list[str]:
    if estimate_tokens(text) <= config.max_tokens:
        return [text]
    units = _semantic_units(text, config.max_tokens)
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for unit in units:
        count = estimate_tokens(unit)
        separator = 1 if current else 0
        if current and current_tokens + separator + count > config.max_tokens:
            chunks.append("\n\n".join(current).strip())
            available_overlap = max(0, config.max_tokens - count - 1)
            overlap = _overlap_tail(
                chunks[-1], min(config.overlap_tokens, available_overlap)
            )
            current = [overlap] if overlap else []
            current_tokens = estimate_tokens(overlap)
        current.append(unit)
        current_tokens += separator + count
    if current:
        final = "\n\n".join(current).strip()
        if final:
            chunks.append(final)
    if len(chunks) > 1 and estimate_tokens(chunks[-1]) < config.min_tokens:
        tail = chunks.pop()
        if tail not in chunks[-1] and estimate_tokens(f"{chunks[-1]}\n\n{tail}") <= config.max_tokens:
            chunks[-1] = f"{chunks[-1]}\n\n{tail}".strip()
        else:
            chunks.append(tail)
    return chunks


def _semantic_units(text: str, max_tokens: int) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        if not stripped and not in_fence:
            if current:
                blocks.extend(_split_oversized_block("\n".join(current), max_tokens))
                current = []
        else:
            current.append(line)
    if current:
        blocks.extend(_split_oversized_block("\n".join(current), max_tokens))
    return blocks


def _split_oversized_block(block: str, max_tokens: int) -> list[str]:
    if estimate_tokens(block) <= max_tokens:
        return [block]
    lines = block.splitlines()
    pieces: list[str] = []
    current: list[str] = []
    for line in lines:
        if estimate_tokens(line) > max_tokens:
            if current:
                pieces.append("\n".join(current))
                current = []
            words = line.split()
            for start in range(0, len(words), max_tokens):
                pieces.append(" ".join(words[start : start + max_tokens]))
            continue
        candidate = "\n".join(current + [line])
        if current and estimate_tokens(candidate) > max_tokens:
            pieces.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        pieces.append("\n".join(current))
    return pieces


def _overlap_tail(text: str, maximum: int) -> str:
    if maximum <= 0:
        return ""
    lines = text.splitlines()
    selected: list[str] = []
    count = 0
    for line in reversed(lines):
        line_tokens = estimate_tokens(line)
        if selected and count + line_tokens > maximum:
            break
        if line_tokens > maximum:
            words = line.split()
            selected.append(" ".join(words[-maximum:]))
            break
        selected.append(line)
        count += line_tokens
    return "\n".join(reversed(selected)).strip()


def _frontmatter(content: str) -> tuple[dict[str, Any], str]:
    match = _FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content
    values: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator and re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", key.strip()):
            values[key.strip().lower()] = value.strip().strip("\"'")
    return values, content[match.end() :]


def _tags(value: Any) -> tuple[str, ...]:
    if not isinstance(value, str) or not value.strip():
        return ()
    cleaned = value.strip().strip("[]")
    return tuple(
        dict.fromkeys(part.strip().strip("\"'") for part in cleaned.split(",") if part.strip())
    )


def _project_from_path(path: str) -> str | None:
    parts = Path(path).parts
    if len(parts) >= 2 and parts[0] == "projects":
        return parts[1]
    return None


def _optional_text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _positive_int(values: dict[str, Any], key: str, default: int) -> int:
    value = values.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ChunkingError(f"knowledge.chunking.{key} must be a positive integer.")
    return value


def _non_negative_int(values: dict[str, Any], key: str, default: int) -> int:
    value = values.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ChunkingError(f"knowledge.chunking.{key} must be a non-negative integer.")
    return value
