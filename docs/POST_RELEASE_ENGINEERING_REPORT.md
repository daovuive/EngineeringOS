# Post-release engineering report — 2026-09-13

[Documentation index](README.md) · [Operations](OPERATIONS.md) ·
[Architecture](ARCHITECTURE.md)

## Status and scope

The accepted release remains functionally valid. No release blocker was found.
This report records post-release CI, RAG quality, latency, capacity, host, and
deployment evidence gathered on WSL2 with 12 CPU cores and 23 GiB RAM.

## GitHub Actions

Release commit `350afe9f578b6620e29c46312b2fa388ece5e363` corresponds to remote
run `34766061187`. The workflow runs for every push and pull request on Python
3.12 and requires no secrets. Governance and compilation passed, but the test
job failed because dependencies were never installed and
`scripts/eos-status` was committed as non-executable.

The local fix installs `.[dev]` and records script mode `100755`. Its exact CI
sequence passed in a fresh temporary virtual environment with 138 tests. The
remote status remains red until these changes are committed and pushed; a green
remote run is not claimed by this report.

## Realistic Hybrid RAG evaluation

`tests/evaluation_cases.json` defines 12 cases spanning exact identifiers,
architecture, cross-document synthesis, citations, ambiguity, insufficient
evidence, decision IDs, filenames, unknown errors, long-form questions, vague
input, and terminology variation. Run it with:

```bash
python scripts/evaluate_rag.py \
  --output tmp/post-release-rag-retrieval.json
python scripts/evaluate_rag.py --live \
  --output tmp/post-release-rag-live.json
```

Measured results against 1,732 indexed chunks:

| Metric | Result |
| --- | ---: |
| Cases meeting every expectation | 6/12 |
| Positive-query expected source in top 6 | 87.5% |
| Retrieval confidence behavior | 58.3% |
| Final abstention accuracy | 58.3% |
| Citation correctness | 100% |
| Mean unsupported-claim rate | 2.9% |
| Index load | 0.69 s |
| Retrieval p50 / p95 | 0.53 / 0.64 s |
| Live total p50 / p95 / max | 37.3 / 101.0 / 115.7 s |

Weak cases are intentionally retained rather than tuned away. Current issues
are historical copies outranking the canonical status-identity source, false
acceptance of unsupported revenue and one-word provider questions, poor exact
filename lookup, and weak terminology variation around retry identity. The
long-form case retrieves its expected source but still misses another expected
identifier.

## Streaming and latency

The configured Ollama transport says `stream: true`, but production is not
end-to-end streaming:

```text
Ollama NDJSON
    -> current Ollama client reads the complete response
    -> RAG verifies generated claims
    -> EOS serializes one complete JSON body
    -> Cloudflare / browser
```

`scripts/benchmark_rag_latency.py` uses the real RAG prompt and consumes Ollama
NDJSON directly for observation only. Five query types across two iterations,
with generation capped at 128 tokens, produced:

| Stage | p50 | p95 |
| --- | ---: | ---: |
| Query embedding | 67 ms | 87 ms |
| Hybrid retrieval including embedding | 413 ms | 463 ms |
| Deterministic rerank | 6.2 ms | 7.2 ms |
| Prompt construction | 0.13 ms | 0.18 ms |
| Ollama first non-empty token | 170 ms | 246 ms |
| Ollama stream complete | 6.60 s | 8.22 s |
| Claim grounding | 1.3 ms | 2.7 ms |
| Total | 6.72 s | 8.64 s |

Run the benchmark with:

```bash
python -u scripts/benchmark_rag_latency.py \
  --iterations 2 --max-tokens 128 \
  --output tmp/post-release-rag-latency.json
```

The production API baseline for the exact `TELEMETRY_PROFILE_UPDATE` query was
73.04 seconds to first byte and 73.04 seconds total. The response was 3,737
characters despite the concise-answer prompt. Reducing the configured maximum
from 4,096 to 512 tokens retained `answered` status and one grounded source;
first byte and total both became 27.44 seconds, a 62.4% reduction, and the
answer became 1,796 characters.

