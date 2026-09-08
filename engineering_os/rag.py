from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Protocol

from engineering_os.knowledge import (
    KnowledgeChunk,
    MEMORY_SOURCE,
    search_index,
    select_retrieval_chunks,
)


DEFAULT_MIN_RELEVANCE = 0.45
DEFAULT_CONFIDENCE_THRESHOLD = 0.62
DEFAULT_OVERFETCH_FACTOR = 4
DEFAULT_SUPPORTED_CLAIM_COVERAGE = 0.75
DEFAULT_PARTIAL_CLAIM_COVERAGE = 0.40
DEFAULT_MIN_SHARED_TERMS = 2
INSUFFICIENT_EVIDENCE = "Insufficient evidence in EngineeringOS knowledge."

_SOURCE_PATTERN = re.compile(r"\[Source:\s*([^\]]+)\]")
_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+(?!\[Source:)")
_TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]*")
_GROUNDING_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "because",
        "by",
        "can",
        "could",
        "does",
        "engineeringos",
        "for",
        "from",
        "how",
        "in",
        "into",
        "instead",
        "is",
        "it",
        "its",
        "may",
        "more",
        "not",
        "of",
        "on",
        "or",
        "rather",
        "refers",
        "represents",
        "should",
        "signifies",
        "system",
        "that",
        "the",
        "than",
        "their",
        "them",
        "these",
        "this",
        "through",
        "to",
        "use",
        "used",
        "using",
        "what",
        "when",
        "which",
        "while",
        "with",
        "would",
    }
)
_GROUNDING_ALIASES = {
    "dictates": "determine",
    "determines": "determine",
    "determining": "determine",
    "independence": "independent",
    "independently": "independent",
    "directly": "direct",
    "depending": "depend",
    "maintaining": "maintain",
    "maintains": "maintain",
    "maintained": "maintain",
    "operating": "operate",
    "operates": "operate",
}


class RAGError(RuntimeError):
    """Raised when a grounded answer cannot be assembled."""


class GroundingStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class GroundingPolicy:
    supported_claim_coverage: float = DEFAULT_SUPPORTED_CLAIM_COVERAGE
    partial_claim_coverage: float = DEFAULT_PARTIAL_CLAIM_COVERAGE
    min_shared_terms: int = DEFAULT_MIN_SHARED_TERMS

    @classmethod
    def from_settings(cls, settings: dict[str, object]) -> "GroundingPolicy":
        knowledge = settings.get("knowledge", {})
        if not isinstance(knowledge, dict):
            raise RAGError("Settings 'knowledge' must be an object.")
        grounding = knowledge.get("grounding", {})
        if not isinstance(grounding, dict):
            raise RAGError("Settings 'knowledge.grounding' must be an object.")

        supported_claim_coverage = grounding.get(
            "supportedClaimCoverage", DEFAULT_SUPPORTED_CLAIM_COVERAGE
        )
        partial_claim_coverage = grounding.get(
            "partialClaimCoverage", DEFAULT_PARTIAL_CLAIM_COVERAGE
        )
        min_shared_terms = grounding.get("minSharedTerms", DEFAULT_MIN_SHARED_TERMS)
        if (
            not isinstance(supported_claim_coverage, int | float)
            or isinstance(supported_claim_coverage, bool)
            or not 0.0 <= supported_claim_coverage <= 1.0
        ):
            raise RAGError("supportedClaimCoverage must be a number between 0 and 1.")
        if (
            not isinstance(partial_claim_coverage, int | float)
            or isinstance(partial_claim_coverage, bool)
            or not 0.0 <= partial_claim_coverage <= 1.0
        ):
            raise RAGError("partialClaimCoverage must be a number between 0 and 1.")
        if partial_claim_coverage >= supported_claim_coverage:
            raise RAGError(
                "partialClaimCoverage must be lower than supportedClaimCoverage."
            )
        if (
            not isinstance(min_shared_terms, int)
            or isinstance(min_shared_terms, bool)
            or min_shared_terms < 1
        ):
            raise RAGError("minSharedTerms must be a positive integer.")
        return cls(
            supported_claim_coverage=float(supported_claim_coverage),
            partial_claim_coverage=float(partial_claim_coverage),
            min_shared_terms=min_shared_terms,
        )


