"""Reusable application orchestration for grounded knowledge queries."""

from __future__ import annotations

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import KnowledgeIndexError, load_index
from engineering_os.llm import create_runtime, get_embedding_contract
from engineering_os.rag import (
    GroundingPolicy,
    RAGResponse,
    RetrievedContext,
    RetrievalPolicy,
    answer_question,
)


def retrieve_knowledge(
    paths: ProjectPaths,
    query: str,
    *,
    limit: int = 4,
    min_score: float | None = None,
) -> tuple[RetrievedContext, ...]:
    """Retrieve filtered authoritative context without generating an answer."""
    from engineering_os.knowledge import search_index

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
    chunks = load_index(index_path, embedding_contract=embedding_contract)
    threshold = policy.candidate_min_score if min_score is None else min_score
    matches = search_index(
        chunks,
        query,
        runtime,
        limit=max(limit, limit * policy.overfetch_factor),
    )
    filtered = [
        RetrievedContext(score, chunk)
        for score, chunk in matches
        if score >= threshold and chunk.source_type != "memory"
    ]
    if not filtered or filtered[0].score < policy.confidence_threshold:
        return ()
    return tuple(filtered[:limit])


def query_knowledge(
    paths: ProjectPaths,
    query: str,
    *,
    limit: int = 3,
    min_score: float | None = None,
    confidence_threshold: float | None = None,
    include_memory: bool = False,
    role: str = "rag",
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
    chunks = load_index(index_path, embedding_contract=embedding_contract)

    return answer_question(
        chunks,
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
    )
