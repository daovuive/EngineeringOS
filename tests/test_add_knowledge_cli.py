from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from engineering_os.cli import main
from engineering_os.config import ProjectPaths
from engineering_os.ingestion import IngestionResult


class AddKnowledgeCliTests(TestCase):
    def test_short_file_form_defaults_to_indexing(self) -> None:
        result = IngestionResult(
            "knowledge/inbox/note.md", "saved", "indexed", 2, True
        )
        output = StringIO()
        with (
            patch("engineering_os.cli.ingest_path", return_value=result) as ingest,
            redirect_stdout(output),
        ):
            exit_code = main(["add-knowledge", "my document.md"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            ingest.call_args.args[1], Path(".").resolve() / "my document.md"
        )
        self.assertEqual(
            ingest.call_args.kwargs, {"title": None, "auto_index": True}
        )
        self.assertIn("Ready for RAG: yes", output.getvalue())

    def test_explicit_file_and_auto_index_form_is_equivalent(self) -> None:
        result = IngestionResult(
            "knowledge/inbox/note.md", "saved", "indexed", 1, True
        )
        with patch("engineering_os.cli.ingest_path", return_value=result) as ingest:
            self.assertEqual(
                main(["add-knowledge", "--file", "Tài liệu mới.md", "--auto-index"]),
                0,
            )
        self.assertEqual(
            ingest.call_args.args[1], Path(".").resolve() / "Tài liệu mới.md"
        )
        self.assertTrue(ingest.call_args.kwargs["auto_index"])

    def test_text_stdin_no_index_and_conflicts(self) -> None:
        skipped = IngestionResult(
            "knowledge/inbox/note.md", "saved", "skipped", None, None
        )
        with patch("engineering_os.cli.ingest_text", return_value=skipped) as ingest:
            self.assertEqual(
                main(
                    [
                        "add-knowledge",
                        "--text",
                        "Nội dung",
                        "--title",
                        "Tiêu đề",
                        "--no-index",
                    ]
                ),
                0,
            )
        ingest.assert_called_once_with(
            ProjectPaths(root=Path(".").resolve()),
            "Nội dung",
            title="Tiêu đề",
            auto_index=False,
        )

        with (
            patch("engineering_os.cli.sys.stdin", StringIO("stdin content")),
            patch("engineering_os.cli.ingest_text", return_value=skipped) as stdin_ingest,
        ):
            self.assertEqual(
                main(["add-knowledge", "--stdin", "--title", "stdin title"]), 0
            )
        self.assertEqual(stdin_ingest.call_args.args[1], "stdin content")

        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["add-knowledge"]), 1)
            self.assertEqual(main(["add-knowledge", "a.md", "--file", "b.md"]), 1)
            self.assertEqual(
                main(
                    [
                        "add-knowledge",
                        "--text",
                        "x",
                        "--auto-index",
                        "--no-index",
                    ]
                ),
                1,
            )
        self.assertIn("Exactly one input source", output.getvalue())
        self.assertIn("cannot be used together", output.getvalue())

    def test_index_failure_returns_nonzero_and_retry_command(self) -> None:
        failed = IngestionResult(
            "knowledge/inbox/note.md",
            "saved",
            "failed",
            None,
            None,
            "embedding down",
        )
        output = StringIO()
        with (
            patch("engineering_os.cli.ingest_text", return_value=failed),
            redirect_stdout(output),
        ):
            exit_code = main(["add-knowledge", "--text", "knowledge"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Saved, indexing failed: embedding down", output.getvalue())
        self.assertIn("add-knowledge --file", output.getvalue())
