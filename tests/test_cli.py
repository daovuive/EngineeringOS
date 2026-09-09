from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from engineering_os.cli import main
from engineering_os.rag import RAGResponse, render_response


def test_version_command_returns_success() -> None:
    assert main(["version"]) == 0


def test_knowledge_ask_delegates_to_shared_query_service_and_preserves_output() -> None:
    response = RAGResponse(
        "The authoritative design decision. [Source: knowledge/design.md#Decision]",
        ("knowledge/design.md#Decision",),
        (),
    )
    output = StringIO()

    with (
        patch("engineering_os.cli.query_knowledge", return_value=response) as query_service,
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

    assert exit_code == 0
    assert output.getvalue() == f"{render_response(response)}\n"
    paths, query = query_service.call_args.args
    assert paths.root == Path(".").resolve()
    assert query == "What is the design decision?"
    assert query_service.call_args.kwargs == {
        "limit": 4,
        "min_score": 0.5,
        "confidence_threshold": 0.7,
        "include_memory": True,
    }
