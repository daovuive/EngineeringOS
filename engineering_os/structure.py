from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engineering_os.templates import resolve_template_source


@dataclass
class ValidationResult:
    missing_folders: list[Path] = field(default_factory=list)
    missing_files: list[Path] = field(default_factory=list)
    missing_templates: list[Path] = field(default_factory=list)
    unknown_templates: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (
            self.missing_folders
            or self.missing_files
            or self.missing_templates
            or self.unknown_templates
        )

    @property
    def error_count(self) -> int:
        return (
            len(self.missing_folders)
            + len(self.missing_files)
            + len(self.missing_templates)
            + len(self.unknown_templates)
        )


def ensure_structure(
    project_root: Path,
    structure: dict[str, Any],
    template_config: dict[str, Any],
    *,
    verbose: bool = True,
) -> None:
    for folder in structure.get("folders", []):
        path = project_root / folder["path"]
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            if verbose:
                print(f"[CREATE] Folder : {folder['path']}")
        elif verbose:
            print(f"[ OK ]    Folder : {folder['path']}")

    for file_entry in structure.get("files", []):
        relative_path = file_entry["path"]
        target = project_root / relative_path

        if target.exists():
            if verbose:
                print(f"[ OK ]    File   : {relative_path}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        source = resolve_template_source(
            project_root,
            template_config,
            file_entry["template"],
        )

        if source is None:
            target.touch()
        else:
            if not source.exists():
                raise FileNotFoundError(f"Template not found: {source}")
            shutil.copyfile(source, target)

        if verbose:
            print(f"[CREATE] File   : {relative_path}")


def validate_structure(
    project_root: Path,
    structure: dict[str, Any],
    template_config: dict[str, Any],
) -> ValidationResult:
    result = ValidationResult()

    for folder in structure.get("folders", []):
        path = project_root / folder["path"]
        if not path.exists():
            result.missing_folders.append(Path(folder["path"]))

    for file_entry in structure.get("files", []):
        path = project_root / file_entry["path"]
        if not path.exists():
            result.missing_files.append(Path(file_entry["path"]))

        try:
            source = resolve_template_source(
                project_root,
                template_config,
                file_entry["template"],
            )
        except ValueError:
            result.unknown_templates.append(file_entry["template"])
            continue

        if source is not None and not source.exists():
            result.missing_templates.append(source.relative_to(project_root))

    return result
