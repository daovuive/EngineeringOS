# Knowledge Ingestion and Hybrid RAG Guide

Last verified: 2026-09-13

This is the canonical user, workflow, and recovery guide for EngineeringOS
knowledge. Command/web coverage is in [EOS Command and Web
Coverage](COMMAND_COVERAGE.md); runtime diagnostics are in
[Operations](OPERATIONS.md).

## Supported inputs and defaults

One import accepts one of:

- a `.md`, `.markdown`, `.txt`, or text-based `.pdf` file;
- direct UTF-8 text with `--text`;
- piped UTF-8 text with `--stdin`.

The default maximum is 2 MiB. External files are copied atomically into
`knowledge/inbox/` and never modified. TXT is wrapped as Markdown; PDF bytes are
preserved exactly. A supported Markdown/PDF already under `knowledge/` is
indexed in place. Automatic indexing is on by default and calls only the
configured embedding role—it does not summarize or rewrite content.

Scanned/image-only PDF, password-protected/malformed PDF, DOCX, images, and
other binary formats are unsupported. A PDF that carries an encryption flag
but opens with an empty password is accepted automatically. EOS never asks for,
stores, or attempts to bypass a PDF password. OCR is deliberately off; an
image-only PDF is saved but reports an indexing failure that says OCR is
required.

## CLI workflow

Run from the repository root:

```bash
python3 eng.py add-knowledge "my-document.md"
python3 eng.py add-knowledge --file "notes with spaces.txt"
python3 eng.py add-knowledge --file "architecture-design.pdf"
python3 eng.py add-knowledge --text "New knowledge content" --title "My note"
python3 eng.py add-knowledge --stdin --title "My note" < notes.txt
python3 eng.py add-knowledge "my-document.md" --no-index
```

Do not combine positional file, `--file`, `--text`, or `--stdin`; do not combine
`--auto-index` with `--no-index`. Success reports the saved path, import state,
index state, chunk count, and `Ready for RAG: yes`. `--no-index` truthfully
reports `skipped` and is not RAG-ready.

To organize a saved Markdown file with the configured local reasoning model:

```bash
python3 eng.py knowledge organize --file knowledge/inbox/My-note.md --dry-run
python3 eng.py knowledge organize --file knowledge/inbox/My-note.md
python3 eng.py knowledge index
```

The model can select only an existing configured destination and cannot invent
a path or overwrite a file. Copy is the recovery-friendly default; `--move`
must be explicit. PDF organization is not supported. Organization changes the
citation path, so rebuild afterward.

## Web workflow

1. Open **Knowledge → Add knowledge**.
2. Upload Markdown, TXT, or a text PDF, or switch to pasted text.
3. Leave **Automatically index for RAG** enabled unless a save-only result is
   intentional, then select **Save & index** once.
4. Read the saved/indexed/partial state. Retry indexing after a partial result.
5. Open the governed saved document and use **Ask EOS** to search or generate a
   grounded answer.
6. For Markdown, optionally preview/confirm LLM folder organization and then
   rebuild the index.

The browser sends content, never a server path. PDF bytes use validated base64
JSON transport; text uses UTF-8. Size, extension, encoding, filenames,
same-origin mutations, and returned paths are validated.

## Duplicate, collision, and retry behavior

- Re-imported identical Markdown/TXT content reuses the SHA-256 marker.
  Identical PDF bytes use the same digest comparison. Both report `unchanged`.
- Different content that maps to an existing filename gets a deterministic
  12-character content-hash suffix. Existing files are never overwritten.
- Incremental indexing replaces only the matching Markdown/PDF document's
  chunks and preserves unrelated entries. Unchanged chunks are not re-embedded.
- If embedding, parsing, or persistence fails, the source remains saved and the
  previous valid index remains intact. Retry the saved document:

```bash
python3 eng.py add-knowledge --file "knowledge/inbox/My-note.md" --auto-index
```

For an embedding-contract change or broad repair, rebuild everything:

```bash
python3 eng.py knowledge index
```

Do not claim RAG readiness until `Indexing: indexed`. For a scanned PDF, create
a reviewed text PDF with an operator-selected OCR tool outside EOS and re-import.

## Complete data path

```text
user input
  -> format / size / encoding / path validation
  -> atomic governed source save
  -> Markdown hierarchy or PDF-page parser
  -> token-aware chunks + overlap + stable IDs + rich metadata
  -> configured local embedding model
  -> vectors + persisted BM25 statistics
  -> writer lock + atomic schema-2.0 JSON replacement
  -> dense and BM25 candidates
  -> weighted Reciprocal Rank Fusion
  -> optional metadata filters
  -> bounded deterministic local reranker
  -> confidence gate
  -> top evidence for Ollama RAG generation
  -> Markdown `path#heading` or PDF `path#page=N` citations
  -> post-generation claim grounding verification
```

Schema `1.1` indexes remain readable with safe defaults; the next rebuild writes
schema `2.0`. The web process reloads the index per request, so a successful CLI
update is immediately available without an application restart.

## Search, filtering, and debug diagnostics

```bash
python3 eng.py knowledge search "REQ-SDV-0012"
python3 eng.py knowledge search "candidateMinScore" --project eos --tag api --debug
python3 eng.py knowledge ask "What does the design require?" --document-type pdf --language en
```

Filters are optional and support `source_type`, `document_type`, `project`,
`language`, and tags; repeat `--tag` to require every listed tag. Debug mode is
opt-in and reports dense, BM25, hybrid and rerank scores, candidate/final ranks,
filters, confidence decision, and any abstention reason. Normal output contains
none of this diagnostic detail.

The WebUI equivalent is **Ask EOS → Retrieval settings → Advanced**. Set the
metadata fields and optionally enable **Debug retrieval**. **Search only** stops
before generation. **Ask with RAG** continues through confidence, Ollama,
citations, and claim grounding. Weak evidence remains an explicit abstention.

## Controlled log indexing

Logs are disabled by default and are considered only during explicit
`knowledge index`, never during a query. To opt in, review and change
`knowledge.logs` in `configs/settings.json`, then rebuild. Allowlist globs must
be project-relative. EOS accepts only `.log` regular files within the project,
applies `maxFileSizeMB` and `retentionDays`, rejects symlinks/binary/non-UTF-8
files, and fails closed on obvious private keys, bearer credentials, passwords,
tokens, API keys, or client secrets. A failed rebuild retains the old index.

## Development and verification

Install project dependencies, then run:

```bash
python3 -m unittest tests.test_chunking tests.test_ingestion tests.test_pdf tests.test_log_ingestion
python3 -m unittest tests.test_retrieval tests.test_reranking tests.test_rag tests.test_query
python3 -m unittest tests.test_actions tests.test_web
python3 -m compileall -q engineering_os tests
python3 eng.py validate
git diff --check
```

Tests use temporary files, generated tiny PDFs, and mocked embeddings. Live
smoke tests must use synthetic content and must not copy personal knowledge or
credentials into logs/fixtures.

Relevant owner-accepted decisions are [governed atomic
ingestion](../ADR/ADR-2026-09-13-01-governed-ingestion-and-atomic-json-index-updates.md),
[shared CLI/web actions](../ADR/ADR-2026-09-13-02-shared-cli-web-application-actions.md),
and [local Hybrid RAG](../ADR/ADR-2026-09-13-04-local-hybrid-rag.md).