@dataclass(frozen=True)
class RetrievalPolicy:
    candidate_min_score: float = DEFAULT_MIN_RELEVANCE
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    overfetch_factor: int = DEFAULT_OVERFETCH_FACTOR

    @classmethod
    def from_settings(cls, settings: dict[str, object]) -> "RetrievalPolicy":
        knowledge = settings.get("knowledge", {})
        if not isinstance(knowledge, dict):
            raise RAGError("Settings 'knowledge' must be an object.")
        retrieval = knowledge.get("retrieval", {})
        if not isinstance(retrieval, dict):
            raise RAGError("Settings 'knowledge.retrieval' must be an object.")

        candidate_min_score = retrieval.get(
            "candidateMinScore", DEFAULT_MIN_RELEVANCE
        )
        confidence_threshold = retrieval.get(
            "confidenceThreshold", DEFAULT_CONFIDENCE_THRESHOLD
        )
        overfetch_factor = retrieval.get("overfetchFactor", DEFAULT_OVERFETCH_FACTOR)
        if (
            not isinstance(candidate_min_score, int | float)
            or isinstance(candidate_min_score, bool)
            or not 0.0 <= candidate_min_score <= 1.0
        ):
            raise RAGError("candidateMinScore must be a number between 0 and 1.")
        if (
            not isinstance(confidence_threshold, int | float)
            or isinstance(confidence_threshold, bool)
            or not 0.0 <= confidence_threshold <= 1.0
        ):
            raise RAGError("confidenceThreshold must be a number between 0 and 1.")
        if (
            not isinstance(overfetch_factor, int)
            or isinstance(overfetch_factor, bool)
            or overfetch_factor < 1
        ):
            raise RAGError("overfetchFactor must be a positive integer.")
        return cls(
            candidate_min_score=float(candidate_min_score),
            confidence_threshold=float(confidence_threshold),
            overfetch_factor=overfetch_factor,
        )


class RetrievalRuntime(Protocol):
    def embed(self, text: str) -> list[float]:
        """Create an embedding for a retrieval query."""


class GenerationRuntime(Protocol):
    def generate(self, prompt: str, *, role: str = "rag") -> str:
        """Generate an answer from retrieved context."""


@dataclass(frozen=True)
class RetrievedContext:
    score: float
    chunk: KnowledgeChunk

    @property
    def source(self) -> str:
        return f"{self.chunk.path}#{self.chunk.heading}"


@dataclass(frozen=True)
class ClaimGrounding:
    claim: str
    status: GroundingStatus
    sources: tuple[str, ...]
    support_score: float


@dataclass(frozen=True)
class RAGResponse:
    answer: str
    sources: tuple[str, ...]
    retrieved: tuple[RetrievedContext, ...]
    grounding: tuple[ClaimGrounding, ...] = ()


def _claim_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in _TOKEN_PATTERN.findall(text.lower()):
        if token in _GROUNDING_STOPWORDS or len(token) <= 1:
            continue
        tokens.add(_GROUNDING_ALIASES.get(token, token))
    return tokens


def _split_claims(answer: str) -> tuple[str, ...]:
    claims: list[str] = []
    for line in answer.splitlines():
        claim_line = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        if not claim_line or claim_line.lower() in {"answer:", "sources:"}:
            continue
        if claim_line.startswith("[Source:") and claim_line.endswith("]"):
            continue
        claims.extend(
            sentence.strip()
            for sentence in _SENTENCE_PATTERN.split(claim_line)
            if sentence.strip()
        )
    return tuple(claims)


def _citation_sources(claim: str) -> tuple[str, ...]:
    sources: list[str] = []
    for citation in _SOURCE_PATTERN.findall(claim):
        for source in re.split(r"\s*(?:,|;)\s*", citation):
            source = source.strip()
            if source and source not in sources:
                sources.append(source)
    return tuple(sources)


