from __future__ import annotations

from pathlib import Path
from typing import Any


def find_template(template_config: dict[str, Any], template_id: str) -> dict[str, Any] | None:
    for item in template_config.get("templates", []):
        if item.get("id") == template_id:
            return item
    return None


def template_root(project_root: Path, template_config: dict[str, Any]) -> Path:
    directory = template_config.get("templateDirectory")
    if not directory:
        raise ValueError("Missing templateDirectory in template config")
    return project_root / directory


def resolve_template_source(
    project_root: Path,
    template_config: dict[str, Any],
    template_id: str,
) -> Path | None:
    template = find_template(template_config, template_id)
    if template is None:
        raise ValueError(f"Unknown template: {template_id}")

    source = template.get("source")
    if source is None:
        return None

    return template_root(project_root, template_config) / source
