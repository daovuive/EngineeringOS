# EngineeringOS RAG Upgrade Resume

Last updated: 2026-09-14T08:43:26+07:00

## Task

Upgrade EngineeringOS from dense-only grounded RAG to Hybrid RAG without
rewriting the working subsystem. Preserve local-first Ollama integration,
atomic JSON persistence, confidence abstention, citations, and post-generation
claim verification.

## Current Phase

Phase 7 — Documentation, final regression, governance, and approval complete.

## Overall Status

COMPLETE

## Post-release work state

### Current phase

Phase 7 — Post-release inspection, implementation, documentation, local
verification, commit/push, and remote CI verification complete. The accepted
release remains valid.

### Completed work

- Reconciled the clean `agent/python-cli-sdv-knowledge` worktree at release
  commit `350afe9f578b6620e29c46312b2fa388ece5e363`.
- Ran the complete local baseline: 138/138 tests, compilation, governance, and
  whitespace checks passed.
- Inspected `.github/workflows/ci.yml`: one Python 3.12 workflow runs on every
  push and pull request, with no branch restriction and no required secrets.
- Verified remote run `34766061187` for release commit `350afe9` failed in the
  deterministic test step. Governance and compilation passed.
- Identified both remote-only failures: project dependencies were not installed
  (`pypdf` missing), and `scripts/eos-status` was committed as mode `100644` so
  three subprocess tests received `PermissionError`.
- Added the project dependency installation step and recorded executable mode
  `100755` for `scripts/eos-status`.
- Reproduced the updated CI sequence in a clean `/tmp` virtual environment;
  138/138 tests and every local CI gate passed.
- Independently verified EOS production health with `scripts/eos-status --deep`.
- Diagnosed degraded systemd state as `ssh.service` repeatedly failing to bind
  port 22 during boot. It is unrelated to EOS/Cloudflare; no service or OS
  configuration was changed. No port-22 listener was present at inspection
  time, so the historical conflicting owner is not currently observable.
- Replaced the stale dense-only evaluation script with a repeatable 12-case
  Hybrid RAG harness covering exact IDs, architecture, cross-document queries,
  citations, ambiguity, insufficient evidence, decision IDs, filenames,
  unknown errors, long-form questions, vague input, and terminology variation.
- Added retrieval-only and live generation/grounding modes with machine-readable
  output, source/citation/abstention/unsupported-claim metrics, and p50/p95 stage
  timings. Reports are intentionally written only under ignored `tmp/` state.
- Preserved the concurrent `nomic-embed-text:latest` configuration change and
  made embedding contract identity canonical across the Ollama bare/`:latest`
  aliases. Legacy index metadata remains loadable; provider, dimensions, and
  any materially different model continue to fail compatibility checks.
- Added a repeatable five-query/two-iteration stage benchmark using monotonic
  timing and the real RAG prompt. It consumes Ollama NDJSON directly to measure
  first non-empty token without changing production response semantics.
- Confirmed that internal Ollama tokens are available quickly but the EOS HTTP
  endpoint and browser receive one JSON body only after generation and claim
  verification. End-to-end token streaming is therefore not implemented.
- Reduced the configured generation ceiling from 4,096 to 512 tokens. The same
  production HTTP query remained answered with one grounded source while TTFB
  and total latency fell by 62.4%; the optimization is kept.
- Added and ran a repeatable capacity benchmark against representative current
  chunks and real 768-dimensional vectors at 1k, 5k, 10k, and 25k chunks. Large
  temporary indexes were deleted after each scale.
- Decision: `KEEP_JSON_INDEX`. Current measured scale is healthy; 25k results
  define a future re-evaluation boundary rather than justify a migration now.
- Created the canonical post-release engineering report and synchronized
  architecture, operations, configuration notes, roadmap, backlog, changelog,
  documentation navigation, and local test/script READMEs.
- Passed the final 140-test regression, Python compilation, governance
  validation, staged/unstaged whitespace checks, and a final deployed health
  check. The protected root README was not modified.
- Rechecked GitHub Actions before push: release run `34766061187` was still the
  latest and remained failed as documented.
