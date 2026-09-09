# agents

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Defines AI roles and work-coordination rules. Agents select skills from the
registry, use knowledge/career sources, and verify results. Reusable workflow
intent belongs in `skills/`; bounded execution lives in
`engineering_os.workflows`. No autonomous agent loop is currently implemented.

## Agent Integration Boundary

An agent is a task coordinator, not a second implementation of the AI stack.
When an executable agent is added, it must:

- classify the request and select registered skills from `configs/skills.json`;
- pass only the context required for the current task;
- invoke the existing retrieval, memory, RAG, and provider/runtime
  abstractions;
- verify the skill output and preserve its source references; and
- return a proposal for human review when the result changes a decision,
  career evidence, authoritative knowledge, memory, or repository policy.

Skills remain responsible for reusable workflows. Provider selection and model
configuration remain under `configs/ai/`; retrieval and grounding remain under
`engineering_os/knowledge.py` and `engineering_os/rag.py`; memory semantics
remain under `memory/`. Agents must not copy those responsibilities or call a
provider directly.

A direct single-skill request uses `eng.py workflow <id>` or the corresponding
web route without adding an agent round-trip. The Solution Architect workflow
is the current bounded coordinator: it reuses requirement and ADR guidance in
one validated generation contract. A future autonomous coordinator remains
justified only when a task needs stateful multi-step execution beyond these
bounded workflows.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
