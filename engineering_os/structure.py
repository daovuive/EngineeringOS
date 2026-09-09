from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import unquote, urlsplit

from engineering_os.templates import resolve_template_source


@dataclass
class ValidationResult:
    missing_folders: list[Path] = field(default_factory=list)
    missing_files: list[Path] = field(default_factory=list)
    missing_templates: list[Path] = field(default_factory=list)
    unknown_templates: list[str] = field(default_factory=list)
    governance_errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (
            self.missing_folders
            or self.missing_files
            or self.missing_templates
            or self.unknown_templates
            or self.governance_errors
        )

    @property
    def error_count(self) -> int:
        return (
            len(self.missing_folders)
            + len(self.missing_files)
            + len(self.missing_templates)
            + len(self.unknown_templates)
            + len(self.governance_errors)
        )


def ensure_structure(
    project_root: Path,
    structure: dict[str, Any],
    template_config: dict[str, Any],
    *,
    verbose: bool = True,
) -> None:
    if structure.get("governance") is not None:
        # Check the complete write plan before creating any directories/files.
        protected = structure["governance"].get("protectedRootReadme")
        if protected is not None and not (project_root / "README.md").is_file():
            raise ValueError("Protected README.md is missing; restore the approved file instead of generating it from a template")
        seen = set()
        for section in ("folders", "files"):
            for entry in structure.get(section, []):
                relative = _relative_path(project_root, entry["path"])
                key = relative.as_posix().casefold()
                if key in seen:
                    raise ValueError(f"Duplicate manifest path: {relative.as_posix()}")
                seen.add(key)

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

    if structure.get("governance") is not None:
        result.governance_errors.extend(_validate_governance(project_root, structure))

    return result


