from __future__ import annotations

import hashlib
import json
from contextlib import redirect_stdout
from dataclasses import asdict, dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Callable

from engineering_os import __version__
from engineering_os.config import (
    ProjectPaths,
    load_project_structure,
    load_runtime_config,
    load_settings,
    load_skills_config,
    load_template_config,
)
from engineering_os.doctor import run_doctor
from engineering_os.knowledge import (
    discover_markdown,
    load_index,
    rebuild_index,
    search_index,
    select_retrieval_chunks,
)
from engineering_os.knowledge_organizer import (
    apply_markdown_organization,
    load_destinations,
    organize_markdown,
    preview_markdown_organization,
)
from engineering_os.llm import (
    build_pull_commands,
    create_runtime,
    get_default_runtime_definition,
    get_embedding_contract,
)
from engineering_os.query import query_knowledge
from engineering_os.rag import render_response
from engineering_os.structure import ensure_structure, validate_structure


class ActionError(RuntimeError):
    """Raised when an explicit web action request is invalid or cannot run."""


@dataclass(frozen=True)
class ActionDefinition:
    id: str
    description: str
    fields: tuple[str, ...]
    long_running: bool = False
    mutating: bool = False


ACTION_CATALOG = (
    ActionDefinition("project.version", "Show the EngineeringOS version.", ()),
    ActionDefinition("project.validate", "Validate governed project structure.", ()),
    ActionDefinition("project.doctor", "Check project and local runtime health.", (), True),
    ActionDefinition("project.preview", "Preview missing governed structure.", ("operation",)),
    ActionDefinition("project.init", "Create missing governed structure.", ("confirmed", "preview_token"), False, True),
    ActionDefinition("project.sync", "Synchronize missing governed structure.", ("confirmed", "preview_token"), False, True),
    ActionDefinition("config.show", "Show one configuration section.", ("name",)),
    ActionDefinition("llm.status", "Show configured and available local models.", (), True),
    ActionDefinition("llm.pull-plan", "Show model pull commands without executing them.", ()),
    ActionDefinition("llm.chat", "Send one prompt to a configured model role.", ("prompt", "role"), True),
    ActionDefinition("llm.embed", "Create an embedding vector preview.", ("text",), True),
    ActionDefinition("knowledge.index-preview", "Preview a complete knowledge-index rebuild.", ()),
    ActionDefinition("knowledge.index-status", "Inspect the current knowledge index.", ()),
    ActionDefinition("knowledge.index", "Rebuild the complete JSON knowledge index.", ("confirmed", "preview_token"), True, True),
    ActionDefinition("knowledge.search", "Search indexed knowledge.", ("query", "limit", "include_memory"), True),
    ActionDefinition(
        "knowledge.ask",
        "Ask a grounded RAG question with retrieval controls.",
        ("query", "limit", "min_score", "confidence_threshold", "include_memory"),
        True,
    ),
    ActionDefinition(
        "knowledge.organize",
        "Classify an imported inbox document into an existing knowledge category.",
        ("document_path", "dry_run", "move", "confirmed"),
        True,
        True,
    ),
    ActionDefinition(
        "knowledge.organize-preview",
        "Preview an LLM-suggested or user-selected approved destination.",
        ("document_path", "destination"),
        True,
    ),
    ActionDefinition(
        "knowledge.organize-apply",
        "Apply an unchanged, previewed knowledge organization operation.",
        (
            "document_path",
            "destination",
            "source_sha256",
            "preview_token",
            "reason",
            "move",
            "confirmed",
        ),
        False,
        True,
    ),
)


def action_catalog() -> list[dict[str, Any]]:
    return [asdict(action) for action in ACTION_CATALOG]


