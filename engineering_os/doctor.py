from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from engineering_os.structure import validate_structure


def run_doctor(
    project_root: Path,
    structure: dict[str, Any],
    template_config: dict[str, Any],
) -> int:
    failed = 0

    print("")
    print("=======================================")
    print(" Engineering OS Doctor")
    print("=======================================")
    print("")

    print("System")
    print("------")
    for command in ("python", "git"):
        if shutil.which(command):
            print(f"[ OK ] {command}")
        else:
            print(f"[FAIL] {command}")
            failed += 1

    if shutil.which("ollama"):
        print("[ OK ] Ollama")
    else:
        print("[WARN] Ollama not installed")

    print("")
    print("Project Structure")
    print("-----------------")

    result = validate_structure(project_root, structure, template_config)

    for folder in result.missing_folders:
        print(f"[FAIL] Missing folder   : {folder.as_posix()}")
    for file_path in result.missing_files:
        print(f"[FAIL] Missing file     : {file_path.as_posix()}")
    for template in result.missing_templates:
        print(f"[FAIL] Missing template : {template.as_posix()}")
    for template_id in result.unknown_templates:
        print(f"[FAIL] Unknown template : {template_id}")

    failed += result.error_count

    print("")
    if failed == 0:
        print("Doctor completed successfully.")
        return 0

    print(f"Doctor found {failed} problem(s).")
    return 1
