import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from engineering_os.config import ProjectPaths, load_runtime_config
from engineering_os.ingestion import (
    KnowledgeIngestionError,
    ingest_bytes,
    ingest_path,
    ingest_text,
    retry_document_index,
)
from engineering_os.knowledge import load_index
from engineering_os.llm import LLMError, get_embedding_contract


class FakeEmbeddingRuntime:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.inputs: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.inputs.append(text)
        if self.fail:
            raise LLMError("embedding unavailable")
        return [float(len(text)), 1.0]


class IngestionTests(TestCase):
    def _project(self, temporary: str) -> tuple[ProjectPaths, dict[str, object]]:
        root = Path(temporary)
        (root / "knowledge/inbox").mkdir(parents=True)
        (root / "runtime/index").mkdir(parents=True)
        (root / "configs/ai").mkdir(parents=True)
        settings = {
            "knowledge": {
                "root": "knowledge",
                "index": "runtime/index/knowledge.json",
                "ingestion": {"directory": "knowledge/inbox", "maxBytes": 4096},
            }
        }
        (root / "configs/settings.json").write_text(json.dumps(settings), encoding="utf-8")
        (root / "configs/ai/providers.json").write_text(
            json.dumps(
                {
                    "providers": {
                        "fake": {"type": "ollama", "endpoint": "http://localhost:1"}
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
            json.dumps({"defaultProvider": "fake", "options": {}}), encoding="utf-8"
        )
        return ProjectPaths(root=root), settings

    def test_direct_text_is_saved_indexed_and_idempotent(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)
            runtime = FakeEmbeddingRuntime()

            first = ingest_text(
                paths,
                "Độ trễ mục tiêu là 42 ms.",
                title="Ghi chú Unicode",
                runtime=runtime,
            )
            calls_after_first = len(runtime.inputs)
            second = ingest_text(
                paths,
                "Độ trễ mục tiêu là 42 ms.",
                title="Tên khác không tạo bản sao",
                runtime=runtime,
            )

            self.assertEqual(first.indexing_state, "indexed")
            self.assertTrue(first.ready_for_rag)
            self.assertEqual(second.import_outcome, "unchanged")
            self.assertEqual(second.document_path, first.document_path)
            self.assertEqual(len(runtime.inputs), calls_after_first)
            contract = get_embedding_contract(load_runtime_config(paths))
            chunks = load_index(paths.root / "runtime/index/knowledge.json", embedding_contract=contract)
            self.assertEqual({chunk.path for chunk in chunks}, {first.document_path.removeprefix("knowledge/")})

    def test_filename_collision_is_deterministic_and_original_is_preserved(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)
            runtime = FakeEmbeddingRuntime()
            source = paths.root / "Tài liệu mới.txt"
            source.write_text("first", encoding="utf-8")
            first = ingest_path(paths, source, runtime=runtime)
            source.write_text("second", encoding="utf-8")
            second = ingest_path(paths, source, runtime=runtime)

            self.assertEqual(first.document_path, "knowledge/inbox/Tài-liệu-mới.md")
            self.assertRegex(second.document_path, r"Tài-liệu-mới-[0-9a-f]{12}\.md$")
            self.assertEqual(source.read_text(encoding="utf-8"), "second")

    def test_no_index_and_failed_index_preserve_saved_document(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)
            skipped = ingest_text(
                paths,
                "Saved without embedding.",
                title="Skipped",
                auto_index=False,
            )
            failed = ingest_text(
                paths,
                "Saved despite embedding failure.",
                title="Failed",
                runtime=FakeEmbeddingRuntime(fail=True),
            )

            self.assertEqual(skipped.indexing_state, "skipped")
            self.assertEqual(failed.indexing_state, "failed")
            self.assertIn("embedding unavailable", failed.error or "")
            self.assertTrue((paths.root / skipped.document_path).exists())
            self.assertTrue((paths.root / failed.document_path).exists())

            retry = retry_document_index(paths, failed.document_path, runtime=FakeEmbeddingRuntime())
            self.assertEqual(retry.indexing_state, "indexed")

    def test_concurrent_document_updates_preserve_both_documents(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)

            def add(number: int):
                return ingest_text(
                    paths,
                    f"Distinct concurrent fact {number}.",
                    title=f"Concurrent {number}",
                    runtime=FakeEmbeddingRuntime(),
                )

            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(add, (1, 2)))

            runtime_config = load_runtime_config(paths)
            chunks = load_index(
                paths.root / "runtime/index/knowledge.json",
                embedding_contract=get_embedding_contract(runtime_config),
            )
            indexed_paths = {chunk.path for chunk in chunks}
            self.assertTrue(all(result.document_path.removeprefix("knowledge/") in indexed_paths for result in results))

    def test_rejects_unsupported_binary_oversized_and_unsafe_retry(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)
            with self.assertRaisesRegex(KnowledgeIngestionError, "Unsupported file format"):
                ingest_bytes(paths, b"%PDF", source_name="document.pdf")
            with self.assertRaisesRegex(KnowledgeIngestionError, "valid UTF-8"):
                ingest_bytes(paths, b"\xff", source_name="document.txt")
            with self.assertRaisesRegex(KnowledgeIngestionError, "exceeds"):
                ingest_bytes(paths, b"x" * 4097, source_name="large.txt")
            outside = paths.root / "outside.md"
            outside.write_text("# Outside\n\nNo", encoding="utf-8")
            with self.assertRaisesRegex(KnowledgeIngestionError, "inside the knowledge root"):
                retry_document_index(paths, "outside.md", runtime=FakeEmbeddingRuntime())

    def test_updated_document_replaces_stale_chunks_and_preserves_unrelated_entries(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)
            first = ingest_text(
                paths, "Original alpha fact.", title="Alpha", runtime=FakeEmbeddingRuntime()
            )
            second = ingest_text(
                paths, "Stable beta fact.", title="Beta", runtime=FakeEmbeddingRuntime()
            )
            first_path = paths.root / first.document_path
            first_path.write_text("# Alpha\n\nUpdated alpha fact.", encoding="utf-8")

            update = retry_document_index(
                paths, first.document_path, runtime=FakeEmbeddingRuntime()
            )

            contract = get_embedding_contract(load_runtime_config(paths))
            chunks = load_index(
                paths.root / "runtime/index/knowledge.json", embedding_contract=contract
            )
            by_path = {chunk.path: chunk.text for chunk in chunks}
            self.assertEqual(update.indexing_state, "indexed")
            self.assertIn("Updated alpha fact", by_path[first.document_path.removeprefix("knowledge/")])
            self.assertIn("Stable beta fact", by_path[second.document_path.removeprefix("knowledge/")])

    def test_atomic_persistence_failure_preserves_previous_valid_index(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)
            initial = ingest_text(
                paths, "Original persisted fact.", title="Atomic", runtime=FakeEmbeddingRuntime()
            )
            document = paths.root / initial.document_path
            document.write_text("# Atomic\n\nReplacement fact.", encoding="utf-8")

            with patch("engineering_os.knowledge.os.replace", side_effect=OSError("disk full")):
                failed = retry_document_index(
                    paths, initial.document_path, runtime=FakeEmbeddingRuntime()
                )

            self.assertEqual(failed.indexing_state, "failed")
            contract = get_embedding_contract(load_runtime_config(paths))
            chunks = load_index(
                paths.root / "runtime/index/knowledge.json", embedding_contract=contract
            )
            self.assertTrue(any("Original persisted fact" in chunk.text for chunk in chunks))
            self.assertFalse(any("Replacement fact" in chunk.text for chunk in chunks))

    def test_dimension_mismatch_fails_without_publishing_an_index(self) -> None:
        with TemporaryDirectory() as temporary:
            paths, _ = self._project(temporary)

            class WrongDimensionRuntime(FakeEmbeddingRuntime):
                def embed(self, text: str) -> list[float]:
                    return [1.0]

            result = ingest_text(
                paths,
                "Dimension compatibility fact.",
                title="Dimensions",
                runtime=WrongDimensionRuntime(),
            )

            self.assertEqual(result.indexing_state, "failed")
            self.assertIn("expected 2, got 1", result.error or "")
            self.assertFalse((paths.root / "runtime/index/knowledge.json").exists())
