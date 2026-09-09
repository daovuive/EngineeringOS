from __future__ import annotations

import argparse
import sys
from pathlib import Path

from engineering_os import __version__
from engineering_os.config import (
    DEFAULT_STRUCTURE_CONFIG,
    DEFAULT_TEMPLATE_CONFIG,
    load_skills_config,
    ProjectPaths,
    load_project_structure,
    load_runtime_config,
    load_settings,
    load_template_config,
)
from engineering_os.doctor import run_doctor
from engineering_os.knowledge import (
    KnowledgeIndexError,
    load_index,
    rebuild_index,
    search_index,
    select_retrieval_chunks,
)
from engineering_os.knowledge_organizer import (
    KnowledgeOrganizationError,
    load_destinations,
    organize_markdown,
)
from engineering_os.ingestion import ingest_path, ingest_text
from engineering_os.llm import (
    LLMError,
    build_pull_commands,
    create_runtime,
    get_embedding_contract,
    get_default_runtime_definition,
)
from engineering_os.rag import (
    render_response,
)
from engineering_os.query import query_knowledge
from engineering_os.structure import ensure_structure, validate_structure
from engineering_os.workflows import (
    WorkflowDocument,
    read_workflow_document,
    run_workflow,
    workflow_ids,
)


def banner() -> None:
    print("")
    print("===========================================")
    print("           Engineering OS")
    print("===========================================")
    print(f"Version : {__version__}")
    print("")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eng",
        description="Engineering OS CLI",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory.",
    )
    parser.add_argument(
        "--structure-config",
        default=str(DEFAULT_STRUCTURE_CONFIG),
        help="Project structure configuration path.",
    )
    parser.add_argument(
        "--template-config",
        default=str(DEFAULT_TEMPLATE_CONFIG),
        help="Template configuration path.",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init", help="Initialize project.")
    subparsers.add_parser("sync", help="Synchronize project.")
    subparsers.add_parser("validate", help="Validate project.")
    subparsers.add_parser("doctor", help="Check environment.")
    subparsers.add_parser("version", help="Show version.")

    config_parser = subparsers.add_parser("config", help="Show configuration.")
    config_parser.add_argument(
        "name",
        nargs="?",
        choices=("settings", "runtime", "structure", "templates", "skills"),
        default="settings",
        help="Configuration section to display.",
    )

    llm_parser = subparsers.add_parser("llm", help="Use local LLM runtime.")
    llm_subparsers = llm_parser.add_subparsers(dest="llm_command")
    llm_subparsers.add_parser("status", help="Check configured local LLM runtime.")
    llm_subparsers.add_parser("pull-plan", help="Print Ollama model pull commands.")

    chat_parser = llm_subparsers.add_parser(
        "chat",
        help="Send one prompt to the configured local LLM runtime.",
    )
    chat_parser.add_argument("prompt", help="Prompt text.")
    chat_parser.add_argument(
        "--role",
        choices=("rag", "chat", "reasoning", "coding"),
        default="chat",
        help="Configured model role to use.",
    )

    embed_parser = llm_subparsers.add_parser("embed", help="Create an embedding vector.")
    embed_parser.add_argument("text", help="Text to embed.")

    knowledge_parser = subparsers.add_parser(
        "knowledge",
        help="Index and search knowledge.",
    )
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_command")
    knowledge_subparsers.add_parser("index", help="Build the Markdown knowledge index.")
    organize_parser = knowledge_subparsers.add_parser(
        "organize",
        help="Classify one Markdown file with the local LLM and place it in knowledge.",
    )
    organize_parser.add_argument("--file", required=True, help="Markdown file to classify.")
    organize_parser.add_argument(
        "--move",
        action="store_true",
        help="Move the source after placement; the default keeps a copied original.",
    )
    organize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the LLM-selected destination without copying or moving a file.",
    )
    search_parser = knowledge_subparsers.add_parser(
        "search",
        help="Search indexed knowledge.",
    )
    search_parser.add_argument("query", help="Search query.")
    search_parser.add_argument("--limit", type=int, default=5, help="Maximum results.")
    search_parser.add_argument(
        "--include-memory",
        action="store_true",
        help="Include fresh project memory as contextual retrieval results.",
    )
    ask_parser = knowledge_subparsers.add_parser(
        "ask",
        help="Answer a question using retrieved knowledge and the configured RAG model.",
    )
    ask_parser.add_argument("query", help="Question to answer.")
    ask_parser.add_argument("--limit", type=int, default=3, help="Maximum context chunks.")
    ask_parser.add_argument(
        "--min-score",
        type=float,
        default=None,
        help="Override the configured minimum score for a retrieved candidate.",
    )
    ask_parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=None,
        help="Override the configured top-candidate confidence gate.",
    )
    ask_parser.add_argument(
        "--include-memory",
        action="store_true",
        help="Include fresh project memory as contextual RAG input.",
    )

    add_knowledge_parser = subparsers.add_parser(
        "add-knowledge",
        help="Import Markdown or UTF-8 text and index it for RAG by default.",
        description=(
            "Import exactly one Markdown (.md/.markdown), plain-text (.txt), "
            "inline-text, or stdin source into governed knowledge storage. "
            "The saved document is indexed automatically unless --no-index is used."
        ),
    )
    add_knowledge_parser.add_argument(
        "path",
        nargs="?",
        help="Markdown or text file path (short form).",
    )
    add_knowledge_parser.add_argument(
        "--file",
        help="Markdown or text file path.",
    )
    add_knowledge_parser.add_argument("--text", help="Knowledge entered directly as text.")
    add_knowledge_parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read UTF-8 text from standard input.",
    )
    add_knowledge_parser.add_argument(
        "--title",
        help="Optional title used to derive a safe filename for direct text.",
    )
    add_knowledge_parser.add_argument(
        "--auto-index",
        action="store_true",
        help="Explicitly enable indexing (already enabled by default).",
    )
    add_knowledge_parser.add_argument(
        "--no-index",
        action="store_true",
        help="Save the document without updating the RAG index.",
    )

    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Run a bounded engineering or architecture workflow.",
    )
    workflow_subparsers = workflow_parser.add_subparsers(dest="workflow_id")
    for workflow_id in workflow_ids():
        parser_for_workflow = workflow_subparsers.add_parser(
            workflow_id,
            help=f"Run the {workflow_id} workflow.",
        )
        parser_for_workflow.add_argument(
            "--file",
            action="append",
            default=[],
            help="UTF-8 input file, relative to --root unless absolute; repeatable.",
        )
        parser_for_workflow.add_argument(
            "--text",
            action="append",
            default=[],
            help="Inline input text; repeatable.",
        )
        parser_for_workflow.add_argument(
            "--with-knowledge",
            action="store_true",
            help="Retrieve supporting context from the existing knowledge index.",
        )
        parser_for_workflow.add_argument(
            "--knowledge-query",
            help="Explicit retrieval query; defaults to a bounded excerpt of the input.",
        )

    return parser


