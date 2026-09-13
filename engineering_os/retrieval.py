"""Hybrid dense/BM25 retrieval, metadata filtering, and diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Protocol

from engineering_os.knowledge import KnowledgeChunk, cosine_similarity
from engineering_os.lexical import bm25_scores, chunk_key


class RetrievalError(RuntimeError):
    """Raised for invalid hybrid retrieval configuration or filters."""


class EmbeddingRuntime(Protocol):
    def embed(self, text: str) -> list[float]: ...


@dataclass(frozen=True)
class HybridRetrievalConfig:
    dense_enabled: bool = True
    lexical_enabled: bool = True
    candidate_count: int = 30
    dense_weight: float = 0.65
    lexical_weight: float = 0.35
    rrf_k: int = 60
    candidate_min_dense_score: float = 0.45

    @classmethod
    def from_settings(cls, settings: dict[str, Any]) -> "HybridRetrievalConfig":
        knowledge = settings.get("knowledge", {})
        retrieval = knowledge.get("retrieval", {}) if isinstance(knowledge, dict) else {}
        if not isinstance(retrieval, dict):
            raise RetrievalError("knowledge.retrieval must be an object.")
        config = cls(
            dense_enabled=_bool(retrieval, "denseEnabled", True),
            lexical_enabled=_bool(retrieval, "lexicalEnabled", True),
            candidate_count=_positive_int(retrieval, "hybridCandidateCount", 30),
            dense_weight=_weight(retrieval, "denseWeight", 0.65),
            lexical_weight=_weight(retrieval, "lexicalWeight", 0.35),
            rrf_k=_positive_int(retrieval, "rrfK", 60),
            candidate_min_dense_score=_weight(
                retrieval, "candidateMinScore", 0.45
            ),
        )
        if not config.dense_enabled and not config.lexical_enabled:
            raise RetrievalError("At least one retrieval path must be enabled.")
        if config.dense_enabled and config.dense_weight == 0:
            raise RetrievalError("denseWeight must be positive when dense retrieval is enabled.")
        if config.lexical_enabled and config.lexical_weight == 0:
            raise RetrievalError("lexicalWeight must be positive when lexical retrieval is enabled.")
        return config


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: KnowledgeChunk
    dense_score: float | None
    lexical_score: float | None
    hybrid_score: float
    rerank_score: float | None = None
    dense_rank: int | None = None
    lexical_rank: int | None = None
    candidate_rank: int = 0
    final_rank: int = 0
    retrieval_sources: tuple[str, ...] = ()

    @property
    def score(self) -> float:
        return self.rerank_score if self.rerank_score is not None else self.hybrid_score

    @property
    def source(self) -> str:
        return citation_source(self.chunk)


def citation_source(chunk: KnowledgeChunk) -> str:
    if chunk.document_type == "pdf" and chunk.page_start is not None:
        page = str(chunk.page_start)
        if chunk.page_end and chunk.page_end != chunk.page_start:
            page = f"{page}-{chunk.page_end}"
        return f"{chunk.path}#page={page}"
    return f"{chunk.path}#{chunk.heading}"


def hybrid_search(
    chunks: list[KnowledgeChunk],
    lexical_index: dict[str, Any],
    query: str,
    runtime: EmbeddingRuntime,
    *,
    limit: int = 10,
    config: HybridRetrievalConfig | None = None,
    filters: Mapping[str, Any] | None = None,
) -> list[RetrievedChunk]:
    if not query.strip():
        raise RetrievalError("Retrieval query must not be empty.")
    if limit < 1:
        raise RetrievalError("Retrieval limit must be positive.")
    config = config or HybridRetrievalConfig()
    _validate_filters(filters)
    dense_scores: dict[str, float] = {}
    if config.dense_enabled:
        query_vector = runtime.embed(query)
        dense_scores = {
            chunk_key(chunk): cosine_similarity(query_vector, chunk.embedding)
            for chunk in chunks
        }
    lexical_scores = (
        bm25_scores(chunks, lexical_index, query) if config.lexical_enabled else {}
    )
    dense_ranked = sorted(
        (
            (key, score)
            for key, score in dense_scores.items()
            if score >= config.candidate_min_dense_score
        ),
        key=lambda item: (-item[1], item[0]),
    )[: config.candidate_count]
    lexical_ranked = sorted(
        lexical_scores.items(), key=lambda item: (-item[1], item[0])
    )[: config.candidate_count]
    dense_ranks = {key: rank for rank, (key, _) in enumerate(dense_ranked, 1)}
    lexical_ranks = {key: rank for rank, (key, _) in enumerate(lexical_ranked, 1)}
    candidates = set(dense_ranks) | set(lexical_ranks)
    maximum_rrf = (
        (config.dense_weight if config.dense_enabled else 0.0)
        + (config.lexical_weight if config.lexical_enabled else 0.0)
    ) / (config.rrf_k + 1)
    by_key = {chunk_key(chunk): chunk for chunk in chunks}
    fused: list[RetrievedChunk] = []
    for key in candidates:
        chunk = by_key[key]
        if not metadata_matches(chunk, filters):
            continue
        dense_rank = dense_ranks.get(key)
        lexical_rank = lexical_ranks.get(key)
        raw_rrf = 0.0
        sources: list[str] = []
        if dense_rank is not None:
            raw_rrf += config.dense_weight / (config.rrf_k + dense_rank)
            sources.append("dense")
        if lexical_rank is not None:
            raw_rrf += config.lexical_weight / (config.rrf_k + lexical_rank)
            sources.append("bm25")
        fused.append(
            RetrievedChunk(
                chunk=chunk,
                dense_score=dense_scores.get(key),
                lexical_score=lexical_scores.get(key),
                hybrid_score=raw_rrf / maximum_rrf if maximum_rrf else 0.0,
                dense_rank=dense_rank,
                lexical_rank=lexical_rank,
                retrieval_sources=tuple(sources),
            )
        )
    fused.sort(key=lambda item: (-item.hybrid_score, item.source, item.chunk.chunk_index))
    return [
        replace(item, candidate_rank=rank, final_rank=rank)
        for rank, item in enumerate(fused[:limit], 1)
    ]


def metadata_matches(chunk: KnowledgeChunk, filters: Mapping[str, Any] | None) -> bool:
    if not filters:
        return True
    for key, expected in filters.items():
        actual = getattr(chunk, key)
        if key == "tags":
            requested = {expected} if isinstance(expected, str) else set(expected)
            if not requested.issubset(set(actual)):
                return False
        elif isinstance(expected, (list, tuple, set, frozenset)):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def retrieval_diagnostics(candidates: list[RetrievedChunk]) -> list[dict[str, Any]]:
    return [
        {
            "source": item.source,
            "document_id": item.chunk.document_id,
            "chunk_id": item.chunk.chunk_id,
            "dense_score": item.dense_score,
            "bm25_score": item.lexical_score,
            "hybrid_score": item.hybrid_score,
            "rerank_score": item.rerank_score,
            "candidate_rank": item.candidate_rank,
            "final_rank": item.final_rank,
            "retrieval_sources": list(item.retrieval_sources),
        }
        for item in candidates
    ]


def _validate_filters(filters: Mapping[str, Any] | None) -> None:
    if filters is None:
        return
    allowed = {"source_type", "document_type", "project", "language", "tags"}
    unknown = set(filters) - allowed
    if unknown:
        raise RetrievalError(f"Unsupported metadata filters: {', '.join(sorted(unknown))}.")


def _bool(values: dict[str, Any], key: str, default: bool) -> bool:
    value = values.get(key, default)
    if not isinstance(value, bool):
        raise RetrievalError(f"knowledge.retrieval.{key} must be a boolean.")
    return value


def _positive_int(values: dict[str, Any], key: str, default: int) -> int:
    value = values.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise RetrievalError(f"knowledge.retrieval.{key} must be a positive integer.")
    return value


def _weight(values: dict[str, Any], key: str, default: float) -> float:
    value = values.get(key, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise RetrievalError(f"knowledge.retrieval.{key} must be between 0 and 1.")
    return float(value)
