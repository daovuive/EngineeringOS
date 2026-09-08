"""Governance regressions; runnable with unittest without optional dependencies."""

import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from engineering_os.cli import main
from engineering_os.structure import ensure_structure, validate_structure


class StructureGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="engineering-os-governance-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.write("README.md", "# Project\n[Docs](docs/README.md)\n")
        self.write("docs/README.md", "# Docs\n[Guides](guides/README.md)\n")
        self.write("docs/guides/README.md", "# Guides\n")
        self.structure = {
            "folders": [{"path": "docs"}, {"path": "docs/guides"}],
            "files": [],
            "governance": {
                "readmeName": "README.md",
                "protectedRootReadme": {
                    "path": "README.md",
                    "sha256": hashlib.sha256((self.root / "README.md").read_bytes()).hexdigest(),
                },
                "ignoredDirectories": ["tmp", "runtime/cache"],
                "allowedRootFiles": ["README.md"],
            },
        }
        self.templates = {"templates": [{"id": "EMPTY", "source": None}]}

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def validate(self):
        return validate_structure(self.root, self.structure, self.templates)

    def test_complete_registered_tree_passes(self) -> None:
        result = self.validate()
        self.assertTrue(result.ok, result.governance_errors)
        self.assertEqual(result.error_count, 0)

    def test_new_top_level_folder_uses_manifest_without_root_readme_link(self) -> None:
        self.structure["folders"].append({"path": "new-area"})
        self.write("new-area/README.md", "# New area\n")
        result = self.validate()
        self.assertTrue(result.ok, result.governance_errors)

    def test_missing_readme_and_parent_navigation_fail(self) -> None:
        (self.root / "docs/guides/README.md").unlink()
        self.write("docs/README.md", "# Docs\n")
        result = self.validate()
        self.assertIn("Missing architecture README: docs/guides/README.md", result.governance_errors)
        self.assertTrue(any("Parent README docs/README.md must link" in error for error in result.governance_errors))
        self.assertFalse(result.ok)
        self.assertEqual(result.error_count, len(result.governance_errors))

    def test_empty_readme_fails(self) -> None:
        self.write("docs/guides/README.md", "  \n")
        self.assertIn("Empty architecture README: docs/guides/README.md", self.validate().governance_errors)

    def test_new_file_requires_local_readme_link(self) -> None:
        self.write("docs/guides/new-lesson.md", "# A lesson\n")
        self.assertTrue(any("Unindexed file: docs/guides/new-lesson.md" in error for error in self.validate().governance_errors))
        self.write("docs/guides/README.md", "# Guides\n[Lesson](new-lesson.md)\n")
        self.assertTrue(self.validate().ok, self.validate().governance_errors)

    def test_auto_indexed_file_pattern_does_not_require_individual_links(self) -> None:
        self.structure["governance"]["autoIndexedFiles"] = [
            {"directory": "docs/guides", "pattern": "Lesson-*.md"}
        ]
        self.write("docs/guides/Lesson-001.md", "# A lesson\n")
        self.assertTrue(self.validate().ok, self.validate().governance_errors)

        self.write("docs/guides/other.md", "# Other\n")
        errors = self.validate().governance_errors
        self.assertIn(
            "Unindexed file: docs/guides/other.md must be linked from docs/guides/README.md",
            errors,
        )

    def test_sync_preserves_existing_root_and_refuses_missing_protected_root(self) -> None:
        original = (self.root / "README.md").read_bytes()
        self.structure["files"] = [{"path": "README.md", "template": "EMPTY"}]
        ensure_structure(self.root, self.structure, self.templates, verbose=False)
        self.assertEqual((self.root / "README.md").read_bytes(), original)
        (self.root / "README.md").unlink()
        self.structure["folders"].append({"path": "new-folder"})
        with self.assertRaisesRegex(ValueError, "Protected README.md is missing"):
            ensure_structure(self.root, self.structure, self.templates, verbose=False)
        self.assertFalse((self.root / "README.md").exists())
        self.assertFalse((self.root / "new-folder").exists())

    def test_root_approval_exception_does_not_exempt_nested_navigation_or_hash(self) -> None:
        self.structure["governance"]["rootNavigationPendingApproval"] = True
        self.write("README.md", "# Changed root\n")
        self.write("docs/README.md", "# Docs\n")
        errors = self.validate().governance_errors
        self.assertTrue(any("Protected README.md changed" in error for error in errors))
        self.assertTrue(any("Parent README docs/README.md must link" in error for error in errors))
        self.assertFalse(any("Parent README README.md must link" in error for error in errors))

    def test_markdown_paths_support_encoding_anchors_references_and_parentheses(self) -> None:
        self.write("docs/a file (draft).md", "Document\n")
        self.write("docs/README.md", """# Docs
[Guides](guides/README.md#anything)
[Space](<a file (draft).md>)
[Encoded](a%20file%20%28draft%29.md#heading)
[Balanced](a%20file%20(draft).md)
[Reference][source]
[source]: <a file (draft).md> "Source document"
[Site](https://example.com/missing)
[Email](mailto:user@example.com)
[Self](#intro)
`[Example](not-a-real-file.md)`
```markdown
[Template placeholder](missing/example.md)
```
~~~markdown
[Another placeholder](missing.md)
~~~
""")
        self.assertTrue(self.validate().ok, self.validate().governance_errors)

    def test_broken_and_escaping_local_links_fail(self) -> None:
        self.write("docs/guides/README.md", "# Guides\n[Missing](missing.md)\n[Escape](../../../outside.md)\n")
        errors = self.validate().governance_errors
        self.assertIn("Broken README link in docs/guides/README.md: missing.md", errors)
        self.assertIn("README link escapes project in docs/guides/README.md: ../../../outside.md", errors)

    def test_machine_specific_file_links_fail(self) -> None:
        self.write("docs/guides/README.md", "# Guides\n[Drive](C:/outside.md)\n[File URI](file:///outside.md)\n")
        errors = self.validate().governance_errors
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(all("must use a relative project path" in error for error in errors))

    def test_unregistered_content_fails_but_generated_and_empty_trees_are_skipped(self) -> None:
        self.write("surprise.txt", "unexpected\n")
        self.write("docs/unplanned/deep/content.md", "unexpected\n")
        self.write("tmp/pytest/work/file.txt", "generated\n")
        self.write("runtime/cache/blobs/file.txt", "generated\n")
        self.write("docs/__pycache__/cache.pyc", "generated\n")
        (self.root / "old-date/empty").mkdir(parents=True)
        errors = self.validate().governance_errors
        self.assertIn("Unexpected root file: surprise.txt", errors)
        self.assertIn("Unregistered directory: docs/unplanned", errors)
        self.assertIn("Unregistered directory: docs/unplanned/deep", errors)
        self.assertEqual(len(errors), 3, errors)

    def test_duplicate_and_escaping_manifest_paths_fail_before_sync_writes(self) -> None:
        for invalid in ("../outside", "/absolute", "C:/outside", "docs/../outside", "docs//extra"):
            with self.subTest(path=invalid):
                self.structure["folders"] = [{"path": "new-folder"}, {"path": invalid}]
                self.assertTrue(any("path" in error.lower() for error in self.validate().governance_errors))
                with self.assertRaises(ValueError):
                    ensure_structure(self.root, self.structure, self.templates, verbose=False)
                self.assertFalse((self.root / "new-folder").exists())
        self.structure["folders"] = [{"path": "docs"}, {"path": "DOCS"}]
        self.assertIn("Duplicate manifest path: DOCS", self.validate().governance_errors)

    def test_skill_registry_requires_unique_ids_existing_files_and_declared_parent(self) -> None:
        self.write("configs/README.md", "# Configs\n")
        self.structure["folders"].append({"path": "configs"})
        self.structure["governance"]["rootNavigationPendingApproval"] = True
        self.write("configs/skills.json", json.dumps({"skills": [
            {"id": "review", "path": "docs/guides/README.md"},
            {"id": "review", "path": "skills/missing/SKILL.md"},
        ]}))
        errors = self.validate().governance_errors
        self.assertIn("Duplicate skill id: review", errors)
        self.assertIn("Missing registered skill: skills/missing/SKILL.md", errors)
        self.assertIn("Skill parent is not a declared folder: skills/missing/SKILL.md", errors)

    def test_legacy_manifest_does_not_enable_governance(self) -> None:
        self.structure.pop("governance")
        self.write("random/file.txt", "legacy content\n")
        self.write("docs/README.md", "")
        self.assertTrue(self.validate().ok)

    def test_cli_returns_nonzero_and_explains_governance_failure(self) -> None:
        self.write("docs/guides/README.md", "")
        output = StringIO()
        with (
            patch("engineering_os.cli.load_project_structure", return_value=self.structure),
            patch("engineering_os.cli.load_template_config", return_value=self.templates),
            redirect_stdout(output),
        ):
            exit_code = main(["--root", str(self.root), "validate"])
        self.assertEqual(exit_code, 1)
        self.assertIn("Governance: Empty architecture README", output.getvalue())
        self.assertIn("Validation failed: 1 problem(s).", output.getvalue())


if __name__ == "__main__":
    unittest.main()
