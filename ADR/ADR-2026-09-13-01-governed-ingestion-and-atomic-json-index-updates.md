# ADR: Govern Knowledge Ingestion and Update the JSON Index Atomically

- **Date:** 2026-09-13
- **Status:** Proposed
- **Scope:** Knowledge ingestion, document identity, and JSON index consistency

## Context

EngineeringOS could rebuild a Markdown index but had no minimal import command,
plain-text conversion, duplicate identity, document-level update, or protection
against concurrent CLI/web writers. A failed full or incremental write could
otherwise publish partial state or lose another writer's update.

The project already owns a provider-neutral embedding boundary and a compatible
versioned JSON index. Current scale does not justify a vector database.

## Alternatives considered

### Ask an LLM to choose a destination

Rejected for ingestion. Model output must not control filesystem paths. LLM
classification remains a separate optional `knowledge organize` workflow over
an explicit allowlist.

### Require a category for every import

Rejected because it prevents the required minimal command and couples import to
taxonomy decisions. A governed inbox gives every new source one safe location.

### Rebuild the complete index after every import

Rejected because it re-embeds unrelated content, increases failure exposure,
and scales poorly with corpus growth.

### Introduce a vector database or background queue

Rejected at current scale because the existing JSON store and synchronous local
runtime satisfy measured acceptance without new infrastructure.

## Proposed decision

1. Store external Markdown/plain text under fixed `knowledge/inbox/`; copy the
   source and never silently overwrite it.
2. Preserve the input body and add non-embedded provenance comments containing
   source filename, source format, SHA-256, and ingestion time.
3. Use SHA-256 for idempotent re-import and a deterministic hash suffix for
   different-content filename collisions.
4. Convert plain text to Markdown and retain citations to the saved project
   document.
5. Update one document's chunks under a thread/process writer lock. Preserve
   unrelated entries and replace stale entries for that path.
6. Validate the embedding contract and dimensions before publishing.
7. Persist the JSON index through a same-directory temporary file, `fsync`, and
   atomic replacement. Preserve the previous index on embedding/write failure.
8. Index automatically by default; `--no-index` is explicit and cannot claim
   RAG readiness.

## Consequences

### Positive

- One minimal import works for CLI and web.
- Repeat imports are idempotent.
- Readers observe either the previous or complete next index.
- CLI/web writers do not silently lose unrelated updates.
- Existing JSON storage and runtime abstractions remain reusable.

### Trade-offs

- The inbox is a staging taxonomy; users may later organize documents.
- File locks use the current Linux/WSL execution environment.
- A full rebuild remains necessary after embedding-contract changes.
- Import does not parse PDF/DOCX or infer categories.

## Validation evidence

- Unit tests cover input forms, Unicode, duplicates, collisions, no-index,
  retry, concurrent updates, stale replacement, dimension mismatch, embedding
  failure, and atomic persistence failure.
- Live synthetic CLI and web imports were retrieved by both adapters with
  citations; repeat imports produced two documents/two chunks only.
- `python3 eng.py validate`, compilation, and the full test suite passed on
  2026-09-13.

## Approval

This ADR documents implemented behavior but remains **Proposed** until the
project owner explicitly accepts it. Rejection requires revisiting the related
implementation before treating another mechanism as canonical.
