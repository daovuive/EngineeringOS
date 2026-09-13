import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from engineering_os.log_ingestion import (
    LogIngestionConfig,
    LogIngestionError,
    discover_allowed_logs,
    read_log_chunk_drafts,
)
from engineering_os.knowledge import LOG_SOURCE, rebuild_index


class FakeRuntime:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0]


class LogIngestionTests(TestCase):
    def test_explicit_rebuild_adds_enabled_logs_with_contextual_authority(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            knowledge = root / "knowledge"
            knowledge.mkdir()
            (knowledge / "fact.md").write_text("# Fact\n\nStable fact", encoding="utf-8")
            log = root / "runtime/logs/rag/app.log"
            log.parent.mkdir(parents=True)
            log.write_text("safe runtime observation", encoding="utf-8")
            chunks = rebuild_index(
                root / "runtime/index/knowledge.json",
                [(knowledge, "knowledge", None)],
                FakeRuntime(),
                embedding_contract={
                    "contractVersion": "1.0",
                    "provider": "test",
                    "model": "test",
                    "dimensions": 2,
                },
                log_config=LogIngestionConfig(enabled=True),
                project_root=root,
            )
            indexed_log = next(item for item in chunks if item.source_type == LOG_SOURCE)
            self.assertEqual(indexed_log.authority, "contextual")
            self.assertEqual(indexed_log.document_type, "log")

    def test_disabled_and_non_allowlisted_logs_are_ignored(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            allowed = root / "runtime/logs/rag/app.log"
            allowed.parent.mkdir(parents=True)
            allowed.write_text("safe", encoding="utf-8")
            other = root / "logs/other.log"
            other.parent.mkdir()
            other.write_text("safe", encoding="utf-8")
            self.assertEqual(discover_allowed_logs(root, LogIngestionConfig()), [])
            enabled = LogIngestionConfig(enabled=True)
            self.assertEqual(discover_allowed_logs(root, enabled), [allowed])

    def test_allowlisted_log_is_chunked_with_timestamp_metadata(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "runtime/logs/services/api.log"
            log.parent.mkdir(parents=True)
            log.write_text("2026-09-13 request completed safely", encoding="utf-8")
            config = LogIngestionConfig(enabled=True)
            paths = discover_allowed_logs(root, config)
            drafts = read_log_chunk_drafts(paths[0], root)
            self.assertEqual(drafts[0].path, "runtime/logs/services/api.log")
            self.assertEqual(drafts[0].document_type, "log")
            self.assertEqual(drafts[0].tags, ("log",))
            self.assertTrue(drafts[0].source_timestamp)
            self.assertTrue(drafts[0].chunk_id)

    def test_expired_log_is_ignored(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "runtime/logs/rag/old.log"
            log.parent.mkdir(parents=True)
            log.write_text("old safe event", encoding="utf-8")
            old = datetime.now(timezone.utc) - timedelta(days=20)
            os.utime(log, (old.timestamp(), old.timestamp()))
            self.assertEqual(
                discover_allowed_logs(root, LogIngestionConfig(enabled=True)), []
            )

    def test_oversized_binary_and_sensitive_logs_are_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "runtime/logs/rag"
            directory.mkdir(parents=True)
            oversized = directory / "large.log"
            oversized.write_bytes(b"x" * (1024 * 1024 + 1))
            with self.assertRaisesRegex(LogIngestionError, "size limit"):
                discover_allowed_logs(
                    root, LogIngestionConfig(enabled=True, max_file_size_mb=1)
                )
            oversized.unlink()
            binary = directory / "binary.log"
            binary.write_bytes(b"safe\x00binary")
            with self.assertRaisesRegex(LogIngestionError, "Binary"):
                read_log_chunk_drafts(binary, root)
            binary.write_text("authorization: Bearer secret-value", encoding="utf-8")
            with self.assertRaisesRegex(LogIngestionError, "Sensitive"):
                read_log_chunk_drafts(binary, root)

    def test_unsafe_allowlist_pattern_is_rejected(self) -> None:
        with self.assertRaisesRegex(LogIngestionError, "inside the project"):
            LogIngestionConfig.from_settings(
                {"knowledge": {"logs": {"enabled": True, "allowlist": ["../*.log"]}}}
            )
