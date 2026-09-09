# Changelog

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
- Proposed, but did not mark accepted, ADRs for governed atomic ingestion and
  the shared CLI/web application-service boundary; corrected ADR-0002 to show
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
  implementation log. Live deployment and ADR approval remain pending.
