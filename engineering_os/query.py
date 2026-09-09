"""Reusable application orchestration for grounded knowledge queries."""

from __future__ import annotations

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import KnowledgeIndexError, load_index
from engineering_os.llm import create_runtime, get_embedding_contract
from engineering_os.rag import (
    GroundingPolicy,
    RAGResponse,
    RetrievalPolicy,
    answer_question,
)


def query_knowledge(
    paths: ProjectPaths,
    query: str,
    *,
    limit: int = 3,
    min_score: float | None = None,
    confidence_threshold: float | None = None,
    include_memory: bool = False,
) -> RAGResponse:
    """Answer a query using the configured knowledge index and RAG runtime."""
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
        role="rag",
        grounding_policy=grounding_policy,
        include_memory=include_memory,
        memory_max_age_days=memory_max_age_days,
    )
