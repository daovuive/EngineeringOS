import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from engineering_os.config import ProjectPaths
from engineering_os.library import (
    KnowledgeLibraryError,
    list_knowledge_documents,
    read_knowledge_document,
    resolve_knowledge_document,
)


class KnowledgeLibraryTests(TestCase):
    def _project(self, temporary: str) -> ProjectPaths:
        root = Path(temporary)
        (root / "knowledge/inbox").mkdir(parents=True)
        (root / "knowledge/architecture").mkdir(parents=True)
        (root / "runtime/index").mkdir(parents=True)
        (root / "configs/ai").mkdir(parents=True)
        (root / "configs/settings.json").write_text(
            json.dumps(
                {
                    "knowledge": {
                        "root": "knowledge",
                        "index": "runtime/index/knowledge.json",
                        "ingestion": {
                            "directory": "knowledge/inbox",
                            "maxBytes": 4096,
                        },
                    }
                }
            ),
            encoding="utf-8",
        )
        (root / "configs/ai/providers.json").write_text(
            json.dumps(
                {
                    "providers": {
                        "fake": {
                            "type": "ollama",
                            "endpoint": "http://localhost:1",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        (root / "configs/ai/models.json").write_text(
            json.dumps(
                {
                    "models": {
                        "embedding": {
                            "provider": "fake",
                            "model": "fake-embedding",
                            "dimensions": 2,
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        (root / "configs/ai/runtime.json").write_text(
            json.dumps({"defaultProvider": "fake", "options": {}}),
            encoding="utf-8",
        )
        return ProjectPaths(root=root)

    def test_lists_filters_and_reports_index_state(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._project(temporary)
            (paths.root / "knowledge/inbox/indexed.md").write_text(
                "# Indexed\n\nFact", encoding="utf-8"
            )
            (paths.root / "knowledge/architecture/saved.md").write_text(
                "# Saved\n\nFact", encoding="utf-8"
            )
            (paths.root / "runtime/index/knowledge.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": "2.0",
                        "embedding": {
                            "contractVersion": "1.0",
                            "provider": "fake",
                            "model": "fake-embedding",
                            "dimensions": 2,
                        },
                        "chunks": [
                            {
                                "path": "inbox/indexed.md",
                                "heading": "Indexed",
                                "text": "Fact",
                                "embedding": [1.0, 0.0],
                                "source_type": "knowledge",
                                "last_updated": None,
                                "authority": "authoritative",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = list_knowledge_documents(paths)
            by_name = {item["name"]: item for item in result["documents"]}
            self.assertEqual(by_name["indexed.md"]["status"], "indexed")
            self.assertEqual(by_name["saved.md"]["status"], "saved_only")
            self.assertEqual(result["summary"]["documents"], 2)
            filtered = list_knowledge_documents(paths, query="indexed")
            self.assertEqual([item["name"] for item in filtered["documents"]], ["indexed.md"])

    def test_reads_only_regular_utf8_markdown_under_knowledge(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._project(temporary)
            document = paths.root / "knowledge/inbox/note.md"
            document.write_text("# Note\n\nSafe content", encoding="utf-8")
            (paths.root / "configs/secret.md").parent.mkdir(exist_ok=True)
            (paths.root / "configs/secret.md").write_text("secret", encoding="utf-8")

            self.assertEqual(
                resolve_knowledge_document(paths, "inbox/note.md"), document
            )
            self.assertIn("Safe content", read_knowledge_document(paths, "knowledge/inbox/note.md")["content"])
            with self.assertRaisesRegex(KnowledgeLibraryError, "governed Markdown"):
                resolve_knowledge_document(paths, "configs/secret.md")
            with self.assertRaisesRegex(KnowledgeLibraryError, "inside the knowledge root"):
                resolve_knowledge_document(paths, "../configs/secret.md")

            link = paths.root / "knowledge/inbox/link.md"
            link.symlink_to(document)
            with self.assertRaisesRegex(KnowledgeLibraryError, "governed Markdown"):
                resolve_knowledge_document(paths, "inbox/link.md")
