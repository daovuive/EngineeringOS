# knowledge

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Accumulated engineering knowledge. Choose a directory by document purpose: tracked learning in architect/, shared architecture knowledge in architecture/, domain knowledge in automotive/ or standards/, and project knowledge in projects/. Decisions about EngineeringOS itself belong in ADR/.

Markdown and text PDFs are indexable sources. New external files normally enter
through `python3 eng.py add-knowledge ...` and the governed `inbox/`; see the
[canonical ingestion and Hybrid RAG guide](../docs/KNOWLEDGE_INGESTION.md).

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
