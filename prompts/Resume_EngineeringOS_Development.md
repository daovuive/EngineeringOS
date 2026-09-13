# EngineeringOS RAG Upgrade Resume

Last updated: 2026-09-13

## Task

Upgrade EngineeringOS from dense-only grounded RAG to Hybrid RAG without
rewriting the working subsystem. Preserve local-first Ollama integration,
atomic JSON persistence, confidence abstention, citations, and post-generation
claim verification.

## Current Phase

Phase 7 — Documentation, final regression, governance, and approval complete.

## Overall Status

COMPLETE

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
