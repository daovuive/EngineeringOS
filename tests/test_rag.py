from unittest import TestCase

from engineering_os.knowledge import KnowledgeChunk
from engineering_os.rag import (
    GroundingPolicy,
    GroundingStatus,
    INSUFFICIENT_EVIDENCE,
    RetrievalPolicy,
    answer_question,
    render_response,
)


class FakeRuntime:
    def __init__(
        self,
        query_vector: list[float],
        generated: str = "The authoritative design decision. [Source: knowledge/design.md#Decision]",
    ) -> None:
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


class RAGTests(TestCase):
    def setUp(self) -> None:
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

    def test_grounded_answer_keeps_sources_separate(self) -> None:
        runtime = FakeRuntime([1.0, 0.0])

        response = answer_question(
            self.chunks,
            "What is the design decision?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.5,
        )

        self.assertEqual(
            response.answer,
            "The authoritative design decision. [Source: knowledge/design.md#Decision]",
        )
        self.assertEqual(response.sources, ("knowledge/design.md#Decision",))
        self.assertIn("[Source: knowledge/design.md#Decision]", runtime.prompts[0])
        self.assertEqual(runtime.roles, ["rag"])
        self.assertIn("Sources:\n- knowledge/design.md#Decision", render_response(response))

    def test_insufficient_evidence_does_not_generate(self) -> None:
        runtime = FakeRuntime([0.0, 0.0])

        response = answer_question(
            self.chunks,
            "What is unsupported?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.9,
        )

        self.assertEqual(response.answer, INSUFFICIENT_EVIDENCE)
        self.assertEqual(response.sources, ())
        self.assertEqual(runtime.prompts, [])

    def test_grounding_drops_partial_and_unsupported_claims(self) -> None:
        runtime = FakeRuntime(
            [1.0, 0.0],
            generated=(
                "The authoritative design decision. "
                "[Source: knowledge/design.md#Decision]\n"
                "The authoritative design decision improves security. "
                "[Source: knowledge/design.md#Decision]\n"
                "EngineeringOS provides authentication. "
                "[Source: knowledge/design.md#Decision]"
            ),
        )

        response = answer_question(
            self.chunks,
            "What is the design decision?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.5,
        )

        self.assertEqual(
            [claim.status for claim in response.grounding],
            [
                GroundingStatus.SUPPORTED,
                GroundingStatus.PARTIALLY_SUPPORTED,
                GroundingStatus.UNSUPPORTED,
            ],
        )
        self.assertIn("The authoritative design decision.", response.answer)
        self.assertNotIn("security", response.answer)
        self.assertNotIn("authentication", response.answer)
        self.assertEqual(response.sources, ("knowledge/design.md#Decision",))

    def test_unsupported_core_answer_returns_insufficient_evidence(self) -> None:
        runtime = FakeRuntime(
            [1.0, 0.0],
            generated=(
                "EngineeringOS provides authentication. "
                "[Source: knowledge/design.md#Decision]"
            ),
        )

        response = answer_question(
            self.chunks,
            "What is the design decision?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.5,
        )

        self.assertEqual(response.answer, INSUFFICIENT_EVIDENCE)
        self.assertEqual(response.sources, ())
        self.assertEqual(response.grounding[0].status, GroundingStatus.UNSUPPORTED)

    def test_reference_only_chunk_cannot_ground_a_factual_claim(self) -> None:
        chunks = [
            KnowledgeChunk(
                "knowledge/references.md",
                "References",
                "Ollama local authentication documentation.",
                [1.0, 0.0],
            )
        ]
        runtime = FakeRuntime(
            [1.0, 0.0],
            generated=(
                "EngineeringOS provides authentication. "
                "[Source: knowledge/references.md#References]"
            ),
        )

        response = answer_question(
            chunks,
            "What does EngineeringOS provide?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.5,
        )

        self.assertEqual(response.answer, INSUFFICIENT_EVIDENCE)
        self.assertEqual(response.sources, ())

    def test_confidence_gate_rejects_weak_retrieval_after_filtering(self) -> None:
        runtime = FakeRuntime([1.0, 1.0])

        response = answer_question(
            self.chunks,
            "What is weakly supported?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.45,
            confidence_threshold=0.75,
        )

        self.assertEqual(response.answer, INSUFFICIENT_EVIDENCE)
        self.assertEqual(response.sources, ())
        self.assertEqual(runtime.prompts, [])

    def test_retrieval_policy_reads_explicit_settings(self) -> None:
        policy = RetrievalPolicy.from_settings(
            {
                "knowledge": {
                    "retrieval": {
                        "candidateMinScore": 0.45,
                        "confidenceThreshold": 0.62,
                        "overfetchFactor": 4,
                    }
                }
            }
        )

        self.assertEqual(policy.candidate_min_score, 0.45)
        self.assertEqual(policy.confidence_threshold, 0.62)
        self.assertEqual(policy.overfetch_factor, 4)

    def test_grounding_policy_reads_explicit_settings(self) -> None:
        policy = GroundingPolicy.from_settings(
            {
                "knowledge": {
                    "grounding": {
                        "supportedClaimCoverage": 0.75,
                        "partialClaimCoverage": 0.4,
                        "minSharedTerms": 2,
                    }
                }
            }
        )

        self.assertEqual(policy.supported_claim_coverage, 0.75)
        self.assertEqual(policy.partial_claim_coverage, 0.4)
        self.assertEqual(policy.min_shared_terms, 2)

    def test_memory_is_opt_in_and_cannot_ground_authoritative_claims(self) -> None:
        chunks = [
            KnowledgeChunk(
                "knowledge/design.md",
                "Decision",
                "The authoritative design decision.",
                [1.0, 0.0],
            ),
            KnowledgeChunk(
                "memory/project-context.md",
                "Current Notes",
                "The project currently prefers local AI for private workflows.",
                [1.0, 0.0],
                "memory",
                "2026-09-01",
                "contextual",
            ),
        ]
        runtime = FakeRuntime([1.0, 0.0])

        response = answer_question(
            chunks,
            "What is the design decision?",
            runtime,
            runtime,
            top_k=2,
            min_relevance=0.5,
            include_memory=True,
            memory_max_age_days=90,
        )

        self.assertIn("[Memory: memory/project-context.md#Current Notes", runtime.prompts[0])
        self.assertEqual(response.sources, ("knowledge/design.md#Decision",))

    def test_stale_memory_is_excluded_from_retrieval(self) -> None:
        chunks = [
            KnowledgeChunk(
                "memory/project-context.md",
                "Current Notes",
                "Old project context.",
                [1.0, 0.0],
                "memory",
                "2025-01-01",
                "contextual",
            )
        ]
        runtime = FakeRuntime([1.0, 0.0])

        response = answer_question(
            chunks,
            "What is the project context?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.5,
            include_memory=True,
            memory_max_age_days=90,
        )

        self.assertEqual(response.answer, INSUFFICIENT_EVIDENCE)
        self.assertEqual(runtime.prompts, [])