def execute_action(paths: ProjectPaths, action_id: str, values: dict[str, Any]) -> dict[str, Any]:
    definition = next((item for item in ACTION_CATALOG if item.id == action_id), None)
    if definition is None:
        raise ActionError("Unknown EOS action.")
    if not isinstance(values, dict) or not set(values).issubset(definition.fields):
        raise ActionError("Action request contains unsupported fields.")

    if action_id == "project.version":
        _require_fields(values)
        return {"version": __version__}
    if action_id == "project.validate":
        _require_fields(values)
        result = validate_structure(
            paths.root,
            load_project_structure(paths),
            load_template_config(paths),
        )
        return {
            "ok": result.ok,
            "error_count": result.error_count,
            "missing_folders": [path.as_posix() for path in result.missing_folders],
            "missing_files": [path.as_posix() for path in result.missing_files],
            "missing_templates": [path.as_posix() for path in result.missing_templates],
            "unknown_templates": result.unknown_templates,
            "governance_errors": result.governance_errors,
        }
    if action_id == "project.doctor":
        _require_fields(values)
        output = StringIO()
        with redirect_stdout(output):
            exit_code = run_doctor(
                paths.root,
                load_project_structure(paths),
                load_template_config(paths),
                load_runtime_config(paths),
            )
        return {"ok": exit_code == 0, "report": output.getvalue().strip()}
    if action_id == "project.preview":
        operation = _enum(values, "operation", ("init", "sync"))
        return _project_preview(paths, operation)
    if action_id in {"project.init", "project.sync"}:
        _require_confirmation(values)
        operation = action_id.removeprefix("project.")
        preview = _project_preview(paths, operation)
        if _text(values, "preview_token", maximum=128) != preview["preview_token"]:
            raise ActionError("Project preview is stale; preview changes again.")
        if preview["blocked"]:
            raise ActionError(
                "Project preview is blocked by unresolved governance or template errors."
            )
        ensure_structure(
            paths.root,
            load_project_structure(paths),
            load_template_config(paths),
            verbose=False,
        )
        return {
            "ok": True,
            "outcome": "missing governed content synchronized",
            "created_count": preview["change_count"],
        }
    if action_id == "config.show":
        name = _enum(values, "name", ("settings", "runtime", "structure", "templates", "skills"))
        loaders: dict[str, Callable[[ProjectPaths], dict[str, Any]]] = {
            "settings": load_settings,
            "runtime": load_runtime_config,
            "structure": load_project_structure,
            "templates": load_template_config,
            "skills": load_skills_config,
        }
        return {"name": name, "config": loaders[name](paths)}

    runtime_config = load_runtime_config(paths)
    if action_id == "llm.pull-plan":
        _require_fields(values)
        return {"commands": build_pull_commands(runtime_config)}
    if action_id == "llm.status":
        _require_fields(values)
        runtime = create_runtime(runtime_config)
        definition = get_default_runtime_definition(runtime_config)
        return {
            "provider": definition.provider.id,
            "endpoint": definition.provider.host,
            "configured_models": {
                role: binding.model for role, binding in definition.models.items()
            },
            "available_models": runtime.list_models(),
        }
    if action_id == "llm.chat":
        runtime = create_runtime(runtime_config)
        prompt = _text(values, "prompt", maximum=12_000)
        role = _enum(values, "role", ("rag", "chat", "reasoning", "coding"), default="chat")
        return {"role": role, "response": runtime.generate(prompt, role=role)}
    if action_id == "llm.embed":
        runtime = create_runtime(runtime_config)
        text = _text(values, "text", maximum=12_000)
        vector = runtime.embed(text)
        return {"dimensions": len(vector), "preview": vector[:8]}

    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    index_path = paths.resolve(knowledge.get("index", "runtime/index/knowledge.json"))
    contract = get_embedding_contract(runtime_config)
    if action_id == "knowledge.index-preview":
        _require_fields(values)
        return _index_preview(paths, knowledge, contract)
    if action_id == "knowledge.index-status":
        _require_fields(values)
        try:
            chunks = load_index(index_path, embedding_contract=contract)
        except (OSError, RuntimeError):
            return {
                "available": False,
                "index_path": index_path.relative_to(paths.root).as_posix(),
                "chunk_count": 0,
                "document_count": 0,
            }
        return {
            "available": True,
            "index_path": index_path.relative_to(paths.root).as_posix(),
            "chunk_count": len(chunks),
            "document_count": len({chunk.path for chunk in chunks}),
        }
    if action_id == "knowledge.index":
        _require_confirmation(values)
        preview = _index_preview(paths, knowledge, contract)
        if _text(values, "preview_token", maximum=128) != preview["preview_token"]:
            raise ActionError("Index preview is stale; preview the rebuild again.")
        root = paths.resolve(knowledge.get("root", "knowledge"))
        memory = settings.get("memory", {})
        memory_root = paths.resolve(memory.get("directory", "memory"))
        sources: list[tuple[Path, str, Path | None]] = [(root, "knowledge", None)]
        if memory_root != root:
            sources.append((memory_root, "memory", paths.root))
        runtime = create_runtime(runtime_config)
        chunks = rebuild_index(index_path, sources, runtime, embedding_contract=contract)
        return {"ok": True, "chunk_count": len(chunks), "index_path": index_path.as_posix()}
    if action_id == "knowledge.search":
        runtime = create_runtime(runtime_config)
        query = _text(values, "query", maximum=4_000)
        limit = _integer(values, "limit", default=5, minimum=1, maximum=20)
        include_memory = _boolean(values, "include_memory", default=False)
        chunks = select_retrieval_chunks(
            load_index(index_path, embedding_contract=contract),
            include_memory=include_memory,
            memory_max_age_days=settings.get("memory", {}).get("retrieval", {}).get("maxAgeDays", 90),
        )
        return {
            "results": [
                {
                    "score": round(score, 4),
                    "source": f"{chunk.path}#{chunk.heading}",
                    "preview": chunk.text.splitlines()[0][:160],
                }
                for score, chunk in search_index(chunks, query, runtime, limit=limit)
            ]
        }
    if action_id == "knowledge.ask":
        query = _text(values, "query", maximum=4_000)
        min_score = _optional_number(values, "min_score")
        confidence_threshold = _optional_number(values, "confidence_threshold")
        for label, value in (
            ("min_score", min_score),
            ("confidence_threshold", confidence_threshold),
        ):
            if value is not None and not 0 <= value <= 1:
                raise ActionError(f"{label} must be between 0 and 1.")
        response = query_knowledge(
            paths,
            query,
            limit=_integer(values, "limit", default=3, minimum=1, maximum=10),
            min_score=min_score,
            confidence_threshold=confidence_threshold,
            include_memory=_boolean(values, "include_memory", default=False),
        )
        return {
            "answer": render_response(response),
            "sources": list(response.sources),
        }
    if action_id == "knowledge.organize":
        runtime = create_runtime(runtime_config)
        document = _inbox_document(paths, _text(values, "document_path", maximum=500))
        move = _boolean(values, "move", default=False)
        dry_run = _boolean(values, "dry_run", default=True)
        if not dry_run:
            _require_confirmation(values)
        result = organize_markdown(
            document,
            paths.root,
            runtime,
            load_destinations(knowledge),
            move=move,
            dry_run=dry_run,
        )
        return {
            "action": result.action,
            "destination": result.destination.relative_to(paths.root).as_posix(),
            "reason": result.reason,
        }
    if action_id == "knowledge.organize-preview":
        document = _inbox_document(paths, _text(values, "document_path", maximum=500))
        preview = preview_markdown_organization(
            document,
            paths.root,
            create_runtime(runtime_config),
            load_destinations(knowledge),
            destination_path=_optional_text(values, "destination", maximum=500),
        )
        return {
            "document_path": preview.source.relative_to(paths.root).as_posix(),
            "destination": preview.destination.parent.relative_to(paths.root).as_posix(),
            "filename": preview.destination.name,
            "reason": preview.reason,
            "source_sha256": preview.source_sha256,
            "preview_token": preview.preview_token,
            "collision": preview.collision,
            "allowed_destinations": list(preview.allowed_destinations),
            "index_effect": "Rebuild the index after applying to refresh citation paths.",
        }
    if action_id == "knowledge.organize-apply":
        _require_confirmation(values)
        document = _inbox_document(paths, _text(values, "document_path", maximum=500))
        result = apply_markdown_organization(
            document,
            paths.root,
            load_destinations(knowledge),
            destination_path=_text(values, "destination", maximum=500),
            source_sha256=_text(values, "source_sha256", maximum=64),
            preview_token=_text(values, "preview_token", maximum=64),
            reason=_text(values, "reason", maximum=400),
            move=_boolean(values, "move", default=False),
        )
        return {
            "action": result.action,
            "destination": result.destination.relative_to(paths.root).as_posix(),
            "reason": result.reason,
            "indexing_state": "rebuild_required",
        }
    raise ActionError("EOS action is not implemented.")


