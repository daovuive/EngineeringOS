# docs

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Operational, architectural, and governance documentation for EngineeringOS itself. Time-varying details belong here so the root README remains stable. Shared technical knowledge belongs in knowledge/.

## Canonical navigation

- [Architecture](ARCHITECTURE.md) describes implemented component boundaries.
- [Knowledge Ingestion Guide](KNOWLEDGE_INGESTION.md) is the user and recovery
  guide for import, indexing, and RAG availability.
- [EOS Command and Web Coverage](COMMAND_COVERAGE.md) maps CLI capabilities to
  web interactions and documents intentional exceptions.
- [EngineeringOS WebUI Guide](WEBUI_GUIDE.md) documents the five workspaces,
  real-data behavior, Activity recovery, and responsive behavior.
- [Operations](OPERATIONS.md) covers local commands and host diagnostics.
- [Architecture Decisions](DECISIONS.md) indexes accepted, superseded, and
  proposed ADRs.
- [WebUI Implementation Log](WEBUI_IMPLEMENTATION_LOG.md) records chronological
  implementation and verification evidence for the five-screen interface.
- [Roadmap](ROADMAP.md) and [Product Backlog](PRODUCT_BACKLOG.md) record delivery
  status and remaining work.
- [Structure Governance](STRUCTURE_GOVERNANCE.md) defines maintained layout and
  validation rules.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
