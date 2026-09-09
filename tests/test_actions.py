from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from engineering_os.actions import ACTION_CATALOG, ActionError, execute_action
from engineering_os.config import ProjectPaths
from engineering_os.knowledge import KnowledgeChunk
from engineering_os.rag import RAGResponse
from engineering_os.structure import ValidationResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FakeRuntime:
    def list_models(self) -> list[str]:
        return ["available-model"]

    def generate(self, prompt: str, *, role: str, max_tokens=None) -> str:
        return f"{role}: {prompt}"

    def embed(self, text: str) -> list[float]:
        return [1.0, 2.0, 3.0]


class ActionTests(TestCase):
    def setUp(self) -> None:
        self.paths = ProjectPaths(root=PROJECT_ROOT)

    def test_catalog_is_unique_and_declares_execution_characteristics(self) -> None:
        identifiers = [action.id for action in ACTION_CATALOG]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertIn("project.validate", identifiers)
        self.assertIn("llm.chat", identifiers)
        self.assertIn("knowledge.index", identifiers)
        self.assertTrue(next(item for item in ACTION_CATALOG if item.id == "knowledge.index").long_running)

    def test_version_validate_and_config_actions_use_project_services(self) -> None:
        self.assertIn("version", execute_action(self.paths, "project.version", {}))
        with patch(
            "engineering_os.actions.validate_structure", return_value=ValidationResult()
        ):
            validation = execute_action(self.paths, "project.validate", {})
        self.assertTrue(validation["ok"])
        shown = execute_action(self.paths, "config.show", {"name": "settings"})
        self.assertEqual(shown["name"], "settings")
        self.assertIn("knowledge", shown["config"])

    def test_runtime_actions_validate_fields_and_use_configured_roles(self) -> None:
        with patch("engineering_os.actions.create_runtime", return_value=FakeRuntime()):
            chat = execute_action(
                self.paths,
                "llm.chat",
                {"prompt": "Explain coupling", "role": "reasoning"},
            )
            embedded = execute_action(self.paths, "llm.embed", {"text": "vector me"})

        self.assertEqual(chat["response"], "reasoning: Explain coupling")
        self.assertEqual(embedded["dimensions"], 3)
        with self.assertRaisesRegex(ActionError, "role must be one of"):
            execute_action(
                self.paths, "llm.chat", {"prompt": "x", "role": "unconfigured"}
            )
        with self.assertRaisesRegex(ActionError, "unsupported fields"):
            execute_action(self.paths, "project.version", {"shell": "rm"})

    def test_mutating_actions_require_explicit_confirmation(self) -> None:
        with self.assertRaisesRegex(ActionError, "confirmed=true"):
            execute_action(self.paths, "project.sync", {"confirmed": False})
        with self.assertRaisesRegex(ActionError, "confirmed=true"):
            execute_action(self.paths, "knowledge.index", {"confirmed": False})

    def test_project_mutation_is_bound_to_a_current_preview(self) -> None:
        validation = ValidationResult(missing_folders=[Path("knowledge/new")])
        with (
            patch("engineering_os.actions.validate_structure", return_value=validation),
            patch("engineering_os.actions.ensure_structure") as ensure,
        ):
            preview = execute_action(
                self.paths, "project.preview", {"operation": "sync"}
            )
            result = execute_action(
                self.paths,
                "project.sync",
                {"confirmed": True, "preview_token": preview["preview_token"]},
            )

        self.assertEqual(preview["folder_count"], 1)
        self.assertEqual(result["created_count"], 1)
        ensure.assert_called_once()

        with patch(
            "engineering_os.actions.validate_structure", return_value=validation
        ):
            with self.assertRaisesRegex(ActionError, "preview is stale"):
                execute_action(
                    self.paths,
                    "project.sync",
                    {"confirmed": True, "preview_token": "0" * 64},
                )

    def test_project_mutation_rejects_a_governance_blocked_preview(self) -> None:
        validation = ValidationResult(governance_errors=["Unexpected root file: demo"])
        with (
            patch("engineering_os.actions.validate_structure", return_value=validation),
            patch("engineering_os.actions.ensure_structure") as ensure,
        ):
            preview = execute_action(
                self.paths, "project.preview", {"operation": "sync"}
            )
            with self.assertRaisesRegex(ActionError, "blocked by unresolved governance"):
                execute_action(
                    self.paths,
                    "project.sync",
                    {"confirmed": True, "preview_token": preview["preview_token"]},
                )

        self.assertTrue(preview["blocked"])
        ensure.assert_not_called()

    def test_search_and_ask_actions_preserve_options_and_sources(self) -> None:
        chunk = KnowledgeChunk("inbox/demo.md", "Fact", "Distinct fact", [1.0, 0.0])
        with (
            patch("engineering_os.actions.create_runtime", return_value=FakeRuntime()),
            patch("engineering_os.actions.load_index", return_value=[chunk]),
            patch(
                "engineering_os.actions.search_index", return_value=[(0.87654, chunk)]
            ) as search,
        ):
            result = execute_action(
                self.paths,
                "knowledge.search",
                {"query": "distinct", "limit": 7, "include_memory": False},
            )
        self.assertEqual(result["results"][0]["score"], 0.8765)
        self.assertEqual(result["results"][0]["source"], "inbox/demo.md#Fact")
        self.assertEqual(search.call_args.kwargs["limit"], 7)

        response = RAGResponse("Grounded answer", ("inbox/demo.md#Fact",), ())
        with (
            patch("engineering_os.actions.create_runtime", return_value=FakeRuntime()),
            patch("engineering_os.actions.query_knowledge", return_value=response) as ask,
        ):
            result = execute_action(
                self.paths,
                "knowledge.ask",
                {
                    "query": "question",
                    "limit": 4,
                    "min_score": 0.4,
                    "confidence_threshold": 0.6,
                    "include_memory": True,
                },
            )
        self.assertEqual(result["sources"], ["inbox/demo.md#Fact"])
        self.assertEqual(ask.call_args.kwargs["limit"], 4)
        self.assertTrue(ask.call_args.kwargs["include_memory"])
