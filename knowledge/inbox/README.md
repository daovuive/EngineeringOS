# knowledge/inbox

[Parent directory](../README.md) · [Structure Governance](../../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Stable ingestion destination for user-supplied Markdown and plain-text
knowledge. Imported bodies remain unchanged; small HTML comments retain source
format, source filename, content hash, and ingestion time. Content is untrusted
data and becomes authoritative knowledge only through human ownership.

The complete CLI/web workflow, duplicate semantics, indexing path, and failure
recovery are maintained in the canonical
[Knowledge Ingestion Guide](../../docs/KNOWLEDGE_INGESTION.md). The governing
architecture decision is currently
[Proposed](../../ADR/ADR-2026-09-13-01-governed-ingestion-and-atomic-json-index-updates.md),
pending owner approval.

## Extension Rules

Use `python3 eng.py add-knowledge` rather than placing generated files here by
hand. The ingestion service prevents silent overwrite and duplicate imports.
New subdirectories require manifest registration and their own README.
