from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from engineering_os.llm import LLMError, create_runtime, get_default_runtime_definition
from engineering_os.structure import validate_structure


def run_doctor(
    project_root: Path,
    structure: dict[str, Any],
    template_config: dict[str, Any],
    runtime_config: dict[str, Any] | None = None,
) -> int:
    failed = 0

    print("")
    print("=======================================")
    print(" Engineering OS Doctor")
    print("=======================================")
    print("")

    print("System")
    print("------")
    python_command = sys.executable or shutil.which("python") or shutil.which("python3")
    if python_command:
        print("[ OK ] python")
    else:
        print("[FAIL] python")
        failed += 1

    for command in ("git",):
        if shutil.which(command):
            print(f"[ OK ] {command}")
        else:
            print(f"[FAIL] {command}")
            failed += 1

    if runtime_config is not None:
        print("")
        print("AI Runtime")
        print("----------")
        try:
            definition = get_default_runtime_definition(runtime_config)
            runtime = create_runtime(runtime_config)
            print(f"[ OK ] default runtime : {definition.endpoint.id}")
            print(f"[ OK ] host            : {definition.endpoint.host}")

            ollama_executable = None
            if definition.endpoint.id == "ollama":
                ollama_executable = shutil.which("ollama")
                if not ollama_executable:
                    print("[INFO] Ollama executable not found on PATH")

            try:
                models = runtime.list_models()
                print(f"[ OK ] runtime API     : {len(models)} model(s) available")
                if definition.endpoint.id == "ollama" and not ollama_executable:
                    print("[INFO] Ollama is reachable even though the executable is not on PATH")
            except LLMError as error:
                print(f"[WARN] runtime API     : {error}")
        except LLMError as error:
            print(f"[FAIL] AI runtime      : {error}")
            failed += 1

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
    for error in result.governance_errors:
        print(f"[FAIL] Governance       : {error}")

    failed += result.error_count

    print("")
    if failed == 0:
        print("Doctor completed successfully.")
        return 0

    print(f"Doctor found {failed} problem(s).")
    return 1
