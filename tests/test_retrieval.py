from unittest import TestCase

from engineering_os.knowledge import KnowledgeChunk
from engineering_os.lexical import build_lexical_index, tokenize
from engineering_os.retrieval import (
    HybridRetrievalConfig,
    RetrievalError,
    hybrid_search,
    retrieval_diagnostics,
)


class FakeRuntime:
    def __init__(self, vector: list[float]) -> None:
        self.vector = vector

    def embed(self, text: str) -> list[float]:
        return self.vector


def chunk(
    path: str,
    heading: str,
    text: str,
    embedding: list[float],
    number: int,
    **metadata,
) -> KnowledgeChunk:
    return KnowledgeChunk(
        path,
        heading,
        text,
        embedding,
        heading_path=(heading,),
        document_id=f"doc-{number}",
        chunk_id=f"chunk-{number}",
        chunk_index=number,
        **metadata,
    )


class HybridRetrievalTests(TestCase):
    def setUp(self) -> None:
        self.chunks = [
            chunk(
                "knowledge/requirements.md",
                "Vehicle requirement",
                "REQ-SDV-0012 config candidateMinScore controls the ECU API.",
                [0.2, 0.98],
                1,
                project="eos",
                language="en",
                tags=("sdv", "api"),
            ),
            chunk(
                "knowledge/knowledge.py",
                "Embedding pipeline",
                "Dense semantic retrieval for architecture guidance.",
                [1.0, 0.0],
                2,
                project="eos",
                language="en",
                tags=("python",),
            ),
            chunk(
                "knowledge/other.md",
                "Unrelated",
                "Cooking instructions.",
                [0.0, 1.0],
                3,
                project="other",
                language="vi",
                tags=("food",),
            ),
        ]
        self.lexical = build_lexical_index(self.chunks)

    def test_tokenizer_preserves_technical_identifiers_and_splits_config_keys(self) -> None:
        tokens = tokenize("REQ-SDV-0012 knowledge.py candidateMinScore ECU")
        self.assertIn("req-sdv-0012", tokens)
        self.assertIn("knowledge.py", tokens)
        self.assertIn("candidateminscore", tokens)
        self.assertIn("candidate", tokens)
        self.assertIn("ecu", tokens)

    def test_bm25_recovers_exact_identifier_when_dense_ranking_is_wrong(self) -> None:
        config = HybridRetrievalConfig(
            candidate_count=10,
            dense_weight=0.2,
            lexical_weight=0.8,
            candidate_min_dense_score=0.0,
        )
        results = hybrid_search(
            self.chunks,
            self.lexical,
            "REQ-SDV-0012",
            FakeRuntime([1.0, 0.0]),
            config=config,
        )
        self.assertEqual(results[0].chunk.path, "knowledge/requirements.md")
        self.assertEqual(results[0].retrieval_sources, ("dense", "bm25"))
        self.assertGreater(results[0].lexical_score or 0, 0)

    def test_filename_config_key_and_acronym_are_lexically_searchable(self) -> None:
        lexical_only = HybridRetrievalConfig(
            dense_enabled=False,
            lexical_enabled=True,
            dense_weight=0.0,
            lexical_weight=1.0,
        )
        for query, expected in (
            ("knowledge.py", "knowledge/knowledge.py"),
            ("candidateMinScore", "knowledge/requirements.md"),
            ("ECU", "knowledge/requirements.md"),
        ):
            results = hybrid_search(
                self.chunks,
                self.lexical,
                query,
                FakeRuntime([0.0, 0.0]),
                config=lexical_only,
            )
            self.assertEqual(results[0].chunk.path, expected)

    def test_metadata_filters_apply_after_candidate_fusion(self) -> None:
        filters = {
            "source_type": "knowledge",
            "document_type": "markdown",
            "project": "eos",
            "language": "en",
            "tags": ["sdv", "api"],
        }
        results = hybrid_search(
            self.chunks,
            self.lexical,
            "requirement",
            FakeRuntime([1.0, 0.0]),
            filters=filters,
            config=HybridRetrievalConfig(candidate_min_dense_score=0.0),
        )
        self.assertEqual([item.chunk.chunk_id for item in results], ["chunk-1"])
        with self.assertRaisesRegex(RetrievalError, "Unsupported metadata"):
            hybrid_search(
                self.chunks,
                self.lexical,
                "x",
                FakeRuntime([1.0, 0.0]),
                filters={"unknown": "x"},
            )

    def test_diagnostics_are_deterministic_and_expose_each_stage(self) -> None:
        config = HybridRetrievalConfig(candidate_min_dense_score=0.0)
        first = hybrid_search(
            self.chunks, self.lexical, "architecture", FakeRuntime([1.0, 0.0]), config=config
        )
        second = hybrid_search(
            self.chunks, self.lexical, "architecture", FakeRuntime([1.0, 0.0]), config=config
        )
        self.assertEqual(first, second)
        diagnostics = retrieval_diagnostics(first)
        self.assertIn("dense_score", diagnostics[0])
        self.assertIn("bm25_score", diagnostics[0])
        self.assertIn("hybrid_score", diagnostics[0])
        self.assertIn("candidate_rank", diagnostics[0])
