# Changelog

## Post-release measurement and hardening — 2026-09-13

- Verified the release GitHub Actions run remotely, reproduced its dependency
  and executable-mode failures, corrected both, and verified green successor
  run `34796787722` after push.
- Upgraded checkout/setup-python actions to their Node 24 majors and verified
  warning-free remote run `34797235128`.
- Added a 12-category Hybrid RAG evaluation dataset plus repeatable retrieval,
  generation, grounding, citation, abstention, and latency reporting.
- Added monotonic stage/TTFT and JSON-index capacity benchmarks; retained the
  JSON index at current scale with explicit future migration thresholds.
- Reduced the measured generation ceiling from 4,096 to 512 tokens, cutting the
  same local HTTP query from 73.04 to 27.44 seconds while retaining its grounded
  answer and source.
- Canonicalized the Ollama bare/`:latest` embedding-model alias so existing
  compatible indexes do not require a false rebuild.
- Confirmed the web response remains buffered until claim verification,
  documented why raw-token streaming was not introduced, and separated the
  unrelated failed SSH unit from healthy EOS/Cloudflare services.

## Local Hybrid RAG — 2026-09-13

- Replaced heading-only/dense-only retrieval with token-aware overlapping
  chunks, rich stable metadata, persisted BM25, weighted RRF, metadata filters,
  and a bounded replaceable deterministic local reranker.
- Kept candidate eligibility separate from final confidence and preserved
  abstention, inline citations, Ollama roles, and post-generation claim checks.
- Added controlled text-PDF ingestion with page citations and disabled-by-default
  allowlisted log indexing with retention, size, binary, path, and secret checks.
- Accepted encryption-flagged PDFs that decrypt with an empty password while
  continuing to reject password-protected PDFs; added `fonttools` for reliable
  CFF Type1 font decoding.
- Declared `engineering_os` explicitly as the sole Python package so editable
  installation does not mistake repository content directories for packages.
- Added opt-in CLI/WebUI retrieval diagnostics and PDF upload/library support.
- Added ADR-2026-09-13-04; the owner accepted it with the related ingestion,
  shared-action, and WebUI decisions after final validation.

## Sprint 1

- Initial repository
- CLI
- ADR

## v1.1 Review Candidate
- Repository reviewed
- Recommend renaming configs/template.json to templates.json if intentional.
- Recommend LICENSE.md -> LICENSE.txt template consistency.

## Five-sprint workflow implementation — 2026-09-13

- Repaired SDV package structure registration and local README governance.
- Added executable Code Review, Requirement Review, ADR Assistant, and Solution
  Architect workflows through the shared CLI and web service.
- Added bounded output repair, source allowlisting, and grounding checks for
  retrieval-backed workflow claims.
- Added registered workflow skill contracts and GitHub Actions validation.
- Reconciled roadmap, backlog, architecture, and operations documentation with
  verified behavior and retained limitations.
- Completed the bounded Sprint 5 Solution Architect workflow using
  schema-constrained generation plus deterministic diagrams, stages, ADR
  options, and evidence rendering; validated live runs passed with and without
  optional retrieval.

## Knowledge ingestion and web command coverage — 2026-09-13

- Added minimal-argument Markdown/plain-text ingestion with automatic indexing,
  content deduplication, deterministic collision handling, provenance, retry,
  and no-index operation.
- Added atomic, writer-coordinated document-level JSON index updates that retain
  the previous valid index on failure.
- Added browser upload/paste ingestion, visible partial states, retry, safe
  document opening, and same-origin mutation checks.
- Added an explicit EOS action catalog and task-oriented web controls for the
  supported CLI surface; no arbitrary shell endpoint was introduced.
- Established `prompts/Resume_EngineeringOS_Development.md` as the live
  development checkpoint and `docs/COMMAND_COVERAGE.md` as the coverage matrix.
- Added `docs/KNOWLEDGE_INGESTION.md` as the canonical CLI/web user and recovery
  guide, then linked the relevant area READMEs to it.
- Initially proposed ADRs for governed atomic ingestion and the shared CLI/web
  application-service boundary; both were later owner-accepted. Corrected ADR-0002 to show
  that ADR-0003 supersedes it and refreshed the decision index.

## Five-workspace WebUI — 2026-09-13

- Replaced the single-column browser form with the owner-approved Knowledge,
  Ask EOS, Engineering, Models, and Project workspaces plus shared Activity.
- Added governed document library/source inspection, bounded RAG excerpts,
  server-validated retrieval controls, folder preview/apply binding, and
  preview-token revalidation for index and project mutations.
- Retained five desktop screenshots and a narrow responsive screenshot as
  historical visual evidence; removed the temporary runtime demo-data mode so
  every shipped page uses the real local API and configured runtime.
- Added the WebUI guide, proposed ADR-2026-09-13-03, and persistent
  implementation log. Live deployment remains pending; the ADR was later
  owner-accepted.