def make_paths(args: argparse.Namespace) -> ProjectPaths:
    return ProjectPaths(
        root=Path(args.root).resolve(),
        structure_config=Path(args.structure_config),
        template_config=Path(args.template_config),
    )


def command_init(paths: ProjectPaths) -> int:
    banner()
    print("Engineering OS Initialization")
    print("")
    ensure_structure(
        paths.root,
        load_project_structure(paths),
        load_template_config(paths),
    )
    print("")
    print("Initialization completed successfully.")
    return 0


def command_sync(paths: ProjectPaths) -> int:
    banner()
    print("Engineering OS Synchronization")
    print("")
    ensure_structure(
        paths.root,
        load_project_structure(paths),
        load_template_config(paths),
    )
    print("")
    print("Synchronization completed.")
    return 0


def command_validate(paths: ProjectPaths) -> int:
    banner()
    print("Engineering OS Validation")
    print("")

    result = validate_structure(
        paths.root,
        load_project_structure(paths),
        load_template_config(paths),
    )

    if result.ok:
        print("Validation completed successfully.")
        return 0

    for folder in result.missing_folders:
        print(f"[MISS] Folder   : {folder.as_posix()}")
    for file_path in result.missing_files:
        print(f"[MISS] File     : {file_path.as_posix()}")
    for template in result.missing_templates:
        print(f"[MISS] Template : {template.as_posix()}")
    for template_id in result.unknown_templates:
        print(f"[MISS] Template : {template_id}")
    for error in result.governance_errors:
        print(f"[FAIL] Governance: {error}")

    print("")
    print(f"Validation failed: {result.error_count} problem(s).")
    return 1


