from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import (
    KnowledgeIndexError,
    load_knowledge_index,
    select_retrieval_chunks,
)
from engineering_os.llm import LLMError, create_runtime, get_embedding_contract
from engineering_os.query import retrieve_candidates
from engineering_os.rag import (
    GroundingPolicy,
    GroundingStatus,
    INSUFFICIENT_EVIDENCE,
    RetrievalPolicy,
    answer_question,
)


DEFAULT_CASES = ROOT / "tests/evaluation_cases.json"


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    category: str
    query: str
    expected_sources: tuple[str, ...]
    expected_identifiers: tuple[str, ...]
    expected_abstention: bool
    notes: str


@dataclass(frozen=True)
class CaseResult:
    id: str
    category: str
    query: str
    expected_sources: tuple[str, ...]
    expected_abstention: bool
    retrieved_sources: tuple[str, ...]
    response_sources: tuple[str, ...]
    top_score: float
    retrieval_ms: float
    generation_grounding_ms: float | None
    total_ms: float
    source_hit: bool
    identifier_hit: bool
    confidence_behavior_correct: bool
    abstention_correct: bool | None
    citation_correct: bool | None
    unsupported_claim_rate: float | None
    passed: bool
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the current EngineeringOS Hybrid RAG pipeline."
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Also run generation and post-generation grounding for every case.",
    )
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when a quality expectation is missed.",
    )
    return parser.parse_args()


def load_cases(path: Path) -> tuple[EvaluationCase, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != "1.0" or not isinstance(data.get("cases"), list):
        raise ValueError("Evaluation dataset must use schemaVersion 1.0 and a cases array.")
    cases: list[EvaluationCase] = []
    seen: set[str] = set()
    for raw in data["cases"]:
        if not isinstance(raw, dict):
            raise ValueError("Every evaluation case must be an object.")
        identifier = raw.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Evaluation case IDs must be unique non-empty strings.")
        seen.add(identifier)
        query = raw.get("query")
        category = raw.get("category")
        sources = raw.get("expectedSources", [])
        expected_identifiers = raw.get("expectedIdentifiers", [])
        expected_abstention = raw.get("expectedAbstention")
        notes = raw.get("notes", "")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"Evaluation case {identifier} has no query.")
        if not isinstance(category, str) or not category:
            raise ValueError(f"Evaluation case {identifier} has no category.")
        if not isinstance(sources, list) or not all(isinstance(item, str) for item in sources):
            raise ValueError(f"Evaluation case {identifier} has invalid expectedSources.")
        if not isinstance(expected_identifiers, list) or not all(
            isinstance(item, str) for item in expected_identifiers
        ):
            raise ValueError(f"Evaluation case {identifier} has invalid expectedIdentifiers.")
        if not isinstance(expected_abstention, bool) or not isinstance(notes, str):
            raise ValueError(f"Evaluation case {identifier} has invalid expectations.")
        cases.append(
            EvaluationCase(
                identifier,
                category,
                query.strip(),
                tuple(sources),
                tuple(expected_identifiers),
                expected_abstention,
                notes,
            )
        )
    return tuple(cases)


def _source_paths(sources: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(source.split("#", 1)[0] for source in sources)


def _all_expected_sources_present(
    expected: tuple[str, ...], actual_sources: tuple[str, ...]
) -> bool:
    actual_paths = set(_source_paths(actual_sources))
    return all(source in actual_paths for source in expected)


def _all_identifiers_present(expected: tuple[str, ...], candidates) -> bool:
    if not expected:
        return True
    evidence = "\n".join(
        f"{item.source}\n{item.chunk.heading}\n{item.chunk.text}" for item in candidates
    ).casefold()
    return all(identifier.casefold() in evidence for identifier in expected)


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * percentile)))
    return ordered[index]


def _latency_summary(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "min_ms": min(values) if values else None,
        "p50_ms": statistics.median(values) if values else None,
        "p95_ms": _percentile(values, 0.95),
        "max_ms": max(values) if values else None,
    }