def _require_fields(values: dict[str, Any]) -> None:
    if values:
        raise ActionError("This action accepts no fields.")


def _require_confirmation(values: dict[str, Any]) -> None:
    if values.get("confirmed") is not True:
        raise ActionError("This mutation requires confirmed=true.")


def _text(values: dict[str, Any], key: str, *, maximum: int) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ActionError(f"{key} must be non-empty text up to {maximum} characters.")
    return value.strip()


def _enum(
    values: dict[str, Any], key: str, choices: tuple[str, ...], *, default: str | None = None
) -> str:
    value = values.get(key, default)
    if value not in choices:
        raise ActionError(f"{key} must be one of: {', '.join(choices)}.")
    return value


def _integer(
    values: dict[str, Any], key: str, *, default: int, minimum: int, maximum: int
) -> int:
    value = values.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise ActionError(f"{key} must be an integer from {minimum} to {maximum}.")
    return value


def _boolean(values: dict[str, Any], key: str, *, default: bool) -> bool:
    value = values.get(key, default)
    if not isinstance(value, bool):
        raise ActionError(f"{key} must be a boolean.")
    return value


def _optional_number(values: dict[str, Any], key: str) -> float | None:
    value = values.get(key)
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ActionError(f"{key} must be a number.")
    return float(value)