def command_config(paths: ProjectPaths, name: str) -> int:
    import json

    loaders = {
        "settings": load_settings,
        "runtime": load_runtime_config,
        "structure": load_project_structure,
        "templates": load_template_config,
        "skills": load_skills_config,
    }
    print(json.dumps(loaders[name](paths), indent=2))
    return 0


def command_llm(paths: ProjectPaths, args: argparse.Namespace) -> int:
    runtime_config = load_runtime_config(paths)
    definition = get_default_runtime_definition(runtime_config)
    runtime = create_runtime(runtime_config)

    if args.llm_command == "status":
        print(f"Provider: {definition.provider.id}")
        print(f"Type    : {definition.provider.type}")
        print(f"Endpoint: {definition.provider.host}")
        print("")
        print("Configured models")
        print("-----------------")
        for role, binding in definition.models.items():
            print(f"{role:10}: {binding.model}")

        print("")
        try:
            models = runtime.list_models()
        except LLMError as error:
            print(f"[WARN] {error}")
            return 1

        print("Available runtime models")
        print("------------------------")
        if models:
            for model in models:
                print(model)
        else:
            print("(none)")
        return 0

    if args.llm_command == "pull-plan":
        for command in build_pull_commands(runtime_config):
            print(command)
        return 0

    if args.llm_command == "chat":
        print(runtime.generate(args.prompt, role=args.role))
        return 0

    if args.llm_command == "embed":
        embedding = runtime.embed(args.text)
        print(f"dimensions: {len(embedding)}")
        print(embedding[:8])
        return 0

    raise LLMError("Missing LLM command. Use: status, pull-plan, chat, or embed.")


def command_knowledge(paths: ProjectPaths, args: argparse.Namespace) -> int:
    if args.knowledge_command == "ask":
        response = query_knowledge(
            paths,
            args.query,
            limit=args.limit,
            min_score=args.min_score,
            confidence_threshold=args.confidence_threshold,
            include_memory=args.include_memory,
        )
        print(render_response(response))
        return 0

    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    root = paths.resolve(knowledge.get("root", "knowledge"))
    index_path = paths.resolve(knowledge.get("index", "runtime/index/knowledge.json"))
    memory = settings.get("memory", {})
    memory_root = paths.resolve(memory.get("directory", "memory"))
    memory_retrieval = memory.get("retrieval", {})
    memory_max_age_days = memory_retrieval.get("maxAgeDays", 90)
    if not isinstance(memory_max_age_days, int) or isinstance(memory_max_age_days, bool):
        raise KnowledgeIndexError("memory.retrieval.maxAgeDays must be an integer.")
    runtime_config = load_runtime_config(paths)
    runtime = create_runtime(runtime_config)
    embedding_contract = get_embedding_contract(runtime_config)
    if args.knowledge_command == "organize":
        source = Path(args.file)
        if not source.is_absolute():
            source = paths.root / source
        result = organize_markdown(
            source,
            paths.root,
            runtime,
            load_destinations(knowledge),
            move=args.move,
            dry_run=args.dry_run,
        )
        print(f"Knowledge file {result.action}: {result.destination.as_posix()}")
        print(f"Reason: {result.reason}")
        print("Run `python eng.py knowledge index` to make it searchable.")
        return 0
    if args.knowledge_command == "index":
        sources: list[tuple[Path, str, Path | None]] = [(root, "knowledge", None)]
        if memory_root != root:
            sources.append((memory_root, "memory", paths.root))
        chunks = rebuild_index(
            index_path,
            sources,
            runtime,
            embedding_contract=embedding_contract,
        )
        print(f"Indexed {len(chunks)} Markdown chunk(s) into {index_path.as_posix()}")
        return 0

    if args.knowledge_command == "search":
        chunks = load_index(index_path, embedding_contract=embedding_contract)
        chunks = select_retrieval_chunks(
            chunks,
            include_memory=args.include_memory,
            memory_max_age_days=memory_max_age_days,
        )
        for score, chunk in search_index(chunks, args.query, runtime, limit=args.limit):
            print(f"{score:.4f}  {chunk.path}#{chunk.heading}")
            print(f"        {chunk.text.splitlines()[0][:160]}")
        return 0

    raise KnowledgeIndexError("Missing knowledge command. Use: index, search, ask, or organize.")


