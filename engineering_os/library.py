"""Governed knowledge-library reads shared by the local web application."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import KnowledgeIndexError, discover_markdown, load_index
from engineering_os.llm import get_embedding_contract


class KnowledgeLibraryError(RuntimeError):
    """Raised when a governed document cannot be listed or inspected safely."""


@dataclass(frozen=True)
class LibraryDocument:
    path: str
    name: str
    folder: str
    status: str
    chunk_count: int
    size_bytes: int


def list_knowledge_documents(
    paths: ProjectPaths,
    *,
    query: str = "",
    folder: str = "",
) -> dict[str, Any]:
    """List governed Markdown documents with truthful current index state."""
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    knowledge_root = paths.resolve(knowledge.get("root", "knowledge")).resolve()
    if not knowledge_root.is_dir():
        raise KnowledgeLibraryError("Configured knowledge root is unavailable.")

    indexed_counts: dict[str, int] = {}
    index_error: str | None = None
    try:
        runtime_config = load_runtime_config(paths)
        chunks = load_index(
            paths.resolve(knowledge.get("index", "runtime/index/knowledge.json")),
            embedding_contract=get_embedding_contract(runtime_config),
        )
        for chunk in chunks:
            normalized = _normalize_index_path(chunk.path, knowledge_root, paths.root)
            indexed_counts[normalized] = indexed_counts.get(normalized, 0) + 1
    except (KnowledgeIndexError, OSError, ValueError):
        index_error = "Knowledge index is unavailable or incompatible."

    query_value = query.strip().casefold()
    folder_value = folder.strip().strip("/")
    all_documents: list[LibraryDocument] = []
    folders: set[str] = set()
    for document in discover_markdown(knowledge_root):
        if document.is_symlink():
            continue
        relative = document.relative_to(paths.root.resolve()).as_posix()
        relative_folder = document.parent.relative_to(knowledge_root).as_posix()
        if relative_folder == ".":
            relative_folder = "root"
        folders.add(relative_folder)
        count = indexed_counts.get(relative, 0)
        all_documents.append(
            LibraryDocument(
                relative,
                document.name,
                relative_folder,
                "indexed" if count else "saved_only",
                count,
                document.stat().st_size,
            )
        )

    documents = [
        item
        for item in all_documents
        if (not folder_value or item.folder == folder_value)
        and (not query_value or query_value in f"{item.name} {item.folder}".casefold())
    ]
    indexed_documents = sum(item.status == "indexed" for item in all_documents)
    return {
        "documents": [asdict(item) for item in documents],
        "folders": sorted(folders),
        "summary": {
            "documents": len(all_documents),
            "indexed": indexed_documents,
            "needs_attention": len(all_documents) - indexed_documents,
        },
        "index_error": index_error,
    }


def resolve_knowledge_document(paths: ProjectPaths, value: str) -> Path:
    """Resolve one Markdown path under the configured knowledge root."""
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeLibraryError("A knowledge document path is required.")
    raw_path = value.split("#", 1)[0].strip()
    raw_candidate = Path(raw_path)
    if ".." in raw_candidate.parts:
        raise KnowledgeLibraryError("Document path must be inside the knowledge root.")
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    knowledge_root = paths.resolve(knowledge.get("root", "knowledge")).resolve()
    project_candidate = paths.resolve(raw_candidate)
    if project_candidate.resolve(strict=False).is_relative_to(knowledge_root):
        candidate = project_candidate.absolute()
    else:
        candidate = (knowledge_root / raw_candidate).absolute()
    try:
        relative = candidate.relative_to(knowledge_root)
    except ValueError as error:
        raise KnowledgeLibraryError("Document path must be inside the knowledge root.") from error
    current = knowledge_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise KnowledgeLibraryError("Document path must name a governed Markdown file.")
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(knowledge_root):
        raise KnowledgeLibraryError("Document path must be inside the knowledge root.")
    if resolved.suffix.lower() != ".md" or not resolved.is_file():
        raise KnowledgeLibraryError("Document path must name a governed Markdown file.")
    return resolved


def read_knowledge_document(paths: ProjectPaths, value: str) -> dict[str, Any]:
    """Return bounded UTF-8 source content for explicit user inspection."""
    document = resolve_knowledge_document(paths, value)
    settings = load_settings(paths)
    ingestion = settings.get("knowledge", {}).get("ingestion", {})
    maximum = ingestion.get("maxBytes", 2 * 1024 * 1024)
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
        raise KnowledgeLibraryError("Knowledge document size policy is invalid.")
    if document.stat().st_size > maximum:
        raise KnowledgeLibraryError("Knowledge document exceeds the inspection size limit.")
    try:
        content = document.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise KnowledgeLibraryError("Knowledge document must be valid UTF-8 Markdown.") from error
    return {
        "path": document.relative_to(paths.root.resolve()).as_posix(),
        "name": document.name,
        "content": content,
    }


def _normalize_index_path(value: str, knowledge_root: Path, project_root: Path) -> str:
    candidate = Path(value)
    if candidate.parts and candidate.parts[0] == knowledge_root.name:
        return candidate.as_posix()
    return (knowledge_root / candidate).relative_to(project_root.resolve()).as_posix()
