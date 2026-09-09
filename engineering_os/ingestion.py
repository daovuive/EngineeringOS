from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import (
    IndexUpdateResult,
    KnowledgeIndexError,
    index_write_lock,
    update_document_index,
)
from engineering_os.llm import LLMError, LLMRuntime, create_runtime, get_embedding_contract


SUPPORTED_SUFFIXES = {".md": "markdown", ".markdown": "markdown", ".txt": "text"}
DEFAULT_MAX_BYTES = 2 * 1024 * 1024
_HASH_PATTERN = re.compile(r"^<!-- eos-ingestion-sha256: ([0-9a-f]{64}) -->$", re.MULTILINE)


class KnowledgeIngestionError(RuntimeError):
    """Raised before a document can be saved safely."""


@dataclass(frozen=True)
class IngestionResult:
    document_path: str
    import_outcome: str
    indexing_state: str
    chunk_count: int | None
    index_changed: bool | None
    error: str | None = None

    @property
    def ready_for_rag(self) -> bool:
        return self.indexing_state == "indexed"


def ingest_path(
    paths: ProjectPaths,
    source: Path,
    *,
    title: str | None = None,
    auto_index: bool = True,
    runtime: LLMRuntime | None = None,
) -> IngestionResult:
    source = source.expanduser().resolve()
    if not source.is_file() or source.is_symlink():
        raise KnowledgeIngestionError("Input file does not exist or is not a regular file.")
    if source == paths.root.resolve() / "README.md":
        raise KnowledgeIngestionError("The protected root README cannot be imported.")

    settings, knowledge_root, _, max_bytes = _ingestion_settings(paths)
    if source.stat().st_size > max_bytes:
        raise KnowledgeIngestionError(f"Input exceeds the {max_bytes}-byte limit.")
    try:
        source.relative_to(knowledge_root)
        inside_knowledge = True
    except ValueError:
        inside_knowledge = False
    if inside_knowledge and source.suffix.lower() == ".md":
        if source.stat().st_size > max_bytes:
            raise KnowledgeIngestionError(f"Input exceeds the {max_bytes}-byte limit.")
        try:
            existing_content = source.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise KnowledgeIngestionError("Input must be valid UTF-8 text.") from error
        if not existing_content.strip():
            raise KnowledgeIngestionError("Input content must not be empty.")
        return _finish_indexing(
            paths,
            source,
            "already_in_knowledge",
            auto_index,
            runtime,
            settings,
        )

    return ingest_bytes(
        paths,
        source.read_bytes(),
        source_name=source.name,
        title=title,
        auto_index=auto_index,
        runtime=runtime,
    )


def ingest_text(
    paths: ProjectPaths,
    content: str,
    *,
    title: str | None = None,
    auto_index: bool = True,
    runtime: LLMRuntime | None = None,
) -> IngestionResult:
    return ingest_bytes(
        paths,
        content.encode("utf-8"),
        source_name="direct-text.txt",
        title=title,
        auto_index=auto_index,
        runtime=runtime,
    )


def ingest_bytes(
    paths: ProjectPaths,
    content: bytes,
    *,
    source_name: str,
    title: str | None = None,
    auto_index: bool = True,
    runtime: LLMRuntime | None = None,
) -> IngestionResult:
    settings, knowledge_root, inbox, max_bytes = _ingestion_settings(paths)
    if not isinstance(content, bytes):
        raise KnowledgeIngestionError("Input content must be bytes.")
    if not content or len(content) > max_bytes:
        if not content:
            raise KnowledgeIngestionError("Input content must not be empty.")
        raise KnowledgeIngestionError(f"Input exceeds the {max_bytes}-byte limit.")

    suffix = Path(source_name).suffix.lower()
    source_format = SUPPORTED_SUFFIXES.get(suffix)
    if source_format is None:
        raise KnowledgeIngestionError(
            "Unsupported file format. Supported formats: .md, .markdown, and .txt."
        )
    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise KnowledgeIngestionError("Input must be valid UTF-8 text.") from error
    if not decoded.strip():
        raise KnowledgeIngestionError("Input content must not be empty.")

    digest = hashlib.sha256(content).hexdigest()
    derived_title = _derive_title(title, decoded, Path(source_name).stem)
    filename_source = (
        derived_title
        if title is not None or source_name == "direct-text.txt"
        else Path(source_name).stem
    )
    filename = _safe_filename(filename_source)
    stored = _stored_markdown(decoded, derived_title, source_name, source_format, digest)
    inbox.mkdir(parents=False, exist_ok=True)

    ingestion_guard = paths.resolve(
        settings.get("knowledge", {}).get("index", "runtime/index/knowledge.json")
    ).with_name("knowledge-ingestion")
    with index_write_lock(ingestion_guard):
        duplicate = _find_duplicate(inbox, digest)
        if duplicate is not None:
            document = duplicate
            outcome = "unchanged"
        else:
            document = _collision_safe_target(inbox, filename, digest)
            _write_text_atomic(document, stored)
            outcome = "saved"

    return _finish_indexing(
        paths,
        document,
        outcome,
        auto_index,
        runtime,
        settings,
    )