- Received owner authorization by instruction to run this resume, committed the
  increment as `9c642f795aab4f46f20012513c799fe628e853c1`, and pushed branch
  `agent/python-cli-sdv-knowledge`.
- Verified remote GitHub Actions run `34796787722` for commit `9c642f7` passed
  every step: dependency installation, governance, compilation, the
  deterministic test suite, and whitespace checks. Job `validate` completed in
  30 seconds.

### Measurements

- Knowledge index: schema 2.0, 1,732 chunks, 36,301,379 bytes, persisted lexical
  index, 768-dimensional `nomic-embed-text` vectors.
- EOS local health: HTTP OK, 4 ms.
- Real deep RAG smoke: answered, 2 sources, 25,421 ms total.
- Cloudflare endpoint: Access-protected HTTP 302, 274 ms reachability check.
- Host: WSL2, 12 CPU cores, 23 GiB RAM, 8.4% RAM used during health check.
- Retrieval evaluation: 12 cases, 6 fully passed, positive source hit 87.5%,
  confidence behavior 58.3%, index load 642 ms, retrieval p50 359 ms and p95
  381 ms.
- Live evaluation: citation correctness 100%, final abstention accuracy 58.3%,
  mean unsupported-claim rate 2.9%, total p50 37.3 s, p95 101.0 s, and maximum
  115.7 s. Weak cases are canonical citation/status identity, insufficient
  revenue, exact filename, long-form boundary, vague provider, and retry
  terminology variation.
- Stage benchmark (10 samples, generation capped at 128 for controlled timing):
  embedding p50/p95 67/87 ms, Hybrid total 413/463 ms, rerank 6.2/7.2 ms,
  Ollama TTFT 170/246 ms, stream-complete 6.60/8.22 s, grounding 1.3/2.7 ms,
  and total 6.72/8.64 s. Confidence-gated cases avoid generation.
- Local production HTTP before/after on the same exact-identifier query:
  73.04/73.04 s TTFB/total at 4,096 tokens versus 27.44/27.44 s at 512 tokens;
  both answered with one source. TTFB remains equal to total because the API is
  intentionally buffered until verification.
- Capacity at 1k/5k/10k/25k chunks: file 12.4/61.9/123.9/309.7 MiB; load
  0.25/1.41/2.86/7.19 s; RSS delta 31/148/271/774 MiB; hybrid p95
  0.14/0.71/1.39/3.70 s. At 25k, dense scan (3.62 s) is the bottleneck while
  BM25 (92 ms) and reranking (2 ms) remain small.
- Final FAST health: EOS HTTP 2 ms, EOS and Cloudflare services/autostart OK,
  no recent EOS/tunnel warnings, public Access response HTTP 302 in 1.45 s.
- Remote CI: run `34796787722`, commit `9c642f7`, conclusion `success`.

### Modified files

- `.github/workflows/ci.yml`: install `.[dev]` before deterministic gates.
- `scripts/eos-status`: Git executable mode corrected from `100644` to `100755`.
- `scripts/evaluate_rag.py`, `tests/evaluation_cases.json`: realistic Hybrid RAG
  evaluation dataset, metrics, timings, and optional live generation.
- `engineering_os/llm.py`, `engineering_os/knowledge.py`, `tests/test_llm.py`,
  `tests/test_ingestion.py`: stable Ollama embedding alias contract and tests.
- `configs/ai/models.json`: concurrent user-owned model alias change preserved.
- `configs/ai/runtime.json`: measured production generation ceiling of 512.
- `scripts/benchmark_rag_latency.py`: retrieval/rerank/prompt/TTFT/stream/
  grounding/total benchmark.
- `scripts/benchmark_index_capacity.py`: scalable JSON build/load/memory and
  dense/BM25/hybrid/rerank benchmark.
- `docs/POST_RELEASE_ENGINEERING_REPORT.md` and linked canonical docs/READMEs:
  CI, evaluation, performance, streaming, capacity, decision, host, health,
  operations, and delivery-state consistency.
- `prompts/Resume_EngineeringOS_Development.md`: post-release evidence and next
  actions.

### Commands executed and tests run

- `gh auth status`, `gh workflow list`, `gh run list --commit 350afe9...`, and
  `gh run view 34766061187 --log-failed`.
