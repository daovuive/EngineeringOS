from unittest import TestCase

from engineering_os.knowledge import KnowledgeChunk
from engineering_os.reranking import DeterministicLocalReranker, RerankConfig
from engineering_os.retrieval import RetrievedChunk


def candidate(number: int, text: str, *, hybrid: float, dense: float) -> RetrievedChunk:
    chunk = KnowledgeChunk(
        f"knowledge/{number}.md",
        f"Heading {number}",
        text,
        [dense, 0.0],
        heading_path=(f"Heading {number}",),
        document_id=f"doc-{number}",
        chunk_id=f"chunk-{number}",
        chunk_index=number,
        project="eos",
        tags=("test",),
    )
    return RetrievedChunk(
        chunk,
        dense,
        None,
        hybrid,
        candidate_rank=number,
        final_rank=number,
        retrieval_sources=("dense",),
    )


class RerankingTests(TestCase):
    def test_reranker_changes_order_for_stronger_query_alignment(self) -> None:
        candidates = [
            candidate(1, "generic architecture overview", hybrid=1.0, dense=0.9),
            candidate(2, "REQ-SDV-0012 controls vehicle status", hybrid=0.7, dense=0.5),
        ]
        results = DeterministicLocalReranker().rerank(
            "REQ-SDV-0012", candidates, 2
        )
        self.assertEqual(results[0].chunk.chunk_id, "chunk-2")
        self.assertGreater(results[0].rerank_score or 0, results[1].rerank_score or 0)

    def test_metadata_and_citation_survive_reranking(self) -> None:
        original = candidate(1, "exact API", hybrid=0.8, dense=0.7)
        result = DeterministicLocalReranker().rerank("exact API", [original], 1)[0]
        self.assertEqual(result.chunk, original.chunk)
        self.assertEqual(result.source, "knowledge/1.md#Heading 1")
        self.assertEqual(result.chunk.project, "eos")
        self.assertEqual(result.chunk.tags, ("test",))
        self.assertEqual(result.candidate_rank, 1)
        self.assertEqual(result.final_rank, 1)

    def test_disabled_reranker_preserves_deterministic_hybrid_order(self) -> None:
        candidates = [
            candidate(1, "generic", hybrid=0.9, dense=0.9),
            candidate(2, "exact identifier", hybrid=0.8, dense=0.8),
        ]
        reranker = DeterministicLocalReranker(RerankConfig(enabled=False))
        first = reranker.rerank("exact identifier", candidates, 2)
        second = reranker.rerank("exact identifier", candidates, 2)
        self.assertEqual(first, second)
        self.assertEqual([item.chunk.chunk_id for item in first], ["chunk-1", "chunk-2"])
        self.assertTrue(all(item.rerank_score is None for item in first))

    def test_strong_exact_evidence_passes_default_confidence_and_weak_abstains(self) -> None:
        reranker = DeterministicLocalReranker()
        exact = reranker.rerank(
            "REQ-SDV-0012",
            [candidate(1, "REQ-SDV-0012", hybrid=1.0, dense=0.8)],
            1,
        )[0]
        weak = reranker.rerank(
            "REQ-SDV-0012",
            [candidate(2, "unrelated", hybrid=0.4, dense=0.2)],
            1,
        )[0]
        self.assertGreaterEqual(exact.score, 0.62)
        self.assertLess(weak.score, 0.62)