def _claim_text(claim: str) -> str:
    return _SOURCE_PATTERN.sub("", claim).strip()


def _is_reference_source(source: str) -> bool:
    return source.rsplit("#", 1)[-1].strip().lower() in {
        "reference",
        "references",
    }


def _coverage(claim: str, evidence: str) -> tuple[float, int]:
    claim_terms = _claim_tokens(claim)
    if not claim_terms:
        return 0.0, 0
    shared_terms = len(claim_terms & _claim_tokens(evidence))
    return shared_terms / len(claim_terms), shared_terms


def _classify_claim(
    claim: str,
    sources: tuple[str, ...],
    evidence: dict[str, str],
    policy: GroundingPolicy,
) -> tuple[GroundingStatus, float]:
    combined_evidence = "\n".join(evidence[source] for source in sources)
    support_score, shared_terms = _coverage(claim, combined_evidence)
    if shared_terms < policy.min_shared_terms:
        status = GroundingStatus.UNSUPPORTED
    elif support_score >= policy.supported_claim_coverage:
        status = GroundingStatus.SUPPORTED
    elif support_score >= policy.partial_claim_coverage:
        status = GroundingStatus.PARTIALLY_SUPPORTED
    else:
        status = GroundingStatus.UNSUPPORTED
    return status, support_score


def verify_claims(
    answer: str,
    retrieved: tuple[RetrievedContext, ...],
    *,
    policy: GroundingPolicy | None = None,
) -> tuple[ClaimGrounding, ...]:
    """Classify atomic generated claims against retrieved evidence chunks."""
    policy = policy or GroundingPolicy()
    evidence = {
        item.source: f"{item.chunk.heading}\n{item.chunk.text}"
        for item in retrieved
        if item.chunk.source_type != MEMORY_SOURCE
        and not _is_reference_source(item.source)
    }
    results: list[ClaimGrounding] = []

    for raw_claim in _split_claims(answer):
        claim = _claim_text(raw_claim)
        cited_sources = _citation_sources(raw_claim)
        if cited_sources:
            candidate_sources = tuple(
                source for source in cited_sources if source in evidence
            )
        else:
            candidate_sources = ()

        ranked_sources = sorted(
            evidence,
            key=lambda source: _coverage(claim, evidence[source]),
            reverse=True,
        )
        if not candidate_sources:
            candidate_sources = tuple(ranked_sources[:1])

        if not candidate_sources:
            results.append(
                ClaimGrounding(claim, GroundingStatus.UNSUPPORTED, (), 0.0)
            )
            continue

        status, support_score = _classify_claim(
            claim, candidate_sources, evidence, policy
        )
        if status is not GroundingStatus.SUPPORTED and ranked_sources:
            best_source = ranked_sources[0]
            best_sources = (best_source,)
            best_status, best_score = _classify_claim(
                claim, best_sources, evidence, policy
            )
            if best_score > support_score:
                candidate_sources = best_sources
                status = best_status
                support_score = best_score
        results.append(
            ClaimGrounding(claim, status, candidate_sources, support_score)
        )

    return tuple(results)


def _render_grounded_claim(claim: ClaimGrounding) -> str:
    citations = " ".join(f"[Source: {source}]" for source in claim.sources)
    return f"{claim.claim} {citations}".strip()


