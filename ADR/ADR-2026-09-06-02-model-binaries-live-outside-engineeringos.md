# ADR: Keep Reusable AI Model Binaries Outside the EngineeringOS Repository

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** Local AI storage ownership

## Context

EngineeringOS originally described `runtime/` as containing model, cache, index, and other local runtime data.

Reusable local LLM, embedding, and ranking model binaries can consume tens or hundreds of gigabytes and have a lifecycle different from project source code and knowledge.

They may also be shared by multiple projects or managed directly by an AI provider such as Ollama.

## Decision

Reusable AI model binaries SHALL NOT be owned by the EngineeringOS repository.

They SHALL NOT be stored under `EngineeringOS/runtime/models` as repository-owned runtime assets.

EngineeringOS `runtime/` SHALL contain project-owned generated state such as:

- indexes,
- caches,
- sessions,
- generated files,
- temporary runtime data.

Physical model binaries SHALL live in provider-owned or infrastructure-owned storage outside the repository.

## Rationale

Model binaries:

- are large,
- are replaceable,
- may be shared,
- are usually managed by the inference provider,
- should not participate in Git or repository backup semantics,
- should be movable without changing EngineeringOS architecture.

## Consequences

### Positive

- EngineeringOS remains small and portable.
- Model storage can move independently.
- Git and repository validation stay clean.
- Provider lifecycle remains separate from knowledge lifecycle.

### Trade-offs

- Local AI setup requires external model storage.
- Provider availability becomes an environmental dependency.

## Implementation

1. Remove any architectural requirement that reusable model binaries live under `runtime/`.
2. Keep only EngineeringOS-owned generated data under `runtime/`.
3. Configure model providers to manage their own model storage.
4. Reference models logically through AI configuration.
5. Add ignore rules where needed so provider caches or local generated data are not accidentally committed.

## Validation

Verify that:

```text
EngineeringOS/runtime/
    -> project-owned generated state only

External/provider storage
    -> reusable model binaries
```

Search the repository for physical model paths and repository-owned model binary directories.

`python eng.py validate` should pass after any structural change required by this decision.

## Change Rule

If a future provider requires repository-local model artifacts, treat that as a new architecture decision rather than silently placing them under `runtime/`.