The token cap is kept. Raw token forwarding is not implemented because tokens
have not yet passed post-generation claim verification. A future design should
stream explicit progress followed by verified answer events, or define a
revision/retraction protocol, before exposing text incrementally. The protected
Cloudflare route returned HTTP 302 without Access credentials, so authenticated
remote TTFT was not measurable. No proxy streaming claim is made.

## JSON index capacity and vector-store decision

`scripts/benchmark_index_capacity.py` duplicates representative current chunks
and existing 768-dimensional vectors under unique IDs. It measures local index
cost without model/network variance; synthetic build time excludes embedding
generation. Each large temporary scale file is deleted after measurement.

```bash
python -u scripts/benchmark_index_capacity.py \
  --scales 1000,5000,10000,25000 --iterations 3 \
  --output tmp/post-release-index-capacity.json
```

| Chunks | File | Build* | JSON write | Load | RSS load delta | Dense p95 | BM25 p95 | Hybrid p95 | Rerank p95 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1,000 | 12.4 MiB | 0.63 s | 1.29 s | 0.25 s | 31 MiB | 135 ms | 3 ms | 141 ms | 3.5 ms |
| 5,000 | 61.9 MiB | 3.09 s | 6.52 s | 1.41 s | 148 MiB | 672 ms | 16 ms | 711 ms | 1.8 ms |
| 10,000 | 123.9 MiB | 6.27 s | 13.04 s | 2.86 s | 271 MiB | 1.34 s | 40 ms | 1.39 s | 1.9 ms |
| 25,000 | 309.7 MiB | 15.63 s | 32.83 s | 7.19 s | 774 MiB | 3.62 s | 92 ms | 3.70 s | 2.0 ms |

`*` Excludes embedding generation.

Decision: **KEEP_JSON_INDEX**.

The current index has 1,732 chunks, is 36.3 MB, loads below 0.7 seconds, and has
measured live retrieval p95 below 0.64 seconds. A vector database would add
deployment, backup, dependency, and migration cost without solving the dominant
generation latency.

Re-evaluate storage before the corpus approaches 10,000–25,000 chunks, or when
actual repeated measurements breach any of these targets:

- index load exceeds 5 seconds;
- interactive retrieval p95 exceeds 2 seconds;
- index resident memory exceeds 25% of host RAM;
- the persisted file exceeds 1 GiB;
- full rebuild exceeds 30 minutes or incremental updates routinely exceed 30 seconds;
- representative concurrent-query p95 misses the 2-second retrieval target;
- required metadata filters cannot be served without a full scan.

A threshold breach justifies a comparative vector-store evaluation; it does
not automatically authorize a production migration or a new ADR status.

## Host and EOS health

Read-only diagnosis found `ssh.service` failed repeatedly during boot because
port 22 was already in use. At inspection time no process was listening on port
22, so the historical conflicting owner could not be identified. The failure
is unrelated to EngineeringOS and Cloudflare; no SSH/systemd configuration was
changed.

Independent application evidence:

- `engineeringos-web.service`: active with autostart enabled;
- local `/health`: HTTP OK in 4 ms;
- Ollama 0.34.0: reachable with all four configured logical-role models present;
- deep RAG smoke: answered with two sources in 25.4 seconds;
- `cloudflared.service`: active with autostart enabled;
- `eos.dao-labs.org`: reachable through Cloudflare Access, unauthenticated HTTP
  302; observed reachability was 274 ms initially and 1.45 s in the final FAST
  health check.

The host systemd state is degraded, while EOS and its tunnel are healthy.

## Recommendations

1. Commit/push the CI fixes and verify the next GitHub Actions run; do not call
   the release SHA green retroactively.
2. Prioritize ambiguity/insufficient-evidence routing and canonical-source
   preference using the retained evaluation cases.
3. Keep the 512-token ceiling and monitor answer truncation/grounding quality on
   owner-selected questions.
4. Design verified streaming as a separate protocol decision; do not bypass
   claim verification for cosmetic token output.
5. Re-run the capacity benchmark as the real corpus approaches 10,000 chunks.
6. Investigate the boot-time SSH port owner separately only if host operations
   require `ssh.service`; it is not an EOS repair.

No new ADR was introduced: this increment keeps the accepted JSON/Hybrid RAG
architecture and changes only measured runtime policy and verification tools.
