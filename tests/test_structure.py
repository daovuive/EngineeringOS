from pathlib import Path

from engineering_os.structure import ensure_structure, validate_structure
from engineering_os.templates import resolve_template_source


def make_project(tmp_path: Path) -> tuple[dict, dict]:
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "README.md").write_text("# Template\n", encoding="utf-8")

    structure = {
        "folders": [
            {"path": "docs", "description": "Project documentation"},
            {"path": "runtime", "description": "Runtime files"},
        ],
        "files": [
            {"path": "README.md", "template": "README"},
            {"path": "docs/EMPTY.md", "template": "EMPTY"},
        ],
    }
    template_config = {
        "templateDirectory": "templates",
        "templates": [
            {"id": "README", "source": "README.md"},
            {"id": "EMPTY", "source": None},
        ],
    }
    return structure, template_config


def test_resolve_template_source(tmp_path: Path) -> None:
    structure, template_config = make_project(tmp_path)

    source = resolve_template_source(tmp_path, template_config, "README")

    assert source == tmp_path / "templates" / "README.md"
    assert structure["files"][0]["template"] == "README"


def test_validate_reports_missing_structure(tmp_path: Path) -> None:
    structure, template_config = make_project(tmp_path)

    result = validate_structure(tmp_path, structure, template_config)

    assert not result.ok
    assert Path("docs") in result.missing_folders
    assert Path("runtime") in result.missing_folders
    assert Path("README.md") in result.missing_files


def test_ensure_structure_creates_folders_and_files(tmp_path: Path) -> None:
    structure, template_config = make_project(tmp_path)

    ensure_structure(tmp_path, structure, template_config, verbose=False)
    result = validate_structure(tmp_path, structure, template_config)

    assert result.ok
    assert (tmp_path / "docs").is_dir()
    assert (tmp_path / "runtime").is_dir()
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# Template\n"
    assert (tmp_path / "docs" / "EMPTY.md").read_text(encoding="utf-8") == ""