def answer_question(
    chunks: list[KnowledgeChunk],
    query: str,
    retrieval_runtime: RetrievalRuntime,
    generation_runtime: GenerationRuntime,
    *,
    top_k: int = 3,
    min_relevance: float = DEFAULT_MIN_RELEVANCE,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    overfetch_factor: int = DEFAULT_OVERFETCH_FACTOR,
    role: str = "rag",
    grounding_policy: GroundingPolicy | None = None,
    include_memory: bool = False,
    memory_max_age_days: int = 90,
) -> RAGResponse:
    if not query.strip():
        raise RAGError("RAG query must not be empty.")
    if top_k < 1:
        raise RAGError("RAG top_k must be positive.")
    if not 0.0 <= min_relevance <= 1.0:
        raise RAGError("RAG min_relevance must be between 0 and 1.")
    if not 0.0 <= confidence_threshold <= 1.0:
        raise RAGError("RAG confidence_threshold must be between 0 and 1.")
    if overfetch_factor < 1:
        raise RAGError("RAG overfetch_factor must be positive.")

    retrieval_chunks = select_retrieval_chunks(
        chunks,
        include_memory=include_memory,
        memory_max_age_days=memory_max_age_days,
    )
    retrieval_limit = max(top_k, top_k * overfetch_factor)
    matches = search_index(
        retrieval_chunks, query, retrieval_runtime, limit=retrieval_limit
    )
    relevant_matches = [
        (score, chunk)
        for score, chunk in matches
        if score >= min_relevance
    ]
    relevant_matches.sort(key=lambda item: item[0], reverse=True)
    retrieved = tuple(
        RetrievedContext(score, chunk)
        for score, chunk in relevant_matches[:top_k]
    )
    if not retrieved or retrieved[0].score < confidence_threshold:
        return RAGResponse(INSUFFICIENT_EVIDENCE, (), ())

    context_blocks = []
    for item in retrieved:
        if item.chunk.source_type == MEMORY_SOURCE:
            updated = item.chunk.last_updated or "unknown"
            context_blocks.append(
                f"[Memory: {item.source}; last updated: {updated}]\n{item.chunk.text}"
            )
        else:
            context_blocks.append(f"[Source: {item.source}]\n{item.chunk.text}")
    context = "\n\n".join(context_blocks)
    prompt = (
        "Answer the question using only the EngineeringOS knowledge supplied "
        "below. Return atomic factual claims as separate sentences. "
        "Append one or more inline citations in the exact form "
        "[Source: path#heading] to every factual claim, using only the supplied "
        "source identifiers. Do not invent unsupported EngineeringOS-specific "
        "facts. Do not add plausible implications about security, scalability, "
        "authentication, reliability, or implementation details unless the "
        "evidence states them directly. Keep general suggestions clearly labeled "
        "as suggestions and do not present them as EngineeringOS facts. "
        "If a factual claim is not directly supported, omit it. Do not output a "
        "separate bibliography; keep citations close to claims. "
        "Memory blocks are contextual project notes, not authoritative technical "
        "knowledge or verified career evidence. Use them only to clarify context "
        "or focus the answer; memory-only claims must not be presented as facts "
        "or cited as authoritative sources. "
        "If the sources do not support an answer, say exactly: "
        f"{INSUFFICIENT_EVIDENCE}\n"
        "Keep the answer concise.\n\n"
        f"Question:\n{query.strip()}\n\n"
        f"Retrieved knowledge:\n{context}"
    )
    answer = generation_runtime.generate(prompt, role=role).strip()
    if not answer:
        raise RAGError("RAG generation returned empty text.")

    grounding = verify_claims(answer, retrieved, policy=grounding_policy)
    supported_claims = tuple(
        claim
        for claim in grounding
        if claim.status is GroundingStatus.SUPPORTED
    )
    if not supported_claims:
        return RAGResponse(INSUFFICIENT_EVIDENCE, (), (), grounding)

    grounded_answer = "\n".join(
        _render_grounded_claim(claim) for claim in supported_claims
    )
    sources = tuple(
        dict.fromkeys(source for claim in supported_claims for source in claim.sources)
    )
    grounded_retrieved = tuple(
        item for item in retrieved if item.source in sources
    )
    return RAGResponse(grounded_answer, sources, grounded_retrieved, grounding)


def render_response(response: RAGResponse) -> str:
    if not response.sources:
        return response.answer
    source_lines = "\n".join(f"- {source}" for source in response.sources)
    return f"{response.answer}\n\nSources:\n{source_lines}"
