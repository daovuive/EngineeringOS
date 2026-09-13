"""Replaceable, deterministic local reranking for hybrid candidates."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Protocol

from engineering_os.lexical import lexical_text, tokenize
from engineering_os.retrieval import RetrievedChunk


class RerankingError(RuntimeError):
    """Raised when reranking configuration is invalid."""


class Reranker(Protocol):
    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]: ...


@dataclass(frozen=True)
class RerankConfig:
    enabled: bool = True
    candidate_count: int = 20
    top_k: int = 6
    hybrid_weight: float = 0.20
    dense_weight: float = 0.25
    lexical_alignment_weight: float = 0.55

    @classmethod
    def from_settings(cls, settings: dict[str, Any]) -> "RerankConfig":
        knowledge = settings.get("knowledge", {})
        values = knowledge.get("rerank", {}) if isinstance(knowledge, dict) else {}
        if not isinstance(values, dict):
            raise RerankingError("knowledge.rerank must be an object.")
        config = cls(
            enabled=_bool(values, "enabled", True),
            candidate_count=_positive_int(values, "candidateCount", 20),
            top_k=_positive_int(values, "topK", 6),
            hybrid_weight=_weight(values, "hybridWeight", 0.20),
            dense_weight=_weight(values, "denseWeight", 0.25),
            lexical_alignment_weight=_weight(
                values, "lexicalAlignmentWeight", 0.55
            ),
        )
        total = (
            config.hybrid_weight
            + config.dense_weight
            + config.lexical_alignment_weight
        )
        if abs(total - 1.0) > 1e-9:
            raise RerankingError("Rerank scoring weights must sum to 1.0.")
        return config


@dataclass(frozen=True)
class DeterministicLocalReranker:
    """Rerank by final evidence quality without another model dependency."""

    config: RerankConfig = RerankConfig()

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        if top_k < 1:
            raise RerankingError("Reranker top_k must be positive.")
        shortlist = candidates[: self.config.candidate_count]
        if not self.config.enabled:
            return [
                replace(item, final_rank=rank)
                for rank, item in enumerate(shortlist[:top_k], 1)
            ]

        scored = [
            replace(item, rerank_score=self._score(query, item))
            for item in shortlist
        ]
        scored.sort(
            key=lambda item: (
                -(item.rerank_score or 0.0),
                -item.hybrid_score,
                item.source,
                item.chunk.chunk_index,
            )
        )
        return [
            replace(item, final_rank=rank)
            for rank, item in enumerate(scored[:top_k], 1)
        ]

    def _score(self, query: str, candidate: RetrievedChunk) -> float:
        query_terms = set(tokenize(query))
        evidence_terms = set(tokenize(lexical_text(candidate.chunk)))
        alignment = (
            len(query_terms & evidence_terms) / len(query_terms)
            if query_terms
            else 0.0
        )
        dense = max(0.0, min(1.0, candidate.dense_score or 0.0))
        score = (
            self.config.lexical_alignment_weight * alignment
            + self.config.dense_weight * dense
            + self.config.hybrid_weight * candidate.hybrid_score
        )
        return max(0.0, min(1.0, score))


def _bool(values: dict[str, Any], key: str, default: bool) -> bool:
    value = values.get(key, default)
    if not isinstance(value, bool):
        raise RerankingError(f"knowledge.rerank.{key} must be a boolean.")
    return value


def _positive_int(values: dict[str, Any], key: str, default: int) -> int:
    value = values.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise RerankingError(f"knowledge.rerank.{key} must be a positive integer.")
    return value


def _weight(values: dict[str, Any], key: str, default: float) -> float:
    value = values.get(key, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise RerankingError(f"knowledge.rerank.{key} must be between 0 and 1.")
    return float(value)
