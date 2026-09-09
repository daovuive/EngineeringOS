import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from engineering_os.config import ProjectPaths, load_runtime_config
from engineering_os.llm import (
    LLMError,
    OllamaRuntime,
    build_pull_commands,
    create_runtime,
    get_default_runtime_definition,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class LLMConfigurationTests(TestCase):
    def setUp(self) -> None:
        self.config = load_runtime_config(ProjectPaths(root=PROJECT_ROOT))

    def test_windows_ollama_provider_and_logical_models_are_configured(self) -> None:
        definition = get_default_runtime_definition(self.config)

        self.assertEqual(definition.provider.id, "ollama-local")
        self.assertEqual(definition.provider.type, "ollama")
        self.assertEqual(definition.provider.host, "http://localhost:11434")
        self.assertEqual(definition.model_for("chat"), "phi3.5:3.8b-mini-instruct-q4_K_M")
        self.assertEqual(definition.model_for("embedding"), "nomic-embed-text")
        self.assertIsInstance(create_runtime(self.config), OllamaRuntime)

    def test_endpoint_can_be_overridden_for_windows_ollama_from_wsl(self) -> None:
        with patch.dict(
            os.environ,
            {"ENGINEERINGOS_OLLAMA_ENDPOINT": "http://172.20.0.1:11434"},
        ):
            definition = get_default_runtime_definition(self.config)

        self.assertEqual(definition.provider.host, "http://172.20.0.1:11434")

    def test_ollama_pull_plan_uses_logical_model_bindings(self) -> None:
        commands = build_pull_commands(self.config)

        self.assertIn("ollama pull granite3.1-moe:3b", commands)
        self.assertIn("ollama pull nomic-embed-text", commands)
        self.assertEqual(len(commands), 4)

    def test_generation_can_bound_tokens_for_one_workflow_stage(self) -> None:
        class RecordingHttpClient:
            def __init__(self) -> None:
                self.payload = None

            def request_json_lines(self, method, path, payload):
                self.payload = payload
                return [{"response": "bounded"}]

        client = RecordingHttpClient()
        runtime = OllamaRuntime(
            get_default_runtime_definition(self.config),
            http_client=client,
        )

        self.assertEqual(
            runtime.generate("stage", role="reasoning", max_tokens=123),
            "bounded",
        )
        self.assertEqual(client.payload["options"]["num_predict"], 123)

        with self.assertRaisesRegex(LLMError, "positive integer"):
            runtime.generate("stage", max_tokens=0)

    def test_structured_generation_sends_schema_and_parses_object(self) -> None:
        class RecordingHttpClient:
            def __init__(self) -> None:
                self.payload = None

            def request_json_lines(self, method, path, payload):
                self.payload = payload
                return [{"response": '{"proposal":"bounded"}'}]

        client = RecordingHttpClient()
        runtime = OllamaRuntime(
            get_default_runtime_definition(self.config),
            http_client=client,
        )
        schema = {
            "type": "object",
            "properties": {"proposal": {"type": "string"}},
            "required": ["proposal"],
        }

        result = runtime.generate_structured(
            "proposal",
            schema,
            role="reasoning",
            max_tokens=321,
        )

        self.assertEqual(result, {"proposal": "bounded"})
        self.assertEqual(client.payload["format"], schema)
        self.assertEqual(client.payload["options"]["num_predict"], 321)