- Clean-venv equivalent of dependency install, `eng.py validate`, compileall,
  unittest discovery, and `git diff --check`: all passed; 138 tests in 18.297 s.
- `scripts/eos-status --deep`, `systemctl --failed`, `systemctl status
  ssh.service`, `journalctl -u ssh.service`, and read-only port/socket checks.
- `python -m unittest tests.test_llm tests.test_ingestion`: 16/16 passed.
- `scripts/evaluate_rag.py` retrieval-only and `--live`: completed all 12 cases;
  reports at `tmp/post-release-rag-retrieval.json` and
  `tmp/post-release-rag-live.json`.
- `scripts/benchmark_rag_latency.py --iterations 2 --max-tokens 128`: 10 samples
  completed; report at `tmp/post-release-rag-latency.json`.
- Two equivalent local HTTP queries measured via curl before/after the 512-token
  cap; both HTTP 200, answered, and cited one source.
- `scripts/benchmark_index_capacity.py --scales 1000,5000,10000,25000
  --iterations 3`: all scales completed; report at
  `tmp/post-release-index-capacity.json` and scale files removed.
- Final `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`:
  140/140 passed in 18.135 s. The first sandboxed attempt could not create
  loopback sockets; the authorized rerun passed all 31 WebUI tests.
- Final compileall, `python eng.py validate`, `git diff --check`, and
  `git diff --cached --check`: passed.
- Final `scripts/eos-status`: application/tunnel checks passed; host still
  reports the unrelated failed unit. Final `gh run list` confirms no new run.
- `git commit`, `git push origin agent/python-cli-sdv-knowledge`, and
  `gh run watch 34796787722 --exit-status`: push succeeded and remote CI passed.

### Known risks

- Historical release run `34766061187` remains red, while its fixes are verified
  by green successor run `34796787722` on commit `9c642f7`.
- GitHub emitted a non-blocking Node 20 deprecation warning for
  `actions/checkout@v4` and `actions/setup-python@v5`; evaluate supported major
  upgrades as a separate CI maintenance change.
- End-to-end HTTP output is currently buffered. Direct Ollama TTFT and local
  HTTP first-byte timing are measured, but even the improved production query
  takes 27.44 s before the browser receives an answer.
- Current confidence behavior accepts unsupported revenue and one-word provider
  queries. Exact-filename and terminology-variation retrieval are also weak.
  Do not hide these quality gaps by weakening the evaluation expectations.
- Browser-visible streaming cannot safely expose raw tokens under the current
  post-generation claim-verification contract. A future streaming design needs
  a verified-event protocol; proxy testing through Cloudflare Access also
  requires authenticated credentials unavailable to this benchmark.
- At roughly 25k representative chunks, dense/hybrid p95 exceeds the proposed
  2 s interactive target and load exceeds 5 s. Re-run before that scale and
  evaluate a vector store only if actual production measurements also breach.
- The SSH port collision is historical and recurring across boots, but does not
  affect EOS. Do not restart or disable SSH without separate owner intent.

### Optional product follow-up

- Improve the documented six weak RAG cases as a separate measured increment.
- Define a verified streaming-event protocol before changing the HTTP contract.
- Re-run capacity/concurrency measurements as the corpus approaches 10k chunks.
- Upgrade GitHub actions after reviewing their current supported major versions.

### Next exact action

No required post-release action remains. The next optional measured increment
is to improve ambiguity/insufficient-evidence handling against the retained
evaluation dataset without weakening its expectations.

## Baseline

- Branch: `agent/python-cli-sdv-knowledge`
- Commit: `dfddc3d`
- Worktree before this resume update: clean
- Baseline command:
  `python3 -m unittest tests.test_rag tests.test_ingestion tests.test_query`
- Baseline result: 22/22 tests pass
- Original index schema: `schemaVersion: 1.1`, top-level `embedding` and
  `chunks`; 854 current chunks
- Original chunk fields: `path`, `heading`, `text`, `embedding`, `source_type`,
  `last_updated`, `authority`
- Runtime dependencies: none declared; optional development dependency is
  `pytest>=8.0`
