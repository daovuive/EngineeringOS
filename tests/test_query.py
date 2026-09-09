from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from engineering_os.config import ProjectPaths
from engineering_os.knowledge import KnowledgeChunk
from engineering_os.query import query_knowledge, retrieve_knowledge
from engineering_os.rag import INSUFFICIENT_EVIDENCE


SETTINGS = {
    "knowledge": {
        "index": "runtime/index/knowledge.json",
        "retrieval": {
            "candidateMinScore": 0.45,
            "confidenceThreshold": 0.62,
            "overfetchFactor": 4,
        },
        "grounding": {
            "supportedClaimCoverage": 0.75,
            "partialClaimCoverage": 0.4,
            "minSharedTerms": 2,
        },
    },
    "memory": {"retrieval": {"maxAgeDays": 90}},
}
EMBEDDING_CONTRACT = {
    "contractVersion": "1.0",
    "provider": "test",
    "model": "test-embedding",
    "dimensions": 2,
}


class FakeRuntime:
    def __init__(self, query_vector: list[float], generated: str) -> None:
        self.query_vector = query_vector
        self.generated = generated
        self.prompts: list[str] = []
        self.roles: list[str] = []

    def embed(self, text: str) -> list[float]:
        return self.query_vector

    def generate(self, prompt: str, *, role: str = "rag") -> str:
        self.prompts.append(prompt)
        self.roles.append(role)
        return self.generated


class QueryKnowledgeTests(TestCase):
    def setUp(self) -> None:
        self.paths = ProjectPaths(root=Path("/project"))
        self.chunks = [
            KnowledgeChunk(
                "knowledge/design.md",
                "Decision",
                "The authoritative design decision.",
                [1.0, 0.0],
            ),
            KnowledgeChunk(
                "knowledge/other.md",
                "Note",
                "An unrelated note.",
                [0.0, 1.0],
            ),
        ]

    def _query(self, runtime: FakeRuntime, chunks: list[KnowledgeChunk] | None = None):
        with (
            patch("engineering_os.query.load_settings", return_value=SETTINGS) as load_settings,
            patch("engineering_os.query.load_runtime_config", return_value={}) as load_runtime_config,
            patch("engineering_os.query.create_runtime", return_value=runtime) as create_runtime,
            patch(
                "engineering_os.query.get_embedding_contract",
                return_value=EMBEDDING_CONTRACT,
            ) as get_embedding_contract,
            patch(
                "engineering_os.query.load_index",
                return_value=chunks if chunks is not None else self.chunks,
            ) as load_index,
        ):
            response = query_knowledge(self.paths, "What is the design decision?", limit=1)

        return response, {
            "load_settings": load_settings,
            "load_runtime_config": load_runtime_config,
            "create_runtime": create_runtime,
            "get_embedding_contract": get_embedding_contract,
            "load_index": load_index,
        }

    def test_grounded_answer_preserves_sources_and_uses_configured_path(self) -> None:
        runtime = FakeRuntime(
            [1.0, 0.0],
            "The authoritative design decision. [Source: knowledge/design.md#Decision]",
        )

        response, dependencies = self._query(runtime)

        self.assertEqual(
            response.answer,
            "The authoritative design decision. [Source: knowledge/design.md#Decision]",
        )
        self.assertEqual(response.sources, ("knowledge/design.md#Decision",))
        self.assertEqual(
            tuple(item.source for item in response.retrieved),
            ("knowledge/design.md#Decision",),
        )
        self.assertEqual(runtime.roles, ["rag"])
        self.assertEqual(
            dependencies["load_index"].call_args.args[0],
            Path("/project/runtime/index/knowledge.json"),
        )
        self.assertEqual(
            dependencies["load_index"].call_args.kwargs,
            {"embedding_contract": EMBEDDING_CONTRACT},
        )
        for dependency in dependencies.values():
            dependency.assert_called_once()

    def test_abstention_preserves_insufficient_evidence_without_generation(self) -> None:
        runtime = FakeRuntime(
            [0.0, 0.0],
            "This answer must not be generated.",
        )

        response, _ = self._query(runtime)

        self.assertEqual(response.answer, INSUFFICIENT_EVIDENCE)
        self.assertEqual(response.sources, ())
        self.assertEqual(runtime.prompts, [])

    def test_memory_remains_opt_in(self) -> None:
        chunks = self.chunks + [
            KnowledgeChunk(
                "memory/project-context.md",
                "Current Notes",
                "The project currently prefers local AI for private workflows.",
                [1.0, 0.0],
                "memory",
                "2026-09-01",
                "contextual",
            )
        ]
        runtime = FakeRuntime(
            [1.0, 0.0],
            "The authoritative design decision. [Source: knowledge/design.md#Decision]",
        )

        response, _ = self._query(runtime, chunks)
        self.assertNotIn("[Memory:", runtime.prompts[0])
        self.assertEqual(response.sources, ("knowledge/design.md#Decision",))

        runtime = FakeRuntime(
            [1.0, 0.0],
            "The authoritative design decision. [Source: knowledge/design.md#Decision]",
        )
        with (
            patch("engineering_os.query.load_settings", return_value=SETTINGS),
            patch("engineering_os.query.load_runtime_config", return_value={}),
            patch("engineering_os.query.create_runtime", return_value=runtime),
            patch("engineering_os.query.get_embedding_contract", return_value=EMBEDDING_CONTRACT),
            patch("engineering_os.query.load_index", return_value=chunks),
        ):
            query_knowledge(
                self.paths,
                "What is the design decision?",
                limit=2,
                include_memory=True,
            )

        self.assertIn("[Memory: memory/project-context.md#Current Notes", runtime.prompts[0])

    def test_retrieve_knowledge_reuses_score_and_confidence_gates(self) -> None:
        runtime = FakeRuntime([1.0, 0.0], "unused")
        with (
            patch("engineering_os.query.load_settings", return_value=SETTINGS),
            patch("engineering_os.query.load_runtime_config", return_value={}),
            patch("engineering_os.query.create_runtime", return_value=runtime),
            patch(
                "engineering_os.query.get_embedding_contract",
                return_value=EMBEDDING_CONTRACT,
            ),
            patch("engineering_os.query.load_index", return_value=self.chunks),
        ):
            retrieved = retrieve_knowledge(self.paths, "design", limit=1)

        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0].source, "knowledge/design.md#Decision")

        weak_chunks = [
            KnowledgeChunk(
                "knowledge/weak.md",
                "Weak",
                "Weak match.",
                [0.6, 0.8],
            )
        ]
        with (
            patch("engineering_os.query.load_settings", return_value=SETTINGS),
            patch("engineering_os.query.load_runtime_config", return_value={}),
            patch("engineering_os.query.create_runtime", return_value=runtime),
            patch(
                "engineering_os.query.get_embedding_contract",
                return_value=EMBEDDING_CONTRACT,
            ),
            patch("engineering_os.query.load_index", return_value=weak_chunks),
        ):
            self.assertEqual(retrieve_knowledge(self.paths, "design", limit=1), ())
