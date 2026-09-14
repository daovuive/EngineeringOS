"""Repeatable local latency and true Ollama TTFT benchmark for EOS Hybrid RAG."""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import (
    KnowledgeIndexError,
    load_knowledge_index,
    select_retrieval_chunks,
)
from engineering_os.llm import (
    LLMError,
    create_runtime,
    get_default_runtime_definition,
    get_embedding_contract,
)
from engineering_os.rag import GroundingPolicy, RAGError, RetrievalPolicy, answer_question
from engineering_os.reranking import DeterministicLocalReranker, RerankConfig
from engineering_os.retrieval import HybridRetrievalConfig, hybrid_search


DEFAULT_CASES = ROOT / "tests/evaluation_cases.json"
BENCHMARK_CASE_IDS = (
    "exact-technical-identifier",
    "cross-document-asr-boundary",
    "long-form-boundary",
    "ambiguous-status",
    "insufficient-revenue",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure EOS retrieval stages, Ollama TTFT, and grounded total latency."
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


class TimedEmbeddingRuntime:
    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime
        self.last_ms = 0.0

    def embed(self, text: str) -> list[float]:
        started = perf_counter()
        result = self.runtime.embed(text)
        self.last_ms = (perf_counter() - started) * 1000
        return result


@dataclass
class GenerationTiming:
    request_start: float = 0.0
    first_token: float | None = None
    stream_complete: float = 0.0


class StreamingProbeRuntime:
    """Generation adapter that consumes Ollama NDJSON as it arrives."""

    def __init__(self, runtime_config: dict[str, Any], *, max_tokens: int) -> None:
        self.definition = get_default_runtime_definition(runtime_config)
        self.max_tokens = max_tokens
        self.timing = GenerationTiming()

    def generate(self, prompt: str, *, role: str = "rag") -> str:
        options: dict[str, Any] = {"num_predict": self.max_tokens}
        configured = self.definition.options
        if configured.temperature is not None:
            options["temperature"] = configured.temperature
        if configured.top_p is not None:
            options["top_p"] = configured.top_p
        payload = json.dumps(
            {
                "model": self.definition.model_for(role),
                "prompt": prompt,
                "stream": True,
                "options": options,
            }
        ).encode("utf-8")
        request = Request(
            f"{self.definition.provider.host}/api/generate",
            data=payload,
            headers={"Accept": "application/x-ndjson", "Content-Type": "application/json"},
            method="POST",
        )
        output: list[str] = []
        self.timing = GenerationTiming(request_start=perf_counter())
        with urlopen(request, timeout=self.definition.provider.timeout) as response:
            for raw_line in response:
                if not raw_line.strip():
                    continue
                item = json.loads(raw_line)
                token = item.get("response")
                if isinstance(token, str) and token:
                    if self.timing.first_token is None:
                        self.timing.first_token = perf_counter()
                    output.append(token)
        self.timing.stream_complete = perf_counter()
        return "".join(output)


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = round((len(ordered) - 1) * percentile)
    return ordered[max(0, min(len(ordered) - 1, index))]


def _summary(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "min_ms": min(values) if values else None,
        "p50_ms": statistics.median(values) if values else None,
        "p95_ms": _percentile(values, 0.95),
        "max_ms": max(values) if values else None,
    }


def _load_selected_cases(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    by_id = {case["id"]: case for case in payload.get("cases", [])}
    missing = [identifier for identifier in BENCHMARK_CASE_IDS if identifier not in by_id]
    if missing:
        raise ValueError(f"Missing benchmark cases: {', '.join(missing)}")
    return [by_id[identifier] for identifier in BENCHMARK_CASE_IDS]


def benchmark(args: argparse.Namespace) -> dict[str, Any]:
    if args.iterations < 1 or args.limit < 1 or args.max_tokens < 1:
        raise ValueError("iterations, limit, and max-tokens must be positive.")
    paths = ProjectPaths(root=ROOT)
    settings = load_settings(paths)
    runtime_config = load_runtime_config(paths)
    base_runtime = create_runtime(runtime_config)
    contract = get_embedding_contract(runtime_config)
    index_path = ROOT / "runtime/index/knowledge.json"
    load_started = perf_counter()
    index = load_knowledge_index(index_path, embedding_contract=contract)
    index_load_ms = (perf_counter() - load_started) * 1000
    chunks = select_retrieval_chunks(index.chunks)
    hybrid_config = HybridRetrievalConfig.from_settings(settings)
    rerank_config = RerankConfig.from_settings(settings)
    retrieval_policy = RetrievalPolicy.from_settings(settings)
    grounding_policy = GroundingPolicy.from_settings(settings)
    cases = _load_selected_cases(args.cases.resolve())
    samples: list[dict[str, Any]] = []

    for iteration in range(1, args.iterations + 1):
        for case in cases:
            sample_started = perf_counter()
            timed_runtime = TimedEmbeddingRuntime(base_runtime)
            hybrid_started = perf_counter()
            hybrid = hybrid_search(
                chunks,
                index.lexical,
                case["query"],
                timed_runtime,
                limit=max(args.limit, rerank_config.candidate_count),
                config=hybrid_config,
            )
            hybrid_complete = perf_counter()
            rerank_started = perf_counter()
            candidates = DeterministicLocalReranker(rerank_config).rerank(
                case["query"], hybrid, min(args.limit, rerank_config.top_k)
            )
            rerank_complete = perf_counter()
            accepted = bool(candidates) and (
                candidates[0].score >= retrieval_policy.confidence_threshold
            )
            prompt_ms: float | None = None
            ttft_ms: float | None = None
            stream_ms: float | None = None
            grounding_ms: float | None = None
            answer_status = "insufficient_evidence"
            if accepted:
                generation = StreamingProbeRuntime(
                    runtime_config, max_tokens=args.max_tokens
                )
                answer_started = perf_counter()
                response = answer_question(
                    index.chunks,
                    case["query"],
                    timed_runtime,
                    generation,
                    top_k=args.limit,
                    min_relevance=retrieval_policy.candidate_min_score,
                    confidence_threshold=retrieval_policy.confidence_threshold,
                    overfetch_factor=retrieval_policy.overfetch_factor,
                    role="rag",
                    grounding_policy=grounding_policy,
                    retrieved_candidates=candidates,
                )
                answer_complete = perf_counter()
                timing = generation.timing
                prompt_ms = (timing.request_start - answer_started) * 1000
                if timing.first_token is not None:
                    ttft_ms = (timing.first_token - timing.request_start) * 1000
                stream_ms = (timing.stream_complete - timing.request_start) * 1000
                grounding_ms = (answer_complete - timing.stream_complete) * 1000
                if response.sources:
                    answer_status = "answered"
            total_ms = (perf_counter() - sample_started) * 1000
            sample = {
                "iteration": iteration,
                "case_id": case["id"],
                "category": case["category"],
                "accepted_for_generation": accepted,
                "answer_status": answer_status,
                "embedding_ms": timed_runtime.last_ms,
                "hybrid_total_ms": (hybrid_complete - hybrid_started) * 1000,
                "hybrid_after_embedding_ms": max(
                    0.0,
                    (hybrid_complete - hybrid_started) * 1000 - timed_runtime.last_ms,
                ),
                "rerank_ms": (rerank_complete - rerank_started) * 1000,
                "prompt_construction_ms": prompt_ms,
                "ollama_ttft_ms": ttft_ms,
                "ollama_stream_complete_ms": stream_ms,
                "grounding_ms": grounding_ms,
                "total_ms": total_ms,
            }
            samples.append(sample)
            print(
                f"SAMPLE {iteration}/{case['id']}: total={total_ms:.1f}ms "
                f"ttft={ttft_ms if ttft_ms is not None else 'n/a'}"
            )

    metrics = {
        key: _summary([float(sample[key]) for sample in samples if sample[key] is not None])
        for key in (
            "embedding_ms",
            "hybrid_total_ms",
            "hybrid_after_embedding_ms",
            "rerank_ms",
            "prompt_construction_ms",
            "ollama_ttft_ms",
            "ollama_stream_complete_ms",
            "grounding_ms",
            "total_ms",
        )
    }
    report = {
        "schemaVersion": "1.0",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "index_chunks": len(index.chunks),
            "index_bytes": index_path.stat().st_size,
            "index_load_ms": index_load_ms,
            "model": get_default_runtime_definition(runtime_config).model_for("rag"),
            "max_tokens": args.max_tokens,
        },
        "sample_count": len(samples),
        "metrics": metrics,
        "samples": samples,
        "streaming_boundary": (
            "ollama_ttft_ms is the first non-empty Ollama NDJSON token. The current "
            "EOS HTTP API sends one JSON body only after generation and grounding, so "
            "browser-visible first byte cannot precede total backend processing."
        ),
    }
    if args.output:
        output = args.output.resolve()
        if not output.is_relative_to((ROOT / "tmp").resolve()):
            raise ValueError("Benchmark output must stay under the repository tmp directory.")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"report={output.relative_to(ROOT)}")
    print(json.dumps(metrics, indent=2))
    return report


def main() -> int:
    try:
        benchmark(parse_args())
    except (OSError, ValueError, KnowledgeIndexError, LLMError, RAGError) as error:
        print(f"benchmark_error={error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
