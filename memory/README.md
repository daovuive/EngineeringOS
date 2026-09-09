# memory

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Long-term project context as sourced notes with update dates. Do not copy roadmaps, profiles, or policies to create a second source of truth. Check older notes against current sources before use. This is a repository directory, not private memory for an AI application.

## Memory Contract

- **Source:** human-maintained notes in `memory/`, with each note carrying a
  `Last updated: YYYY-MM-DD` line when it is eligible for retrieval.
- **Freshness:** memory is eligible only when its update date is no more than
  the configured `memory.retrieval.maxAgeDays` old. Missing or invalid dates
  are treated as stale and excluded from retrieval.
- **Authority:** memory is contextual and non-authoritative. It does not
  establish technical requirements, architecture decisions, or verified
  career experience. Those claims remain owned by their primary sources.
- **Retrieval role:** memory is opt-in context for project intent, current
  state, preferences, and continuity. The existing knowledge index and RAG
  path are reused; no separate memory store is created.

Memory may guide what the model considers relevant, but it cannot by itself
ground an authoritative answer. AI-generated assumptions, suggestions, or
inferences must not be written to `memory/` as facts without human review and
an explicit source/update date.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