def command_workflow(paths: ProjectPaths, args: argparse.Namespace) -> int:
    if not args.workflow_id:
        raise ValueError(
            "Missing workflow. Use: " + ", ".join(workflow_ids()) + "."
        )
    documents: list[WorkflowDocument] = []
    for value in args.file:
        file_path = Path(value)
        if not file_path.is_absolute():
            file_path = paths.root / file_path
        documents.append(read_workflow_document(file_path.resolve()))
    documents.extend(
        WorkflowDocument(f"inline-{number}", value)
        for number, value in enumerate(args.text, 1)
    )
    response = run_workflow(
        paths,
        args.workflow_id,
        documents,
        with_knowledge=args.with_knowledge,
        knowledge_query=args.knowledge_query,
    )
    print(response.result)
    print("")
    print(f"Workflow: {response.workflow}")
    print(f"Knowledge retrieval: {response.retrieval_status}")
    return 0


def command_add_knowledge(paths: ProjectPaths, args: argparse.Namespace) -> int:
    sources = [args.path is not None, args.file is not None, args.text is not None, args.stdin]
    if sum(sources) != 1:
        raise ValueError(
            "Exactly one input source is required: positional file, --file, --text, or --stdin."
        )
    if args.auto_index and args.no_index:
        raise ValueError("--auto-index and --no-index cannot be used together.")
    auto_index = not args.no_index

    if args.text is not None:
        result = ingest_text(paths, args.text, title=args.title, auto_index=auto_index)
    elif args.stdin:
        result = ingest_text(
            paths,
            sys.stdin.read(),
            title=args.title,
            auto_index=auto_index,
        )
    else:
        value = args.file if args.file is not None else args.path
        assert value is not None
        source = Path(value)
        if not source.is_absolute():
            source = paths.root / source
        result = ingest_path(paths, source, title=args.title, auto_index=auto_index)

    print(f"Document: {result.document_path}")
    print(f"Import: {result.import_outcome}")
    print(f"Indexing: {result.indexing_state}")
    if result.chunk_count is not None:
        print(f"Chunks: {result.chunk_count}")
    if result.ready_for_rag:
        print("Ready for RAG: yes")
        return 0
    if result.indexing_state == "skipped":
        print("Ready for RAG: no (indexing intentionally skipped)")
        return 0
    print(f"Saved, indexing failed: {result.error or 'unknown indexing error'}")
    print(f"Retry: python3 eng.py add-knowledge --file {json_quote(result.document_path)} --auto-index")
    return 1


def json_quote(value: str) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "help"
    paths = make_paths(args)

    try:
        if command == "init":
            return command_init(paths)
        if command == "sync":
            return command_sync(paths)
        if command == "validate":
            return command_validate(paths)
        if command == "doctor":
            return run_doctor(
                paths.root,
                load_project_structure(paths),
                load_template_config(paths),
                load_runtime_config(paths),
            )
        if command == "config":
            return command_config(paths, args.name)
        if command == "llm":
            return command_llm(paths, args)
        if command == "knowledge":
            return command_knowledge(paths, args)
        if command == "add-knowledge":
            return command_add_knowledge(paths, args)
        if command == "workflow":
            return command_workflow(paths, args)
        if command == "version":
            banner()
            return 0

        parser.print_help()
        return 0
    except Exception as error:
        print(f"[FAIL] {error}")
        return 1
