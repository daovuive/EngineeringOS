"""Benchmark the existing JSON/BM25/vector index at increasing chunk counts."""

from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import statistics
import sys
from dataclasses import asdict, replace
from pathlib import Path
from time import perf_counter
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import KnowledgeIndexError, load_knowledge_index, search_index
from engineering_os.lexical import bm25_scores, build_lexical_index
from engineering_os.llm import get_embedding_contract
from engineering_os.reranking import DeterministicLocalReranker, RerankConfig
from engineering_os.retrieval import HybridRetrievalConfig, hybrid_search


DEFAULT_SCALES = (1_000, 5_000, 10_000, 25_000)
QUERY = "How should telemetry statusId identity survive retries?"


class StaticEmbeddingRuntime:
    def __init__(self, vector: list[float]) -> None:
        self.vector = vector

    def embed(self, text: str) -> list[float]:
        return self.vector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure JSON index build/load/memory and query stage latency."
    )
    parser.add_argument(
        "--scales",
        default=",".join(str(value) for value in DEFAULT_SCALES),
        help="Comma-separated positive chunk counts.",
    )
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _parse_scales(raw: str) -> tuple[int, ...]:
    try:
        scales = tuple(int(value.strip()) for value in raw.split(",") if value.strip())
    except ValueError as error:
        raise ValueError("scales must be comma-separated integers") from error
    if not scales or any(value < 1 for value in scales):
        raise ValueError("scales must contain positive integers")
    return tuple(sorted(set(scales)))


def _rss_bytes() -> int:
    status = Path("/proc/self/status")
    if not status.exists():
        return 0
    for line in status.read_text(encoding="utf-8").splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) * 1024
    return 0


def _summary(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    p95_index = round((len(ordered) - 1) * 0.95)
    return {
        "min_ms": min(values),
        "p50_ms": statistics.median(values),
        "p95_ms": ordered[p95_index],
        "max_ms": max(values),
    }


def _representative_chunks(source_chunks, count: int):
    templates = source_chunks[: min(len(source_chunks), 256)]
    if not templates:
        raise ValueError("The source index has no chunks.")
    chunks = []
    for number in range(count):
        template = templates[number % len(templates)]
        chunks.append(
            replace(
                template,
                path=f"capacity/{number:06d}/{template.path}",
                document_id=f"capacity-document-{number:06d}",
                chunk_id=f"capacity-chunk-{number:06d}",
                chunk_index=number,
            )
        )
    return chunks


def _write_index(path: Path, chunks, contract: dict[str, Any], lexical) -> None:
    payload = {
        "schemaVersion": "2.0",
        "embedding": dict(contract),
        "chunks": [asdict(chunk) for chunk in chunks],
        "lexical": lexical,
    }
    with path.open("w", encoding="utf-8") as output:
        json.dump(payload, output, separators=(",", ":"))


def benchmark(args: argparse.Namespace) -> dict[str, Any]:
    scales = _parse_scales(args.scales)
    if args.iterations < 1:
        raise ValueError("iterations must be positive")
    paths = ProjectPaths(root=ROOT)
    settings = load_settings(paths)
    contract = get_embedding_contract(load_runtime_config(paths))
    source_path = ROOT / "runtime/index/knowledge.json"
    source = load_knowledge_index(source_path, embedding_contract=contract)
    runtime = StaticEmbeddingRuntime(source.chunks[0].embedding)
    hybrid_config = HybridRetrievalConfig.from_settings(settings)
    rerank_config = RerankConfig.from_settings(settings)
    reranker = DeterministicLocalReranker(rerank_config)
    output_directory = ROOT / "tmp/index-capacity"
    output_directory.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    for scale in scales:
        gc.collect()
        rss_before = _rss_bytes()
        build_started = perf_counter()
        chunks = _representative_chunks(source.chunks, scale)
        lexical = build_lexical_index(chunks)
        build_ms = (perf_counter() - build_started) * 1000
        index_path = output_directory / f"knowledge-{scale}.json"
        write_started = perf_counter()
        _write_index(index_path, chunks, contract, lexical)
        write_ms = (perf_counter() - write_started) * 1000
        file_bytes = index_path.stat().st_size

        del chunks, lexical
        gc.collect()
        rss_preload = _rss_bytes()
        load_started = perf_counter()
        loaded = load_knowledge_index(index_path, embedding_contract=contract)
        load_ms = (perf_counter() - load_started) * 1000
        rss_loaded = _rss_bytes()

        dense_times: list[float] = []
        bm25_times: list[float] = []
        hybrid_times: list[float] = []
        rerank_times: list[float] = []
        for _ in range(args.iterations):
            started = perf_counter()
            search_index(loaded.chunks, QUERY, runtime, limit=20)
            dense_times.append((perf_counter() - started) * 1000)

            started = perf_counter()
            bm25_scores(loaded.chunks, loaded.lexical, QUERY)
            bm25_times.append((perf_counter() - started) * 1000)

            started = perf_counter()
            candidates = hybrid_search(
                loaded.chunks,
                loaded.lexical,
                QUERY,
                runtime,
                limit=rerank_config.candidate_count,
                config=hybrid_config,
            )
            hybrid_times.append((perf_counter() - started) * 1000)

            started = perf_counter()
            reranker.rerank(QUERY, candidates, rerank_config.top_k)
            rerank_times.append((perf_counter() - started) * 1000)

        result = {
            "chunks": scale,
            "file_bytes": file_bytes,
            "synthetic_build_excluding_embeddings_ms": build_ms,
            "json_write_ms": write_ms,
            "json_load_ms": load_ms,
            "rss_before_bytes": rss_before,
            "rss_preload_bytes": rss_preload,
            "rss_loaded_bytes": rss_loaded,
            "rss_load_delta_bytes": max(0, rss_loaded - rss_preload),
            "dense_latency": _summary(dense_times),
            "bm25_latency": _summary(bm25_times),
            "hybrid_latency": _summary(hybrid_times),
            "rerank_latency": _summary(rerank_times),
        }
        results.append(result)
        print(
            f"SCALE {scale}: file={file_bytes / 1024 / 1024:.1f}MiB "
            f"load={load_ms:.1f}ms hybrid_p95={result['hybrid_latency']['p95_ms']:.1f}ms "
            f"rss_delta={result['rss_load_delta_bytes'] / 1024 / 1024:.1f}MiB"
        )
        del loaded
        index_path.unlink()
        gc.collect()

    report = {
        "schemaVersion": "1.0",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "source_chunks": len(source.chunks),
            "source_bytes": source_path.stat().st_size,
            "embedding_dimensions": contract["dimensions"],
            "iterations": args.iterations,
        },
        "method": (
            "Representative source chunks and existing 768-dimension embeddings are "
            "duplicated with unique IDs. Build timing excludes embedding generation; "
            "query timings use a fixed existing vector so they isolate local index cost."
        ),
        "results": results,
    }
    if args.output:
        output = args.output.resolve()
        if not output.is_relative_to((ROOT / "tmp").resolve()):
            raise ValueError("Benchmark output must stay under the repository tmp directory.")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"report={output.relative_to(ROOT)}")
    return report


def main() -> int:
    try:
        benchmark(parse_args())
    except (OSError, ValueError, KnowledgeIndexError) as error:
        print(f"benchmark_error={error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
