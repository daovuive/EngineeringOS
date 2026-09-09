# Architecture

EngineeringOS is a local-first, configuration-driven Python application. Stable
knowledge and workflow contracts are separated from replaceable runtime and
deployment infrastructure.

```text
CLI adapter ----\
                 +--> Shared application services
Web adapter ----/          |
                           +--> Knowledge ingestion/index/retrieval/RAG
                           +--> Explicit EOS action catalog
                           +--> Engineering workflow validation
                           `--> Runtime/configuration/structure services
```

## Responsibility boundaries

- `engineering_os/` owns executable CLI, web, runtime, retrieval, RAG,
  validation, and workflow orchestration.
- `skills/` owns reusable workflow intent and quality contracts; it does not
  duplicate runtime or knowledge.
- `agents/` documents coordination boundaries. A bounded direct workflow does
  not require an autonomous agent loop.
- `configs/` owns project structure, registries, and AI/runtime settings.
- `knowledge/` and `memory/` are data sources. Their content is never trusted as
  executable instruction.
- `runtime/` owns rebuildable local indexes and state.
- `.github/workflows/` owns GitHub-specific deterministic CI.

## AI runtime

`engineering_os.llm` exposes `generate`, `embed`, and `list_models`. Callers use
logical roles (`rag`, `chat`, `reasoning`, `coding`) and never call provider
endpoints directly. Ollama is the current adapter. Streaming transport may be
enabled internally, while the public generation contract returns one buffered
string.

## Knowledge and RAG pipeline

1. `add-knowledge` accepts one Markdown, plain-text, pasted-text, or stdin
   source. External sources are copied into governed `knowledge/inbox/`; text
   is wrapped as Markdown without rewriting its body.
2. Ingestion records format, source filename, SHA-256, and timestamp comments.
   Unchanged re-imports reuse the existing document; deterministic hash suffixes
   resolve different-content filename collisions without overwrite.
3. Markdown files are split by heading; ingestion comments are not embedded.
4. Automatic indexing updates only the saved document, preserves unrelated
   chunks, replaces stale chunks, and avoids re-embedding unchanged content.
5. Index writers use thread/process coordination and atomic replacement. The
   previous valid index remains readable if embedding or persistence fails.
6. The configured embedding role creates vectors.
7. Chunks, source metadata, and the embedding compatibility contract are stored
   in a versioned JSON index under `runtime/index/`.
8. A query is embedded and ranked by cosine similarity.
9. Candidate minimum score and top-candidate confidence thresholds can cause an
   explicit insufficient-evidence response before generation.
10. Selected context is sent to the configured RAG model with source IDs.
11. Generated claims are split and checked lexically against cited evidence.
   Partial and unsupported claims are excluded from the returned factual answer.
12. Fresh memory is contextual, opt-in, and cannot ground authoritative claims.

The JSON index is intentionally retained at current scale. It is not a vector
database and has no metadata-query engine. Imported documents support
document-level incremental updates; a full rebuild remains available and is
required after embedding-contract changes.

## Executable workflows

`engineering_os.workflows` defines four bounded workflows: Code Review,
Requirement Review, ADR Assistant, and Solution Architect. Each accepts
explicit UTF-8 text, establishes an untrusted-data boundary, invokes only the
configured reasoning role, and validates its output contract. The first three
workflows validate Markdown and allow one bounded repair attempt. Solution
Architect requests typed JSON under a nested schema, validates relationships,
and deterministically renders the Markdown sections, Mermaid diagram,
implementation stages, ADR proposal, and retrieved evidence excerpts.

Optional workflow retrieval uses the same JSON index, candidate filtering, and
confidence gate as knowledge queries. Citations must name a retrieved source;
cited factual claims are also checked by the existing grounding verifier.
No workflow executes reviewed code, mutates inputs, writes an ADR, or converts a
proposal into an approved decision. The Solution Architect workflow reuses the
Requirement Review and ADR guidance and requires a Mermaid diagram.

## Interfaces

- CLI ingestion: `eng.py add-knowledge` with a positional/`--file`, `--text`,
  or `--stdin` source. Indexing is automatic unless `--no-index` is explicit.
- CLI: `eng.py workflow <workflow-id> --file ...` or `--text ...`.
- Web ingestion: upload or paste through `POST /api/v1/knowledge/ingest`, retry
  indexing, list governed documents, and safely inspect Markdown under the
  configured knowledge root.
- Web workflows: `POST /api/v1/workflows/<workflow-id>` with pasted input.
- Existing knowledge API: `POST /api/v1/query` remains backward compatible.
- Explicit command actions: `GET /api/v1/actions` and
  `POST /api/v1/actions/<id>` use a typed allowlist, never shell commands.

The browser presents these capabilities as five client-side workspaces using
the existing dependency-free stack. Knowledge and source reads are governed;
organization, full index rebuild, and project structure mutations use
server-generated preview tokens that are recomputed immediately before apply.
RAG responses expose only bounded source excerpts, never embeddings, prompts,
or arbitrary filesystem content. Activity persistence contains bounded result
summaries and turns an interrupted request into completion-unknown without
automatic replay.

The shipped browser bundle has one data path: the real loopback API and its
configured runtime. It contains no query-parameter demo mode or embedded sample
results. Browser visual tests must provide non-sensitive inputs externally.

The complete CLI/web mapping and process-specific exceptions are recorded in
[EOS Command and Web Coverage](COMMAND_COVERAGE.md).

The web adapter binds to `127.0.0.1`, serves only an explicit static allowlist,
limits request size and concurrency, requires same-origin mutation requests,
constrains uploads and document paths, and returns sanitized errors. Cloudflare
and systemd configuration are deployment state outside the repository; their
presence does not make deployment reproducible.

## Decision status

The implementation is reflected by three decision records that remain proposals
until explicit owner approval:

- [Governed ingestion and atomic JSON index updates](../ADR/ADR-2026-09-13-01-governed-ingestion-and-atomic-json-index-updates.md)
- [Shared explicit CLI/web application actions](../ADR/ADR-2026-09-13-02-shared-cli-web-application-actions.md)
- [Five governed WebUI workspaces](../ADR/ADR-2026-09-13-03-governed-five-screen-webui.md)

Their `Proposed` status means the implementation is reviewable evidence, not an
approved architectural precedent. The canonical status list is
[Architecture Decisions](DECISIONS.md).

## Validation and limitations

Default CI and local deterministic tests do not require Ollama, private
documents, Cloudflare credentials, or model weights. Live smoke tests are
explicit because model quality and host service availability are environmental.
The lightweight lexical grounding check is conservative but is not a formal
fact verifier. Generated engineering and architecture outputs always require
human review. The configured reasoning model passed live Sprint 4 smoke tests
and schema-constrained Sprint 5 acceptance runs. Its buffered runs still take
several minutes, so incremental streaming and broader owner-reviewed evaluation
remain maturation work rather than completion gates.