def evaluate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    if args.limit < 1:
        raise ValueError("--limit must be positive.")
    cases = load_cases(args.cases.resolve())
    paths = ProjectPaths(root=ROOT)
    settings = load_settings(paths)
    runtime_config = load_runtime_config(paths)
    runtime = create_runtime(runtime_config)
    contract = get_embedding_contract(runtime_config)

    index_path = ROOT / "runtime/index/knowledge.json"
    load_started = perf_counter()
    index = load_knowledge_index(index_path, embedding_contract=contract)
    index_load_ms = (perf_counter() - load_started) * 1000
    chunks = select_retrieval_chunks(index.chunks)
    retrieval_policy = RetrievalPolicy.from_settings(settings)
    grounding_policy = GroundingPolicy.from_settings(settings)
    results: list[CaseResult] = []

    for case in cases:
        retrieval_started = perf_counter()
        candidates = retrieve_candidates(
            settings,
            chunks,
            index.lexical,
            case.query,
            runtime,
            limit=args.limit,
            min_score=None,
        )
        retrieval_ms = (perf_counter() - retrieval_started) * 1000
        retrieved_sources = tuple(item.source for item in candidates)
        top_score = candidates[0].score if candidates else 0.0
        source_hit = _all_expected_sources_present(
            case.expected_sources, retrieved_sources
        )
        identifier_hit = _all_identifiers_present(
            case.expected_identifiers, candidates
        )
        accepted = bool(candidates) and top_score >= retrieval_policy.confidence_threshold
        confidence_correct = accepted != case.expected_abstention

        response_sources: tuple[str, ...] = ()
        generation_ms: float | None = None
        abstention_correct: bool | None = None
        citation_correct: bool | None = None
        unsupported_rate: float | None = None
        if args.live:
            generation_started = perf_counter()
            response = answer_question(
                index.chunks,
                case.query,
                runtime,
                runtime,
                top_k=args.limit,
                min_relevance=retrieval_policy.candidate_min_score,
                confidence_threshold=retrieval_policy.confidence_threshold,
                overfetch_factor=retrieval_policy.overfetch_factor,
                role="rag",
                grounding_policy=grounding_policy,
                retrieved_candidates=candidates,
            )
            generation_ms = (perf_counter() - generation_started) * 1000
            response_sources = response.sources
            abstained = response.answer == INSUFFICIENT_EVIDENCE
            abstention_correct = abstained == case.expected_abstention
            retrieved_set = set(retrieved_sources)
            citation_correct = (
                not response_sources
                if abstained
                else bool(response_sources)
                and all(source in retrieved_set for source in response_sources)
            )
            unsupported = sum(
                claim.status is GroundingStatus.UNSUPPORTED
                for claim in response.grounding
            )
            unsupported_rate = (
                unsupported / len(response.grounding) if response.grounding else 0.0
            )

        checks = [source_hit, identifier_hit, confidence_correct]
        if args.live:
            checks.extend([bool(abstention_correct), bool(citation_correct)])
        total_ms = retrieval_ms + (generation_ms or 0.0)
        result = CaseResult(
            case.id,
            case.category,
            case.query,
            case.expected_sources,
            case.expected_abstention,
            retrieved_sources,
            response_sources,
            top_score,
            retrieval_ms,
            generation_ms,
            total_ms,
            source_hit,
            identifier_hit,
            confidence_correct,
            abstention_correct,
            citation_correct,
            unsupported_rate,
            all(checks),
            case.notes,
        )
        results.append(result)
        print(
            f"CASE {result.id}: {'PASS' if result.passed else 'WEAK'} "
            f"score={result.top_score:.4f} retrieval={result.retrieval_ms:.1f}ms "
            f"total={result.total_ms:.1f}ms"
        )
        print(f"  retrieved={result.retrieved_sources}")
        if args.live:
            print(
                f"  response_sources={result.response_sources} "
                f"abstention_correct={result.abstention_correct} "
                f"unsupported_rate={result.unsupported_claim_rate:.1%}"
            )

    positive = [result for result in results if not result.expected_abstention]
    abstention = [result for result in results if result.expected_abstention]
    live_results = [result for result in results if result.generation_grounding_ms is not None]
    report: dict[str, Any] = {
        "schemaVersion": "1.0",
        "mode": "live" if args.live else "retrieval-only",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "index_schema": index.schema_version,
            "index_chunks": len(index.chunks),
            "index_bytes": index_path.stat().st_size,
            "embedding_contract": contract,
        },
        "summary": {
            "cases": len(results),
            "passed": sum(result.passed for result in results),
            "weak": sum(not result.passed for result in results),
            "positive_source_hit_rate": (
                sum(result.source_hit for result in positive) / len(positive)
                if positive
                else None
            ),
            "retrieval_confidence_behavior_rate": sum(
                result.confidence_behavior_correct for result in results
            )
            / len(results),
            "final_abstention_accuracy": (
                sum(bool(result.abstention_correct) for result in live_results)
                / len(live_results)
                if live_results
                else None
            ),
            "citation_correctness_rate": (
                sum(bool(result.citation_correct) for result in live_results)
                / len(live_results)
                if live_results
                else None
            ),
            "unsupported_claim_rate": (
                statistics.mean(
                    result.unsupported_claim_rate or 0.0 for result in live_results
                )
                if live_results
                else None
            ),
            "index_load_ms": index_load_ms,
            "retrieval_latency": _latency_summary(
                [result.retrieval_ms for result in results]
            ),
            "generation_grounding_latency": _latency_summary(
                [
                    result.generation_grounding_ms
                    for result in live_results
                    if result.generation_grounding_ms is not None
                ]
            ),
            "total_latency": _latency_summary(
                [result.total_ms for result in live_results]
            ),
            "weak_case_ids": [result.id for result in results if not result.passed],
            "abstention_case_ids": [result.id for result in abstention],
        },
        "results": [asdict(result) for result in results],
    }
    if args.output:
        output = args.output.resolve()
        if not output.is_relative_to((ROOT / "tmp").resolve()):
            raise ValueError("Evaluation output must stay under the repository tmp directory.")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"report={output.relative_to(ROOT)}")
    print(json.dumps(report["summary"], indent=2))
    exit_code = 1 if args.strict and report["summary"]["weak"] else 0
    return report, exit_code


def main() -> int:
    args = parse_args()
    try:
        _, exit_code = evaluate(args)
    except (OSError, ValueError, KnowledgeIndexError, LLMError) as error:
        print(f"evaluation_error={error}", file=sys.stderr)
        return 2
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