- Relevant architecture: heading-based Markdown chunking; `nomic-embed-text`
  dense embeddings; cosine ranking; candidate and confidence thresholds;
  Ollama `rag` generation; inline `path#heading` citations; lexical claim
  verification after generation

## Completed

- Read the full Hybrid RAG task prompt.
- Reconciled the previous WebUI checkpoint with commit `dfddc3d` and replaced
  it with this task-focused checkpoint at the established location.
- Inspected the current index representation, configuration convention,
  dependency declaration, parsing/chunking, dense search, confidence gate,
  citation construction, and claim-grounding path.
- Verified the relevant 22-test baseline.
- Implemented deterministic approximate-token chunking with configurable
  maximum, overlap, and minimum sizes; semantic block boundaries and short code
  fences are preserved where practical.
- Preserved Markdown heading hierarchy and added stable `document_id`,
  `chunk_id`, and `chunk_index` values.
- Added optional `document_type`, `language`, `project`, `version`, `tags`, page,
  and source-timestamp metadata with simple frontmatter/path extraction.
- Upgraded newly written indexes to schema `2.0`; schema `1.1` loads with safe
  defaults and triggers re-embedding on the next incremental document update.
- Passed 38 chunking/ingestion/RAG/query/action/CLI tests.
- Added a deterministic local tokenizer that preserves identifiers, filenames,
  configuration keys, acronyms, and useful split forms.
- Added persisted BM25 corpus statistics to schema `2.0`; legacy indexes build
  an in-memory lexical fallback when loaded.
- Added weighted Reciprocal Rank Fusion over dense and BM25 rankings, applied
  metadata filters after candidate fusion, and exposed per-stage diagnostics.
- Preserved `load_index()` compatibility and added `load_knowledge_index()` for
  consumers that need persisted lexical state.
- Passed 43 chunking/ingestion/retrieval/RAG/query/action/CLI tests.
- Added a replaceable `Reranker` protocol and deterministic local reranker that
  scores query/evidence term alignment, dense quality, and hybrid rank quality.
- Added enabled/disabled reranking configuration, bounded shortlist size, and
  final top-k policy without a cloud or ML dependency.
- Routed query, CLI search, and web action search through persisted BM25,
  hybrid fusion, metadata filtering, and reranking.
- Adapted confidence to the final rerank score while keeping candidate
  eligibility separate and preserving the existing `0.62` abstention threshold.
- Preserved page-capable citation metadata through `RetrievedChunk` and
  `RetrievedContext`; post-generation `verify_claims()` semantics are unchanged.
- Passed 47 Phase 4 relevant tests.
- Added controlled local PDF parsing with `pypdf`, normalized extracted text,
  shared token-aware chunking, stable IDs, and source timestamps.
- Preserved original PDF bytes under governed knowledge storage; incremental
  updates and full rebuilds now discover and index Markdown plus PDF documents.
- Added page-aware metadata and citations (`path#page=N`) without changing the
  existing Markdown `path#heading` format.
- Empty/image-only PDFs fail indexing with an explicit OCR-required message;
  malformed and password-protected PDFs fail safely. Encryption-flagged PDFs
  that open with an empty password are accepted automatically.
- Passed 50 Phase 5 relevant tests using small generated in-memory PDFs.
- Added disabled-by-default log ingestion with project-relative allowlist globs,
  retention, size, extension, regular-file, symlink, and root-boundary checks.
- Added UTF-8/binary validation plus detection of private keys, bearer headers,
  passwords, tokens, API keys, and client secrets before indexing.
- Added token-aware log chunks with stable IDs, contextual authority, log tags,
  and source timestamps.
- Wired logs only into explicit CLI/web-action full rebuilds; query execution
  never reparses changing log files.
- Passed 56 Phase 6 relevant tests, including an explicit rebuild assertion.
- Added CLI and WebUI metadata filters and opt-in retrieval diagnostics; normal
  output remains unchanged. Web upload/library/retry now supports PDFs.
- Updated the canonical ingestion/RAG guide, workflow/operations instructions,
  architecture, configuration notes, web guide, command coverage, roadmap,
  backlog, changelog, documentation navigation, and child READMEs.
- Added proposed ADR-2026-09-13-04 for local Hybrid RAG; owner approval remains
  pending and was not inferred from implementation.
