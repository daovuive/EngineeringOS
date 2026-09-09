from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from engineering_os.cli import main
from engineering_os.rag import RAGResponse, render_response
from engineering_os.workflows import WorkflowResponse


class CliTests(TestCase):
    def test_version_command_returns_success(self) -> None:
        self.assertEqual(main(["version"]), 0)

    def test_knowledge_ask_delegates_to_shared_query_service_and_preserves_output(
        self,
    ) -> None:
        response = RAGResponse(
            "The authoritative design decision. [Source: knowledge/design.md#Decision]",
            ("knowledge/design.md#Decision",),
            (),
        )
        output = StringIO()

        with (
            patch(
                "engineering_os.cli.query_knowledge", return_value=response
            ) as query_service,
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "--root",
                    ".",
                    "knowledge",
                    "ask",
                    "What is the design decision?",
                    "--limit",
                    "4",
                    "--min-score",
                    "0.5",
                    "--confidence-threshold",
                    "0.7",
                    "--include-memory",
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), f"{render_response(response)}\n")
        paths, query = query_service.call_args.args
        self.assertEqual(paths.root, Path(".").resolve())
        self.assertEqual(query, "What is the design decision?")
        self.assertEqual(
            query_service.call_args.kwargs,
            {
                "limit": 4,
                "min_score": 0.5,
                "confidence_threshold": 0.7,
                "include_memory": True,
            },
        )

    def test_workflow_command_accepts_inline_input_and_prints_result(self) -> None:
        response = WorkflowResponse(
            "requirement-review",
            "# Requirement Review\n## Findings\nA finding",
            (),
            "not_requested",
        )
        output = StringIO()
        with (
            patch("engineering_os.cli.run_workflow", return_value=response) as service,
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "workflow",
                    "requirement-review",
                    "--text",
                    "The system shall respond quickly.",
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertIn(response.result, output.getvalue())
        paths, workflow_id, documents = service.call_args.args
        self.assertEqual(paths.root, Path(".").resolve())
        self.assertEqual(workflow_id, "requirement-review")
        self.assertEqual(documents[0].content, "The system shall respond quickly.")
        self.assertEqual(
            service.call_args.kwargs,
            {
                "with_knowledge": False,
                "knowledge_query": None,
            },
        )

    def test_knowledge_organize_delegates_to_safe_organizer(self) -> None:
        from engineering_os.knowledge_organizer import OrganizationResult

        output = StringIO()
        result = OrganizationResult(
            Path("incoming.md"),
            Path("knowledge/architecture/patterns/incoming.md"),
            "Reusable architecture pattern.",
            "would_copy",
        )
        with (
            patch("engineering_os.cli.create_runtime", return_value=object()),
            patch("engineering_os.cli.load_destinations", return_value=(object(),)),
            patch("engineering_os.cli.organize_markdown", return_value=result) as organize,
            redirect_stdout(output),
        ):
            exit_code = main(
                [
                    "--root",
                    ".",
                    "knowledge",
                    "organize",
                    "--file",
                    "incoming.md",
                    "--dry-run",
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("would_copy", output.getvalue())
        self.assertIn("knowledge index", output.getvalue())
        self.assertEqual(
            organize.call_args.args[0], Path(".").resolve() / "incoming.md"
        )
        self.assertEqual(organize.call_args.kwargs, {"move": False, "dry_run": True})
