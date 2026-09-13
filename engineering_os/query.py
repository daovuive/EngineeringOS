"""Reusable application orchestration for grounded knowledge queries."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import (
    KnowledgeIndexError,
    load_knowledge_index,
    select_retrieval_chunks,
)
from engineering_os.llm import create_runtime, get_embedding_contract
from engineering_os.rag import (
    GroundingPolicy,
    RAGResponse,
    RetrievedContext,
    RetrievalPolicy,
    answer_question,
)
from engineering_os.reranking import DeterministicLocalReranker, RerankConfig
from engineering_os.retrieval import (
    HybridRetrievalConfig,
    hybrid_search,
    retrieval_diagnostics,
)


def retrieve_candidates(
    settings: dict[str, Any],
    chunks,
    lexical,
    query: str,
    runtime,
    *,
    limit: int,
    min_score: float | None,
    filters: Mapping[str, Any] | None = None,
):
    """Run hybrid candidate generation and bounded local reranking."""
    retrieval_config = HybridRetrievalConfig.from_settings(settings)
    if min_score is not None:
        retrieval_config = replace(
            retrieval_config, candidate_min_dense_score=min_score
        )
    rerank_config = RerankConfig.from_settings(settings)
    shortlist_limit = max(limit, rerank_config.candidate_count)
    candidates = hybrid_search(
        chunks,
        lexical,
        query,
        runtime,
        limit=shortlist_limit,
        config=retrieval_config,
        filters=filters,
    )
    return DeterministicLocalReranker(rerank_config).rerank(
        query, candidates, min(limit, rerank_config.top_k)
    )


def retrieve_knowledge(
    paths: ProjectPaths,
    query: str,
    *,
    limit: int = 4,
    min_score: float | None = None,
    filters: Mapping[str, Any] | None = None,
) -> tuple[RetrievedContext, ...]:
    """Retrieve filtered authoritative context without generating an answer."""
    if not query.strip():
        raise KnowledgeIndexError("Knowledge query must not be empty.")
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    index_path = paths.resolve(
        knowledge.get("index", "runtime/index/knowledge.json")
    )
    runtime_config = load_runtime_config(paths)
    runtime = create_runtime(runtime_config)
    embedding_contract = get_embedding_contract(runtime_config)
    policy = RetrievalPolicy.from_settings(settings)
    index = load_knowledge_index(index_path, embedding_contract=embedding_contract)
    chunks = select_retrieval_chunks(index.chunks)
    candidates = retrieve_candidates(
        settings,
        chunks,
        index.lexical,
        query,
        runtime,
        limit=limit,
        min_score=min_score,
        filters=filters,
    )
    if not candidates or candidates[0].score < policy.confidence_threshold:
        return ()
    return tuple(RetrievedContext.from_candidate(item) for item in candidates)


def query_knowledge(
    paths: ProjectPaths,
    query: str,
    *,
    limit: int = 3,
    min_score: float | None = None,
    confidence_threshold: float | None = None,
    include_memory: bool = False,
    role: str = "rag",
    filters: Mapping[str, Any] | None = None,
    debug: bool = False,
) -> RAGResponse:
    """Answer a query using the configured knowledge index and RAG runtime."""
    if role not in {"rag", "reasoning"}:
        raise KnowledgeIndexError("Knowledge answers require the rag or reasoning role.")
    settings = load_settings(paths)
    knowledge = settings.get("knowledge", {})
    index_path = paths.resolve(
        knowledge.get("index", "runtime/index/knowledge.json")
    )
    memory = settings.get("memory", {})
    memory_retrieval = memory.get("retrieval", {})
    memory_max_age_days = memory_retrieval.get("maxAgeDays", 90)
    if not isinstance(memory_max_age_days, int) or isinstance(
        memory_max_age_days, bool
    ):
        raise KnowledgeIndexError("memory.retrieval.maxAgeDays must be an integer.")

    runtime_config = load_runtime_config(paths)
    runtime = create_runtime(runtime_config)
    embedding_contract = get_embedding_contract(runtime_config)
    retrieval_policy = RetrievalPolicy.from_settings(settings)
    grounding_policy = GroundingPolicy.from_settings(settings)
    index = load_knowledge_index(index_path, embedding_contract=embedding_contract)
    selected_chunks = select_retrieval_chunks(
        index.chunks,
        include_memory=include_memory,
        memory_max_age_days=memory_max_age_days,
    )
    candidates = retrieve_candidates(
        settings,
        selected_chunks,
        index.lexical,
        query,
        runtime,
        limit=limit,
        min_score=min_score,
        filters=filters,
    )

    response = answer_question(
        index.chunks,
        query,
        runtime,
        runtime,
        top_k=limit,
        min_relevance=(
            retrieval_policy.candidate_min_score if min_score is None else min_score
        ),
        confidence_threshold=(
            retrieval_policy.confidence_threshold
            if confidence_threshold is None
            else confidence_threshold
        ),
        overfetch_factor=retrieval_policy.overfetch_factor,
        role=role,
        grounding_policy=grounding_policy,
        include_memory=include_memory,
        memory_max_age_days=memory_max_age_days,
        retrieved_candidates=candidates,
    )
    if not debug:
        return response
    decision = "pass" if candidates and candidates[0].score >= (
        retrieval_policy.confidence_threshold
        if confidence_threshold is None
        else confidence_threshold
    ) else "abstain"
    reason = None if decision == "pass" else (
        "no eligible candidates" if not candidates else "final evidence quality below confidence threshold"
    )
    return replace(
        response,
        diagnostics={
            "query": query,
            "filters": dict(filters or {}),
            "candidates": retrieval_diagnostics(candidates),
            "confidence_decision": decision,
            "abstention_reason": reason,
        },
    )
