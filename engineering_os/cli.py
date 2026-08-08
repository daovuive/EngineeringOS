from __future__ import annotations

import argparse
from pathlib import Path

from engineering_os import __version__
from engineering_os.config import (
    DEFAULT_STRUCTURE_CONFIG,
    DEFAULT_TEMPLATE_CONFIG,
    ProjectPaths,
    load_project_structure,
    load_runtime_config,
    load_settings,
    load_template_config,
)
from engineering_os.doctor import run_doctor
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
        choices=("settings", "runtime", "structure", "templates"),
        default="settings",
        help="Configuration section to display.",
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
    }
    print(json.dumps(loaders[name](paths), indent=2))
    return 0


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
            )
        if command == "config":
            return command_config(paths, args.name)
        if command == "version":
            banner()
            return 0

        parser.print_help()
        return 0
    except Exception as error:
        print(f"[FAIL] {error}")
        return 1
