# EngineeringOS Five-Sprint Roadmap

Last verified: 2026-09-13

Status values are `implemented and verified`, `implemented but unverified`,
`partial`, `planned`, or `blocked`. Completion is based on observable behavior,
not the presence of a prompt or document. Detailed acceptance evidence is in
[Product Backlog](PRODUCT_BACKLOG.md).

## Sprint 1 — Foundation and Local CLI

**Status: implemented and verified.** The governed repository structure,
configuration loaders, initialization/synchronization, validation, doctor, and
CLI entry point are implemented. Ollama configuration began in this sprint and
is exercised through the runtime abstraction.

## Sprint 2 — Local AI and Web Access

**Status: implemented and verified.** The Ollama adapter, logical model roles,
CLI chat, loopback-only custom web interface, query API, service diagnostics,
explicit allowlisted command actions, ingestion controls, and protected
Cloudflare deployment are present. The custom interface is the accepted
implementation; Open WebUI is not a remaining requirement.

Running services are environment state, not reproducible deployment
automation. The repository documents diagnostics but does not provision the
host services or Cloudflare Access policy.

## Sprint 3 — Knowledge Base and Grounded RAG

**Status: implemented and verified for the current scale.** Markdown/PDF
discovery, token-aware overlapping chunks, rich metadata, Ollama embeddings,
persisted BM25, dense/BM25 RRF fusion, metadata filters, bounded local
reranking, final-confidence abstention, page-aware citations, claim grounding,
opt-in freshness-filtered memory, Markdown/plain-text/PDF ingestion,
disabled-by-default allowlisted log indexing, deduplication, and atomic
document-level index updates are implemented.

A vector database is conditional future work, not a current defect. The
post-release benchmark retained JSON at the current 1,732-chunk scale and found
the first prospective interactive-limit breach at 25,000 representative
chunks. The evidence and re-evaluation thresholds are recorded in the
[Post-release Engineering Report](POST_RELEASE_ENGINEERING_REPORT.md).

## Sprint 4 — Engineering Workflows

**Status: implemented and verified locally.** Code Review, Requirement Review,
and ADR Assistant are registered workflows available through CLI and web. They
share runtime/retrieval mechanisms, enforce output contracts, treat inputs as
untrusted data, and never modify reviewed files or approve decisions.

Remaining maturation work is evaluation against a broader set of real inputs,
not basic implementation. Synthetic live smoke tests passed for all three
workflows. Buffered response latency ranged from roughly 78 to 127 seconds on
the configured local model.

## Sprint 5 — Solution Architect Workflow

**Status: implemented and verified locally.** The bounded workflow, CLI/web
paths, requirement/ADR reuse, schema-constrained generation, deterministic
Mermaid/stage/ADR assembly, fail-closed citation handling, and deterministic
tests are implemented. Representative live runs with the configured reasoning
model returned validated proposals both with and without optional retrieval.

The result remains a proposal for human review. Broader evaluation and
end-to-end incremental streaming are maturation work; buffered local runs still
take roughly three minutes on the current host.

## Cross-cutting delivery status

GitHub Actions defines governance validation, Python compilation, the
service-independent test suite, and whitespace checks. The accepted release
commit's remote run failed because dependencies were not installed and the
status script lacked executable mode; both fixes pass the exact CI sequence
locally, while a new remote run remains pending commit/push. Live Ollama and
deployed-service smoke checks remain explicit local operations and are not CI
gates.
The ingestion/index consistency, shared CLI/web action, WebUI, and Hybrid RAG
decisions were accepted by the owner on 2026-09-13.

The five-workspace WebUI is implemented without a runtime demo-data mode: every
session reads the real local API and configured runtime. Historical synthetic
screenshots retain visual evidence from implementation. Its architecture ADR
is accepted. Deployed EOS and Cloudflare health were independently verified;
authenticated remote query streaming was not available through Cloudflare
Access. Realistic Hybrid RAG evaluation now exists and its weak cases remain
post-release quality work.