- Passed the complete 135-test suite including 30 loopback web tests.
- Passed Python compilation and `git diff --check`.
- Confirmed no generated runtime index or large PDF fixture is part of the diff.
- Received explicit owner approval for the protected root README restoration,
  its current checksum baseline, and ADR-2026-09-13-01 through -04.
- Restored root README content to the Git version, normalized its bytes, updated
  the approved SHA-256 baseline, and passed repository governance validation.
- Fixed editable installation by declaring `engineering_os` as the sole Python
  package and treating generated `engineering_os.egg-info` as build state.
- Added `fonttools` for CFF Type1 decoding and fixed empty-password encrypted
  PDF parsing; all nine repository PDFs parse successfully, including the
  198-chunk iSAQB book that previously stopped a full rebuild.
- Passed the updated complete 137-test suite, compilation, diff, and governance
  validation gates.
- Updated the Ask EOS shared submit handler to preserve the trimmed question,
  reject empty/disabled submissions, clear the textarea immediately, and then
  continue the existing search or RAG request. Click and `Ctrl+Enter` retain the
  same handler and backend payload.
- Added a static frontend contract test for validation/clear/request ordering
  and both event bindings; 31/31 WebUI tests and 138/138 full tests pass.

## In Progress

- None.

## Remaining

- None. Remote CI, deployment/restart, live Ollama quality evaluation, and a
  runtime index rebuild are optional operator follow-up rather than incomplete
  repository work.

## Modified Files

- `prompts/Resume_EngineeringOS_Development.md`
  - Replaced the completed WebUI handoff with the active Hybrid RAG state.
- `engineering_os/knowledge.py`
  - Uses token-aware drafts, rich metadata, stable IDs, schema compatibility,
    and persisted lexical statistics.
  - Adds explicitly discovered log chunks during configured full rebuilds.
- `engineering_os/chunking.py`
  - Exposes the shared text splitter for non-Markdown parsers.
- `engineering_os/ingestion.py`
  - Accepts, validates, deduplicates, atomically stores, retries, and indexes
    PDF files while retaining Markdown/TXT behavior.
- `engineering_os/ingestion.py`, `engineering_os/cli.py`, `engineering_os/actions.py`
  - Pass centralized indexing configuration; CLI/action search now uses hybrid
    candidates and reranking diagnostics.
- `engineering_os/query.py`, `engineering_os/rag.py`
  - Orchestrate hybrid candidates, reranking, final confidence, citations,
    generation, and unchanged claim grounding in the required order.
- `configs/settings.json`
  - Adds explicit chunking, hybrid retrieval, reranking, PDF, and log policy.
- `pyproject.toml`
  - Declares maintained PDF parser/font-decoding dependencies and explicit
    Python package discovery.
- `tests/test_ingestion.py`
  - Covers schema `2.0` output, persisted lexical data, metadata IDs, and schema
    `1.1` compatibility.
- `tests/test_query.py`, `tests/test_actions.py`
  - Exercise the loaded lexical index and hybrid candidate interfaces.
- `tests/test_web.py`
  - Locks the Ask EOS validation, immediate-clear, payload, click, and keyboard
    submit contract alongside the existing HTTP/WebUI coverage.
- `engineering_os/library.py`, `engineering_os/web.py`,
  `engineering_os/web_static/index.html`, `engineering_os/web_static/app.js`
  - Add governed PDF reads/uploads plus filter/debug HTTP and UI behavior.
  - Clear the accepted Ask EOS question immediately before starting its request.
- `configs/README.md`, `docs/ARCHITECTURE.md`, `docs/KNOWLEDGE_INGESTION.md`,
  `docs/OPERATIONS.md`, `docs/COMMAND_COVERAGE.md`, `docs/WEBUI_GUIDE.md`
  - Document configuration and complete CLI/web ingestion-to-grounding flows,
    recovery, filters, diagnostics, PDF limits, and log safety.
- `docs/README.md`, `docs/ROADMAP.md`, `docs/PRODUCT_BACKLOG.md`,
  `docs/CHANGELOG.md`, `docs/DECISIONS.md`, `engineering_os/README.md`,
  `knowledge/README.md`
  - Reconcile navigation and delivery status with implemented behavior.