def retry_document_index(
    paths: ProjectPaths,
    document_path: str,
    *,
    runtime: LLMRuntime | None = None,
) -> IngestionResult:
    settings, knowledge_root, _, _ = _ingestion_settings(paths)
    document = paths.resolve(document_path).resolve()
    try:
        document.relative_to(knowledge_root)
    except ValueError as error:
        raise KnowledgeIngestionError("Retry path must be inside the knowledge root.") from error
    if document.suffix.lower() != ".md" or not document.is_file():
        raise KnowledgeIngestionError("Retry path must name an existing Markdown document.")
    return _finish_indexing(
        paths,
        document,
        "existing",
        True,
        runtime,
        settings,
    )


def _finish_indexing(
    paths: ProjectPaths,
    document: Path,
    outcome: str,
    auto_index: bool,
    runtime: LLMRuntime | None,
    settings: dict[str, Any],
) -> IngestionResult:
    relative = document.relative_to(paths.root.resolve()).as_posix()
    if not auto_index:
        return IngestionResult(relative, outcome, "skipped", None, None)
    knowledge = settings.get("knowledge", {})
    try:
        runtime_config = load_runtime_config(paths)
        active_runtime = runtime or create_runtime(runtime_config)
        update: IndexUpdateResult = update_document_index(
            paths.resolve(knowledge.get("index", "runtime/index/knowledge.json")),
            document,
            paths.resolve(knowledge.get("root", "knowledge")),
            active_runtime,
            embedding_contract=get_embedding_contract(runtime_config),
        )
    except (KnowledgeIndexError, LLMError) as error:
        return IngestionResult(relative, outcome, "failed", None, None, str(error))
    except OSError:
        return IngestionResult(
            relative, outcome, "failed", None, None, "Index persistence failed."
        )
    return IngestionResult(
        relative,
        outcome,
        "indexed",
        update.chunk_count,
        update.changed,
    )


def _ingestion_settings(
    paths: ProjectPaths,
) -> tuple[dict[str, Any], Path, Path, int]:
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    if not isinstance(knowledge, dict):
        raise KnowledgeIngestionError("knowledge settings must be an object.")
    ingestion = knowledge.get("ingestion", {})
    if not isinstance(ingestion, dict):
        raise KnowledgeIngestionError("knowledge.ingestion must be an object.")
    max_bytes = ingestion.get("maxBytes", DEFAULT_MAX_BYTES)
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 1:
        raise KnowledgeIngestionError("knowledge.ingestion.maxBytes must be positive.")
    knowledge_root = paths.resolve(knowledge.get("root", "knowledge")).resolve()
    inbox = paths.resolve(ingestion.get("directory", "knowledge/inbox")).resolve()
    try:
        inbox.relative_to(knowledge_root)
    except ValueError as error:
        raise KnowledgeIngestionError("Ingestion directory must be inside knowledge root.") from error
    if not knowledge_root.is_dir() or not inbox.is_dir():
        raise KnowledgeIngestionError("Configured knowledge or ingestion directory is unavailable.")
    return settings, knowledge_root, inbox, max_bytes


def _derive_title(title: str | None, content: str, fallback: str) -> str:
    if title is not None:
        if not isinstance(title, str) or not title.strip():
            raise KnowledgeIngestionError("Title must be non-empty text when provided.")
        return title.strip()[:160]
    for line in content.splitlines():
        candidate = line.strip().lstrip("#").strip()
        if candidate:
            return candidate[:160]
    return fallback or "knowledge-note"


def _safe_filename(value: str) -> str:
    value = re.sub(r"[\\/\x00-\x1f:*?\"<>|]+", "-", value.strip())
    value = re.sub(r"\s+", "-", value).strip(" .-")
    if not value:
        value = "knowledge-note"
    return f"{value[:100]}.md"


def _stored_markdown(
    content: str,
    title: str,
    source_name: str,
    source_format: str,
    digest: str,
) -> str:
    safe_source = Path(source_name).name.replace("--", "—")
    metadata = (
        f"<!-- eos-ingestion-sha256: {digest} -->\n"
        f"<!-- eos-ingestion-source: {safe_source} -->\n"
        f"<!-- eos-ingestion-format: {source_format} -->\n"
        f"<!-- eos-ingested-at: {datetime.now(timezone.utc).isoformat()} -->\n\n"
    )
    if source_format == "markdown":
        return metadata + content
    return metadata + f"# {title}\n\n" + content


def _find_duplicate(inbox: Path, digest: str) -> Path | None:
    for candidate in sorted(inbox.glob("*.md")):
        try:
            prefix = candidate.read_text(encoding="utf-8")[:512]
        except (OSError, UnicodeDecodeError):
            continue
        match = _HASH_PATTERN.search(prefix)
        if match and match.group(1) == digest:
            return candidate
    return None


def _collision_safe_target(inbox: Path, filename: str, digest: str) -> Path:
    target = inbox / filename
    if not target.exists():
        return target
    stem = target.stem
    target = inbox / f"{stem}-{digest[:12]}.md"
    if target.exists():
        raise KnowledgeIngestionError(
            f"Unable to resolve filename collision safely for {target.name}."
        )
    return target


def _write_text_atomic(path: Path, content: str) -> None:
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
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
