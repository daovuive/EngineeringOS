# ADR: Use Minimum-Required Context for Codex Workflows

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** AI-assisted development workflow

## Context

EngineeringOS contains many documentation, knowledge, configuration, skill, and runtime areas.

Forcing Codex to read the root README, governance documents, manifest, and large portions of the repository for every small task wastes context tokens and can reduce focus.

At the same time, architecture and governance rules must remain enforceable when a task crosses structural boundaries.

## Decision

Codex SHALL start from the smallest context sufficient for the authorized task and expand context only when required.

Tasks SHALL be treated broadly as:

### Level 1 — Local Task

Read the target and nearest relevant guidance only.

### Level 2 — Subsystem Task

Read the relevant subsystem README chain, configs, schemas, registries, and directly affected files.

### Level 3 — Architecture/Structural Task

Read the root README, structure governance, manifest, and relevant affected-area documentation.

Repository-wide scans SHALL NOT be the default.

Validation SHALL also begin with the narrowest relevant checks and expand when the change has broader impact.

## Rationale

This reduces:

- token consumption,
- repeated context loading,
- unrelated repository exploration,
- accidental broad refactoring.

It preserves governance because architectural tasks still require global context.

## Consequences

### Positive

- Lower Codex context usage.
- Faster task execution.
- Better focus on relevant files.
- Less accidental modification outside scope.

### Trade-offs

- Codex must classify task scope correctly.
- A task may need to escalate context when hidden dependencies are discovered.

## Implementation

Maintain the decision rules in `AGENTS.md`.

Default workflow:

```text
understand task
    -> identify target
    -> read nearest applicable guidance
    -> inspect minimum files
    -> make smallest correct change
    -> run targeted validation
    -> expand only if evidence requires it
```

Codex SHALL prefer targeted searches for:

- exact filenames,
- symbols,
- config keys,
- registry entries,
- errors,
- directly referenced paths.

Codex SHALL NOT scan unrelated knowledge, skills, career data, ADRs, or documentation merely to become familiar with the repository.

## Validation

A routine local task should not require a full repository scan or automatic root README reload.

A structural task should still execute governance validation, including:

```bash
python eng.py validate
```

when required by `AGENTS.md` and project governance.