- `README.md`, `configs/project-structure.json`
  - Restored the owner-approved root wording and updated its explicitly
    approved protected SHA-256 baseline.
- `ADR/ADR-2026-09-13-01-governed-ingestion-and-atomic-json-index-updates.md`,
  `ADR/ADR-2026-09-13-02-shared-cli-web-application-actions.md`, and
  `ADR/ADR-2026-09-13-03-governed-five-screen-webui.md`
  - Recorded explicit owner acceptance and consequences.
- `docs/WEBUI_IMPLEMENTATION_LOG.md`
  - Appended Hybrid RAG web integration, validation, and approval evidence.

## New Files

- `engineering_os/chunking.py`
  - Token estimation, Markdown hierarchy, semantic splitting, overlap, stable
    IDs, and lightweight metadata parsing.
- `tests/test_chunking.py`
  - Chunk splitting, overlap, hierarchy, metadata, code-block, ID, and config tests.
- `engineering_os/lexical.py`
  - Technical tokenizer, serializable corpus statistics, and BM25 scoring.
- `engineering_os/retrieval.py`
  - Dense/BM25 candidate generation, weighted RRF, metadata filters, citations,
    and diagnostics.
- `tests/test_retrieval.py`
  - Identifier retrieval, filename/config/acronym behavior, fusion, filtering,
  and diagnostic determinism.
- `engineering_os/reranking.py`
  - Replaceable protocol, deterministic local backend, and centralized policy.
- `tests/test_reranking.py`
  - Ordering changes, metadata/citation preservation, disabled behavior, and
  strong/weak confidence behavior.
- `engineering_os/pdf.py`
  - Safe text extraction, normalization, page chunking, metadata, and errors.
- `tests/test_pdf.py`
  - Generated text-PDF success, byte preservation, page metadata/citations,
  empty/scanned handling, and malformed input.
- `engineering_os/log_ingestion.py`
  - Allowlist discovery, retention/size/path checks, sensitive-data rejection,
    token-aware drafts, stable identifiers, and timestamps.
- `tests/test_log_ingestion.py`
  - Disabled/non-allowlisted behavior, successful explicit rebuild, expiry,
    oversize, binary, secret, metadata, and unsafe-pattern tests.
- `ADR/ADR-2026-09-13-04-local-hybrid-rag.md`
  - Accepted decision, alternatives, consequences, and validation evidence.

## Configuration Changes

- `knowledge.chunking.maxTokens`: 500
- `knowledge.chunking.overlapTokens`: 80
- `knowledge.chunking.minTokens`: 80
- `knowledge.retrieval.denseEnabled`: true
- `knowledge.retrieval.lexicalEnabled`: true
- `knowledge.retrieval.hybridCandidateCount`: 30
- `knowledge.retrieval.denseWeight`: 0.65
- `knowledge.retrieval.lexicalWeight`: 0.35
- `knowledge.retrieval.rrfK`: 60
- `knowledge.rerank.enabled`: true
- `knowledge.rerank.candidateCount`: 20
- `knowledge.rerank.topK`: 6
- `knowledge.rerank.hybridWeight`: 0.20
- `knowledge.rerank.denseWeight`: 0.25
- `knowledge.rerank.lexicalAlignmentWeight`: 0.55
- `knowledge.pdf.enabled`: true
- `knowledge.pdf.ocrEnabled`: false
- `knowledge.logs.enabled`: false
- `knowledge.logs.allowlist`: `runtime/logs/rag/*.log`,
  `runtime/logs/services/*.log`
- `knowledge.logs.maxFileSizeMB`: 10
- `knowledge.logs.retentionDays`: 14

## Index Schema Changes

- New writes use schema `2.0` with optional rich metadata, stable IDs, and a
  top-level persisted `lexical` BM25 corpus.
- Existing schema `1.1` loads compatibly with empty/default metadata.
- PDF chunks use the existing optional `page_start`, `page_end`, and
  `source_timestamp`, `document_title`, and `document_author` schema `2.0`
  fields.

## Dependencies Added

- `pypdf>=4.0,<7.0` runtime dependency.
- `fonttools>=4.0,<5.0` runtime dependency for CFF Type1 font decoding.

