# Knowledge Ingestion Guide

Last verified: 2026-09-13

This is the canonical user and recovery guide for adding knowledge to
EngineeringOS. The command/web inventory remains in
[EOS Command and Web Coverage](COMMAND_COVERAGE.md); runtime diagnostics remain
in [Operations](OPERATIONS.md).

## Supported input and defaults

EngineeringOS accepts exactly one source per import:

- a positional file or `--file` using UTF-8 `.md`, `.markdown`, or `.txt`;
- direct UTF-8 text using `--text`;
- piped UTF-8 text using `--stdin`.

PDF, DOCX, images, and other binary formats are rejected rather than decoded as
plain text. The configured limit is 2 MiB. External input is copied; its
original is never modified. Files already under `knowledge/` are indexed in
place when they are supported Markdown.

Imported documents use the governed `knowledge/inbox/` destination. The model
does not select this path and no category argument is required. Plain text is
stored as Markdown so the existing heading chunker can index it. The body is
preserved; small comments record source filename, format, SHA-256, and import
time and are excluded from embeddings.

Automatic indexing is enabled by default. It uses only the configured embedding
role; it does not call a chat model, summarize, or rewrite the document.

## Optional LLM-assisted organization

Ingestion deliberately uses the fixed inbox. To ask the installed/configured
reasoning model to select the best existing knowledge area, preview the result:

```bash
python3 eng.py knowledge organize --file knowledge/inbox/My-note.md --dry-run
```

Then apply it as a safe copy:

```bash
python3 eng.py knowledge organize --file knowledge/inbox/My-note.md
python3 eng.py knowledge index
```

Add `--move` only when the inbox source should be removed after successful
placement. The model can choose only from the existing destinations in
`knowledge.organizer.destinations`; it cannot invent a path, rename a file, or
overwrite an existing target. Validation, an unavailable runtime, or a rejected
model response fails before placement. Copy is the recovery-friendly default;
use `--move` only after previewing and retaining any backup your workflow
requires. Organization does not update the index automatically, so run the
documented rebuild before relying on the new path in RAG.

The web equivalent is **Knowledge → Add knowledge → Suggest folder with local
LLM**. Web organization accepts only a document already saved in the governed
inbox. The server binds each preview to the document SHA-256 and selected
approved destination, reports collisions and indexing/citation effects, and
revalidates both before a confirmed copy or move.

## CLI examples

All examples run from the repository root:

```bash
python3 eng.py add-knowledge "my-document.md"
python3 eng.py add-knowledge --file "notes with spaces.txt"
python3 eng.py add-knowledge --file "kiến-thức.md" --auto-index
python3 eng.py add-knowledge --text "New knowledge content"
python3 eng.py add-knowledge --text "New knowledge content" --title "My note"
python3 eng.py add-knowledge --stdin --title "My note" < notes.txt
python3 eng.py add-knowledge "my-document.md" --no-index
```

Do not combine positional file, `--file`, `--text`, or `--stdin`. Do not combine
`--auto-index` and `--no-index`.

A successful indexed result reports:

```text
Document: knowledge/inbox/My-note.md
Import: saved
Indexing: indexed
Chunks: 1
Ready for RAG: yes
```

`--no-index` is a successful save, but reports `Indexing: skipped` and never
claims the document is ready for RAG.

## Web workflow

1. Open the protected EngineeringOS page.
2. In **Add knowledge**, choose one `.md`, `.markdown`, or `.txt` file from the
   current device, or paste text.
3. Optionally enter a title. Leave **Index automatically for RAG** selected for
   the default behavior.
4. Select **Save knowledge** once. The button remains disabled while the request
   is active.
5. Read the explicit saved/indexed/partial state. Use **Open saved document** to
   inspect the stored source, then use **Ask EOS** for search or grounded RAG.
6. Optionally request a folder suggestion, choose another approved folder if
   needed, confirm Copy/Move, and rebuild the index to refresh citation paths.

The browser sends file content, never a server filesystem path. Mutation
requests must be same-origin. Upload size, extension, UTF-8 decoding, filenames,
and returned document paths are validated.

## Duplicate and collision behavior

- Re-importing identical content finds the existing SHA-256 marker and reports
  `Import: unchanged`; it does not create another document or chunk.
- If a different document would use an existing filename, the new filename gets
  a deterministic 12-character content-hash suffix.
- An existing different file is never overwritten silently.
- Updating a Markdown document already under `knowledge/` replaces only that
  document's stale chunks and preserves every unrelated index entry.

## Indexing and RAG availability

```text
explicit user input
    -> format/size/UTF-8 validation
    -> fixed governed inbox or existing knowledge document
    -> atomic document save
    -> heading chunks (ingestion metadata excluded)
    -> configured embedding model
    -> embedding-contract/dimension validation
    -> writer lock + atomic JSON index replacement
    -> indexed status and chunk count
    -> available to search/RAG on the next request
```

The CLI and web application share this service. RAG loads the JSON index for
each request, so a successful CLI update is visible to the running web process
without an application cache refresh.

## Partial failure and recovery

If saving succeeds but embedding or index persistence fails:

- the source document remains saved;
- the previous valid index remains intact;
- the CLI exits nonzero and reports `Saved, indexing failed`;
- the web page shows a partial state and a **Retry indexing** action;
- retry replaces stale chunks and cannot duplicate an unchanged document.

Copy and run the CLI retry printed by the failed command. Its form is:

```bash
python3 eng.py add-knowledge --file "knowledge/inbox/My-note.md" --auto-index
```

Alternatively, rebuild the complete compatible index:

```bash
python3 eng.py knowledge index
```

Do not claim RAG readiness until the result reports `Indexing: indexed`. An
embedding-contract mismatch requires a full rebuild with the currently
configured embedding model; vectors from incompatible contracts are never
mixed silently.

## Development and verification

Targeted checks:

```bash
python3 -m unittest tests.test_ingestion tests.test_add_knowledge_cli
python3 -m unittest tests.test_actions tests.test_web
python3 -m compileall -q engineering_os tests
python3 eng.py validate
git diff --check
```

Default tests use temporary storage and mocked embeddings. Live ingestion/RAG
smoke tests must use synthetic content and a temporary project root; do not copy
personal knowledge into logs or fixtures.

Architecture decisions are recorded as proposed ADRs until the owner approves
them: [governed ingestion and atomic index updates](../ADR/ADR-2026-09-13-01-governed-ingestion-and-atomic-json-index-updates.md)
and [shared CLI/web application actions](../ADR/ADR-2026-09-13-02-shared-cli-web-application-actions.md).
