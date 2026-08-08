from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_STRUCTURE_CONFIG = Path("configs/project-structure.json")
DEFAULT_TEMPLATE_CONFIG = Path("configs/template.json")
DEFAULT_SETTINGS_CONFIG = Path("configs/settings.json")
DEFAULT_RUNTIME_CONFIG = Path("configs/ai-runtime.json")


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    structure_config: Path = DEFAULT_STRUCTURE_CONFIG
    template_config: Path = DEFAULT_TEMPLATE_CONFIG
    settings_config: Path = DEFAULT_SETTINGS_CONFIG
    runtime_config: Path = DEFAULT_RUNTIME_CONFIG

    def resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.root / candidate


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")

    return data


def load_project_structure(paths: ProjectPaths) -> dict[str, Any]:
    return load_json(paths.resolve(paths.structure_config))


def load_template_config(paths: ProjectPaths) -> dict[str, Any]:
    return load_json(paths.resolve(paths.template_config))


def load_settings(paths: ProjectPaths) -> dict[str, Any]:
    return load_json(paths.resolve(paths.settings_config))


def load_runtime_config(paths: ProjectPaths) -> dict[str, Any]:
    return load_json(paths.resolve(paths.runtime_config))