## Important Design Decisions

- Keep the JSON index and atomic writer lock at current corpus scale.
- Add focused modules instead of expanding `knowledge.py` and `rag.py` into
  larger monoliths.
- Prefer deterministic local BM25, Reciprocal Rank Fusion, and a lightweight
  local reranker; no external search service or cloud API.
- Preserve reranking before generation and claim verification after generation.
- Do not lower existing thresholds to conceal weak retrieval.

## Tests

### Passing

- 22/22 baseline RAG, ingestion, and query tests.
- 38/38 Phase 2 relevant tests.
- 43/43 Phase 3 relevant tests.
- 47/47 Phase 4 relevant tests.
- 50/50 Phase 5 relevant tests.
- 56/56 Phase 6 relevant tests.
- 135/135 full regression tests, including 30/30 loopback web tests.
- 137/137 post-remediation regression tests, including the empty-password and
  password-protected PDF cases.
- 138/138 post-UX-change regression tests; 31/31 WebUI tests pass.

### Failing

- None.

## Commands Already Run

```bash
git status --short
git diff --stat
python3 -m unittest tests.test_rag tests.test_ingestion tests.test_query
python3 -m unittest tests.test_chunking tests.test_ingestion tests.test_rag tests.test_query tests.test_actions tests.test_cli
python3 -m unittest tests.test_retrieval tests.test_chunking tests.test_ingestion tests.test_rag tests.test_query tests.test_actions tests.test_cli
python3 -m unittest tests.test_reranking tests.test_retrieval tests.test_chunking tests.test_ingestion tests.test_rag tests.test_query tests.test_actions tests.test_cli
PYTHONPATH=/tmp/eos-pypdf/usr/lib/python3/dist-packages:. python3 -m unittest tests.test_pdf tests.test_ingestion tests.test_chunking tests.test_reranking tests.test_retrieval tests.test_rag tests.test_query tests.test_actions tests.test_cli
PYTHONPATH=/tmp/eos-pypdf/usr/lib/python3/dist-packages:. python3 -m unittest tests.test_log_ingestion tests.test_pdf tests.test_ingestion tests.test_chunking tests.test_reranking tests.test_retrieval tests.test_rag tests.test_query tests.test_actions tests.test_cli
PYTHONPATH=/tmp/eos-pypdf/usr/lib/python3/dist-packages:. python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=/tmp/eos-pypdf/usr/lib/python3/dist-packages:. python3 -m compileall -q engineering_os tests
git diff --check
python3 eng.py validate
```

## Known Issues / Risks

- The checked-in runtime index remains schema `1.1` generated state until the
  operator rebuilds it; code loads it compatibly.
- The protected root `README.md` changed during this worktree session at line
  514 (`12. Review` became `12.Review`). The owner explicitly approved restoring
  it and updating the stale manifest checksum; final validation passes.
- PDF support depends on `pypdf` and `fonttools`, both declared in
  `pyproject.toml`. Ubuntu/WSL system Python may be externally managed; install
  and run EOS through the repository `.venv`.
- Existing citations and old schema loading are compatibility-critical.
- Runtime indexes are generated state and must not be committed.

## Do Not Redo

- Do not repeat the Phase 1 baseline unless code affecting it changes.
- Do not redesign the Ollama runtime abstraction or replace atomic JSON writes.
- Do not remove confidence abstention or post-generation grounding.
- Do not modify the protected root `README.md`.

## Next Exact Actions

1. Optional operator action: activate `.venv` and run
   `python eng.py knowledge index` to migrate the generated runtime index from
   schema `1.1` to `2.0`.
2. Optional operator action: restart/deploy the web process and run a synthetic
   live Ollama/PDF retrieval smoke test.

## Last Verified State

- Git state before resume update: clean at `dfddc3d`.
- Latest test command: `.venv/bin/python -m unittest discover -s tests -p
  'test_*.py'` with loopback permission.
- Latest result: 138 tests passed in 19.031 seconds; 31 WebUI tests passed, and
  compilation, diff, and governance validation passed. No JavaScript DOM test
  runner is installed, so live textbox behavior remains a browser smoke step.

## Last Updated

2026-09-13
