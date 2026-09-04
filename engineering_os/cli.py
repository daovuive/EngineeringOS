from __future__ import annotations

import argparse
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
    build_index,
    load_index,
    save_index,
    search_index,
)
from engineering_os.llm import (
    LLMError,
    build_pull_commands,
    create_runtime,
    get_default_runtime_definition,
)
from engineering_os.structure import ensure_structure, validate_structure


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
    search_parser = knowledge_subparsers.add_parser(
        "search",
        help="Search indexed knowledge.",
    )
    search_parser.add_argument("query", help="Search query.")
    search_parser.add_argument("--limit", type=int, default=5, help="Maximum results.")

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

    print("")
    print("Validation failed.")
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
        print(f"Runtime : {definition.endpoint.id}")
        print(f"Host    : {definition.endpoint.host}")
        print("")
        print("Configured models")
        print("-----------------")
        for role, model in definition.models.items():
            print(f"{role:10}: {model}")

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
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    root = paths.resolve(knowledge.get("root", "knowledge"))
    index_path = paths.resolve(knowledge.get("index", "runtime/index/knowledge.json"))
    runtime = create_runtime(load_runtime_config(paths))

    if args.knowledge_command == "index":
        chunks = build_index(root, runtime)
        save_index(index_path, chunks)
        print(f"Indexed {len(chunks)} Markdown chunk(s) into {index_path.as_posix()}")
        return 0

    if args.knowledge_command == "search":
        chunks = load_index(index_path)
        for score, chunk in search_index(chunks, args.query, runtime, limit=args.limit):
            print(f"{score:.4f}  {chunk.path}#{chunk.heading}")
            print(f"        {chunk.text.splitlines()[0][:160]}")
        return 0

    raise KnowledgeIndexError("Missing knowledge command. Use: index or search.")


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
        if command == "version":
            banner()
            return 0

        parser.print_help()
        return 0
    except Exception as error:
        print(f"[FAIL] {error}")
        return 1
