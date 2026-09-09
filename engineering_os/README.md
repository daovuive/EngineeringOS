# engineering_os

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

EngineeringOS Python implementation: CLI, configuration loading, structure
creation/validation, runtime abstraction, knowledge ingestion, incremental JSON
indexing, Markdown search/RAG, bounded engineering workflows, explicit web
actions, governed knowledge-library reads, preview-bound mutations, and the
loopback web adapter. The root `eng.py` is only an entry point.
Runtime calls go through `LLMRuntime`/`create_runtime`; workflow intent remains
registered under `skills/`, while executable orchestration lives in
`engineering_os.workflows`.

Canonical contracts and user behavior are documented in
[Architecture](../docs/ARCHITECTURE.md), the
[Knowledge Ingestion Guide](../docs/KNOWLEDGE_INGESTION.md), and
[EOS Command and Web Coverage](../docs/COMMAND_COVERAGE.md). The five-screen
interface is documented in the [WebUI Guide](../docs/WEBUI_GUIDE.md).

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
