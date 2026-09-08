# ADR: Keep the Local AI End-to-End Practice as One Master Prompt File

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** Prompt organization and AI practice workflow

## Context

EngineeringOS uses reusable prompts as practical exercises for reviewing, building, validating, and operating the Local AI stack.

The Local AI roadmap currently contains fourteen sequential practice phases:

1. Architecture review
2. Governance validation
3. Provider/model configuration
4. Provider smoke testing
5. Embedding setup
6. Knowledge indexing
7. Retrieval validation
8. RAG integration
9. RAG evaluation
10. Memory integration
11. Skills integration
12. Agent integration
13. Observability and performance review
14. Portability, recovery, and final validation

A decision was required on whether to store these practices as fourteen separate Markdown files or as one master Markdown file.

## Decision

The fourteen Local AI practice prompts SHALL be stored in one master Markdown file:

```text
prompts/EngineeringOS_Local_AI_End_to_End_Practice.md
```

The file SHALL contain one independent prompt section per phase.

Codex or another AI tool SHOULD execute only the current phase prompt rather than treating the entire file as one execution request.

No new folder is required for this practice roadmap.

## Rationale

Keeping one master file provides the best balance between maintainability and context efficiency.

Benefits:

- The fourteen phases form one continuous end-to-end learning and validation path.
- One file is easier to review, version, rename, and maintain.
- The repository avoids unnecessary file proliferation.
- The full Local AI roadmap remains visible in one place.
- Each phase remains independently executable.
- Codex can load only the current phase, preserving the minimum-context principle defined in `AGENTS.md`.
- The file acts as a practical curriculum rather than fourteen unrelated prompt artifacts.

The important operating rule is:

> One file for the roadmap; one prompt per phase; execute only the current phase.

## Alternatives Considered

### Alternative A — Fourteen Separate Prompt Files

Example:

```text
prompts/
├── local-ai-phase-01-architecture.md
├── local-ai-phase-02-governance.md
├── ...
└── local-ai-phase-14-final-validation.md
```

This was rejected for the current stage because:

- it adds unnecessary repository clutter,
- navigation becomes more fragmented,
- the phases are strongly related,
- maintenance overhead is higher,
- there is no current need for independent lifecycle or ownership of each phase.

### Alternative B — One Single Monolithic Prompt

One file containing one giant prompt that asks Codex to execute all fourteen phases at once was rejected.

Reasons:

- excessive context consumption,
- weak task isolation,
- difficult failure diagnosis,
- unnecessary repository-wide scanning,
- increased risk of unrelated modifications,
- conflicts with the minimum-required-context principle.

The accepted design is therefore one file with fourteen independently executable prompts, not one giant execution prompt.

## Consequences

### Positive

- Clear end-to-end Local AI practice roadmap.
- Low file-management overhead.
- Low repository clutter.
- Each phase can still be executed independently.
- Context usage remains controlled.
- The progression from architecture to final validation is preserved.
- The file can evolve as a practical learning artifact.

### Trade-offs

- The master file may become relatively long.
- Users and AI tools must select the correct phase instead of blindly executing the entire document.
- Mature phases may eventually deserve promotion into canonical skills.

## Implementation

Store the master practice file at:

```text
prompts/EngineeringOS_Local_AI_End_to_End_Practice.md
```

The document SHOULD contain:

```text
Phase 1
    -> objective
    -> Codex prompt
    -> exit criteria

Phase 2
    -> objective
    -> Codex prompt
    -> exit criteria

...

Phase 14
    -> objective
    -> Codex prompt
    -> exit criteria
```

When using the file:

1. Identify the current phase.
2. Provide Codex only the prompt for that phase.
3. Follow `AGENTS.md`.
4. Keep context within the smallest relevant scope.
5. Complete and validate the current phase before moving to the next one.
6. Do not ask Codex to execute all fourteen phases in one request unless performing an explicitly authorized full-system audit.

## Promotion Rule

The master practice file is not a replacement for `skills/`.

If one phase becomes:

- stable,
- reusable,
- operationally important,
- multi-step,
- and repeatedly executed as a canonical workflow,

that phase SHOULD be considered for promotion into the existing EngineeringOS skill system according to project governance.

The practice prompt may then reference the canonical skill rather than duplicating the workflow.

Do not create a second workflow mechanism.

## Validation

Confirm that:

- the file lives under the existing `prompts/` responsibility area,
- no new folder was introduced solely for the roadmap,
- the file contains independent phase prompts,
- project guidance does not require AI tools to load all phases for a single task,
- promoted workflows follow the existing skill governance.

Run the validation required by `AGENTS.md` if adding the ADR or prompt file changes maintained project structure or README/manifest references.

## Change Rule

Split this master file only when one or more phases develop an independent lifecycle, ownership boundary, or canonical workflow responsibility that justifies separation.

Until then, keep the Local AI end-to-end practice as one master file with independently executable phases.