def _relative_path(project_root: Path, value: Any) -> Path:
    """Accept only canonical relative paths that resolve inside the project."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Invalid project path: {value!r}")
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if (
        PurePosixPath(normalized).is_absolute()
        or PureWindowsPath(value).drive
        or any(part in ("", ".", "..") or ":" in part for part in parts)
    ):
        raise ValueError(f"Project path must be canonical and relative: {value!r}")
    path = Path(*parts)
    if not (project_root / path).resolve().is_relative_to(project_root.resolve()):
        raise ValueError(f"Project path escapes the project: {value!r}")
    return path


def _markdown_targets(markdown: str) -> list[str]:
    """Read inline links and reference definitions, excluding fenced examples.

    This intentionally is a small Markdown link reader, not a CommonMark parser.
    HTML links and heading-anchor existence are outside this check's scope.
    """
    lines = []
    fence: str | None = None
    fence_length = 0
    for line in markdown.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            run = marker.group(1)
            if fence is None:
                fence, fence_length = run[0], len(run)
            elif run[0] == fence and len(run) >= fence_length:
                fence = None
            continue
        if fence is None:
            lines.append(line)
    content = "\n".join(lines)
    # Code spans are examples too; retain newlines for reference definitions.
    content = re.sub(r"(`+)([^`\n]*?)\1", "", content)
    starts = [match.end() for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*", content)]
    starts.extend(match.end() for match in re.finditer(r"^\s{0,3}\[[^\]\n]+\]:\s*", content, re.M))
    targets = []
    for start in starts:
        if start >= len(content):
            continue
        if content[start] == "<":
            end = content.find(">", start + 1)
            if end >= 0:
                targets.append(content[start + 1 : end])
            continue
        end, depth = start, 0
        while end < len(content):
            char = content[end]
            if char == "\\" and end + 1 < len(content):
                end += 2
                continue
            if char.isspace() or (char == ")" and depth == 0):
                break
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            end += 1
        if end > start:
            targets.append(re.sub(r"\\([() ])", r"\1", content[start:end]))
    return targets


def _readme_links(project_root: Path, readme: Path, errors: list[str]) -> set[Path]:
    label = readme.relative_to(project_root).as_posix()
    try:
        content = readme.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        errors.append(f"Cannot read {label}: {error}")
        return set()
    if not content.strip():
        errors.append(f"Empty architecture README: {label}")
    links = set()
    for target in _markdown_targets(content):
        if PureWindowsPath(target).drive:
            errors.append(f"README link must use a relative project path in {label}: {target}")
            continue
        try:
            parsed = urlsplit(target)
        except ValueError:
            errors.append(f"Invalid README link in {label}: {target}")
            continue
        if parsed.scheme.lower() == "file":
            errors.append(f"README link must use a relative project path in {label}: {target}")
            continue
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        local = unquote(parsed.path).replace("\\", "/")
        resolved = (readme.parent / local).resolve()
        if not resolved.is_relative_to(project_root):
            errors.append(f"README link escapes project in {label}: {target}")
        elif not resolved.exists():
            errors.append(f"Broken README link in {label}: {target}")
        else:
            links.add(resolved)
    return links


def _validate_governance(project_root: Path, structure: dict[str, Any]) -> list[str]:
    project_root = project_root.resolve()
    governance = structure["governance"]
    errors: list[str] = []
    if not isinstance(governance, dict):
        return ["governance must be an object"]

    folders: set[Path] = set()
    seen: set[str] = set()
    for section in ("folders", "files"):
        for entry in structure.get(section, []):
            try:
                relative = _relative_path(project_root, entry["path"])
            except ValueError as error:
                errors.append(str(error))
                continue
            key = relative.as_posix().casefold()
            if key in seen:
                errors.append(f"Duplicate manifest path: {relative.as_posix()}")
            seen.add(key)
            if section == "folders":
                folders.add(relative)
                if (project_root / relative).exists() and not (project_root / relative).is_dir():
                    errors.append(f"Declared folder is not a directory: {relative.as_posix()}")
            else:
                if relative.parent != Path(".") and relative.parent not in folders:
                    errors.append(f"File parent is not a declared folder: {relative.as_posix()}")
                if (project_root / relative).exists() and not (project_root / relative).is_file():
                    errors.append(f"Declared file is not a file: {relative.as_posix()}")

    for folder in sorted(folders):
        if folder.parent != Path(".") and folder.parent not in folders:
            errors.append(f"Folder parent is not declared: {folder.as_posix()}")

    readme_name = governance.get("readmeName", "README.md")
    if readme_name != "README.md":
        errors.append("governance.readmeName must be README.md")
        readme_name = "README.md"
    readmes = {Path(readme_name)} | {folder / readme_name for folder in folders}
    links_by_readme: dict[Path, set[Path]] = {}
    for relative in sorted(readmes):
        readme = project_root / relative
        if not readme.resolve().is_relative_to(project_root):
            errors.append(f"Architecture README escapes project: {relative.as_posix()}")
            continue
        if not readme.is_file():
            errors.append(f"Missing architecture README: {relative.as_posix()}")
            continue
        links_by_readme[relative] = _readme_links(project_root, readme, errors)
    protected = governance.get("protectedRootReadme")
    if isinstance(protected, dict):
        if protected.get("path") != readme_name:
            errors.append("protectedRootReadme.path must be README.md")
        expected = protected.get("sha256", "")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
            errors.append("protectedRootReadme.sha256 must contain a SHA-256 digest")
        elif (project_root / readme_name).is_file() and (project_root / readme_name).resolve().is_relative_to(project_root):
            actual = hashlib.sha256((project_root / readme_name).read_bytes()).hexdigest()
            if actual != expected.lower():
                errors.append("Protected README.md changed; explicit user approval is required before updating its SHA-256 baseline")
    elif protected is not None:
        errors.append("protectedRootReadme must be an object")

    ignored = set()
    for value in governance.get("ignoredDirectories", []):
        try:
            ignored.add(_relative_path(project_root, value))
        except ValueError as error:
            errors.append(str(error))
    populated: set[Path] = set()
    for current, directories, filenames in os.walk(project_root, followlinks=False):
        relative = Path(current).relative_to(project_root)
        kept = []
        for name in directories:
            child = relative / name
            if child in ignored or name == "__pycache__":
                continue
            if (project_root / child).is_symlink():
                errors.append(f"Uninspected directory symlink: {child.as_posix()}")
                continue
            kept.append(name)
        directories[:] = kept
        if filenames:
            populated.add(relative)
            populated.update(relative.parents)
    for relative in sorted(populated - folders - {Path(".")}):
        errors.append(f"Unregistered directory: {relative.as_posix()}")

    if "allowedRootFiles" in governance:
        allowed = set()
        for value in governance["allowedRootFiles"]:
            try:
                relative = _relative_path(project_root, value)
                if relative.parent != Path("."):
                    raise ValueError(f"allowedRootFiles must list filenames only: {value!r}")
                allowed.add(relative.name)
            except ValueError as error:
                errors.append(str(error))
        for child in sorted(project_root.iterdir()):
            if child.is_file() and child.name not in allowed:
                errors.append(f"Unexpected root file: {child.name}")

    registry = project_root / "configs/skills.json"
    if not registry.resolve().is_relative_to(project_root):
        errors.append("Skills registry escapes project: configs/skills.json")
        return errors
    if registry.is_file():
        try:
            skills = json.loads(registry.read_text(encoding="utf-8-sig"))["skills"]
            ids = set()
            for skill in skills:
                skill_id = skill["id"]
                if not isinstance(skill_id, str) or not skill_id.strip():
                    raise ValueError("Skill id must be a nonempty string")
                if skill_id in ids:
                    errors.append(f"Duplicate skill id: {skill_id}")
                ids.add(skill_id)
                relative = _relative_path(project_root, skill["path"])
                if not (project_root / relative).is_file():
                    errors.append(f"Missing registered skill: {relative.as_posix()}")
                if relative.parent not in folders:
                    errors.append(f"Skill parent is not a declared folder: {relative.as_posix()}")
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
            errors.append(f"Invalid skills registry: {error}")
    return errors