def _optional_text(values: dict[str, Any], key: str, *, maximum: int) -> str | None:
    value = values.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ActionError(f"{key} must be non-empty text up to {maximum} characters.")
    return value.strip()


def _project_preview(paths: ProjectPaths, operation: str) -> dict[str, Any]:
    result = validate_structure(
        paths.root,
        load_project_structure(paths),
        load_template_config(paths),
    )
    folders = [path.as_posix() for path in result.missing_folders]
    files = [path.as_posix() for path in result.missing_files]
    plan = {"operation": operation, "folders": folders, "files": files}
    token = hashlib.sha256(
        json.dumps(plan, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        **plan,
        "preview_token": token,
        "folder_count": len(folders),
        "file_count": len(files),
        "change_count": len(folders) + len(files),
        "blocked": bool(
            result.missing_templates
            or result.unknown_templates
            or result.governance_errors
        ),
        "governance_errors": result.governance_errors,
    }


def _index_preview(
    paths: ProjectPaths,
    knowledge: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    root = paths.resolve(knowledge.get("root", "knowledge"))
    settings = load_settings(paths)
    memory = settings.get("memory", {})
    memory_root = paths.resolve(memory.get("directory", "memory"))
    source_roots = [(root, "knowledge")]
    if memory_root != root and memory_root.is_dir():
        source_roots.append((memory_root, "memory"))
    documents = []
    for source_root, source_type in source_roots:
        documents.extend(
            {
                "path": path.relative_to(paths.root).as_posix(),
                "source_type": source_type,
                "size": path.stat().st_size,
                "modified_ns": path.stat().st_mtime_ns,
            }
            for path in discover_markdown(source_root)
            if not path.is_symlink()
        )
    documents.sort(key=lambda item: item["path"])
    plan = {"documents": documents, "embedding": contract}
    token = hashlib.sha256(
        json.dumps(plan, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "preview_token": token,
        "document_count": len(documents),
        "documents": [item["path"] for item in documents],
        "effect": "Replace the complete compatible JSON index after all embeddings succeed.",
    }


def _inbox_document(paths: ProjectPaths, value: str) -> Path:
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    ingestion = knowledge.get("ingestion", {}) if isinstance(knowledge, dict) else {}
    inbox = paths.resolve(ingestion.get("directory", "knowledge/inbox")).resolve()
    candidate = paths.resolve(value).resolve()
    try:
        candidate.relative_to(inbox)
    except ValueError as error:
        raise ActionError("Document path must be inside the ingestion directory.") from error
    if candidate.suffix.lower() != ".md" or not candidate.is_file() or candidate.is_symlink():
        raise ActionError("Document path must name an imported Markdown file.")
    return candidate
