# Architecture

Engineering OS follows a modular architecture. Configuration files describe
the modules, while Python provides the execution layer.

```text
User
 |
 v
Python CLI / AI Agent
 |
 +--> Skills ------> Prompts / Tools
 |
 +--> Memory ------> Knowledge Repository
 |
 +--> AI Runtime --> Local AI Model
```

Module boundaries:

- `agents/` contains role-specific orchestration and decides which skills to use.
- `skills/` contains reusable capability workflows. It is the canonical home
  for AI skills and must not duplicate knowledge or prompt content.
- `prompts/` contains reusable prompt fragments and prompt templates.
- `tools/` contains integrations with external systems and utilities.
- `memory/` contains persistent context about the project and its owner.
- `knowledge/` contains source documents and engineering knowledge.
- `runtime/` contains EngineeringOS-owned generated data such as caches and indexes; provider-owned model binaries remain outside the repository.
- `engineering_os/` contains executable Python modules, including runtime adapters.

Repository governance is defined in [Structure Governance](STRUCTURE_GOVERNANCE.md).
The root README is the protected charter, the manifest inventories managed
directories, and each directory README explains placement and navigation.
`python eng.py validate` checks mechanical drift, README links and the protected
root baseline. It does not enforce operating-system permissions or determine
whether document content belongs to the correct domain.

AI runtime integration is accessed through a small runtime abstraction in
`engineering_os.llm`. Core CLI, future RAG code, and agents should depend on
the generic runtime API (`generate`, `embed`, `list_models`) rather than
provider-specific HTTP endpoints. Ollama is the first implemented adapter.
Provider definitions and logical model bindings are stored under `configs/ai/`;
additional providers require adapters before they can be enabled.

When runtime `stream` is enabled, the Ollama adapter uses Ollama's streaming
transport internally. The current `generate` API still buffers streamed chunks
and returns one final string; end-to-end incremental token streaming can be
added later when a caller needs it.

The first knowledge-base slice is implemented in `engineering_os.knowledge`:
it discovers Markdown files, creates heading-based chunks, requests embeddings
through the runtime abstraction, and stores a local JSON index. Search ranks
chunks with cosine similarity. This is an indexing/search foundation, not yet a
full RAG prompt assembly or vector-database integration.

The intended execution flow is:

```text
Request -> Agent -> Skill -> Retrieve knowledge/memory -> Call AI Runtime
        -> Validate output -> Return result for human review
```

Every module should remain loosely coupled. A skill should be callable by more
than one agent, and a runtime change should not require changing skill logic.
