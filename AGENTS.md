# EngineeringOS AI Entrypoint

This file defines how AI tools should enter, navigate, and modify EngineeringOS.

The goal is to preserve architectural governance while minimizing unnecessary
context loading, repository scanning, and repeated token consumption.

AI should use the smallest context sufficient to complete the authorized task
correctly.

---

## Core Operating Rule

Start narrow and expand context only when required.

Do not scan, summarize, or preload the entire repository by default.

Use this progression:

```text
Understand the task
    -> identify the target area
    -> read the nearest applicable guidance
    -> inspect the minimum required files
    -> make the smallest correct change
    -> run targeted validation
    -> expand context only if evidence requires it
```

Repository-wide context is required for architectural or structural changes, but
should not be loaded automatically for routine local work.

---

## Context Levels

Classify the task before reading project files.

### Level 1 — Local Task

Use for changes limited to a known file, symbol, test, or small implementation
area.

Examples:

- fix a function,
- update a test,
- correct a configuration parser,
- change a prompt,
- edit an existing knowledge note,
- fix a typo or broken link,
- modify a known skill implementation without changing its contract.

Default context:

1. Read the target file.
2. Read the nearest applicable `README.md` if placement or local rules matter.
3. Read directly related tests, configs, or referenced files only when required.

Do not automatically read:

- root `README.md`,
- all architecture documents,
- all ADRs,
- all skills,
- all agents,
- all knowledge,
- all career data,
- the entire manifest,
- unrelated sibling READMEs.

Expand scope only when the task cannot be completed safely from local context.

---

### Level 2 — Subsystem Task

Use when a change affects multiple files within one established responsibility
area.

Examples:

- changes under `configs/ai/`,
- extending one skill package,
- modifying the EngineeringOS runtime abstraction,
- changing several files under `knowledge/architect/`,
- updating a local registry and its implementation together.

Read:

1. The README of the relevant top-level area.
2. The README chain from that area down to the target.
3. Relevant registry, schema, or configuration files.
4. Files directly participating in the change.

Read the root README or structure governance only if:

- the local rules refer to them for the decision being made,
- a responsibility boundary is unclear,
- a structural conflict is discovered,
- or the task begins to affect repository-wide architecture.

Do not inspect unrelated subsystems.

---

### Level 3 — Architecture or Structural Task

Use when the task may change repository-wide structure, ownership, governance,
or architectural contracts.

Examples:

- adding a top-level directory,
- moving responsibility between top-level areas,
- changing root allowlists,
- changing governance behavior,
- changing manifest structure,
- introducing a second configuration mechanism,
- modifying the root README,
- changing protected architecture baselines.

Before making changes:

1. Read [root README](README.md).
2. Read [structure governance](docs/STRUCTURE_GOVERNANCE.md).
3. Read [manifest](configs/project-structure.json).
4. Read the README chain for every affected area.
5. Read relevant ADRs or architecture documents when the decision depends on
   them.

Architecture tasks may require broader context, but still should not trigger an
unrelated full-repository scan.

---

## File Placement and Structural Changes

Before creating, moving, deleting, or relocating maintained project content:

1. Identify the responsibility area that should own the content.
2. Read the nearest README governing that destination.
3. Check the manifest when the operation changes maintained structure.
4. Follow the nearest README's placement rules.
5. Surface conflicts before changing architecture.

For routine edits to an existing file in a known location, do not reload the
entire structural governance chain unless the change affects placement,
ownership, or architecture.

New maintained directories must follow the applicable governance rules,
including README, manifest, registry, and parent-link requirements where
required.

Do not create new structural mechanisms merely because they are convenient for
the current task.

---

## Skills and Reusable Workflows

For reusable workflows, consult [skills](skills/README.md) and the
[skill registry](configs/skills.json) when the current task actually involves a
skill or reusable workflow.

If a matching skill exists:

- read the matching `SKILL.md`,
- reuse its canonical workflow,
- do not invent a parallel workflow,
- do not duplicate its instructions into agents, prompts, or knowledge.

Do not read the complete skills tree for unrelated coding or documentation
tasks.

Architect learning currently uses the
[learning entrypoint](knowledge/architect/README.md).

A new teaching skill remains a separate proposal unless explicitly authorized.

Keep one canonical workflow per skill.

---

## Knowledge and Source Ownership

Keep one primary source for each piece of knowledge.

Prefer links and references over duplication.

Do not copy authoritative content between:

- `knowledge/`,
- `career/`,
- `memory/`,
- `skills/`,
- `agents/`,
- `prompts/`,
- documentation,
- or configuration

unless the destination explicitly requires a derived representation.

Read knowledge, career, memory, ADRs, or documentation only when the current
task depends on that information.

Do not preload these areas for routine implementation work.

---

## Search and Repository Exploration

Prefer targeted search over broad exploration.

Search for:

- exact filenames,
- symbols,
- configuration keys,
- registry entries,
- error messages,
- referenced paths,
- tests,
- or explicit concepts.

Avoid recursive inspection of unrelated directories.

Do not use broad commands or repository-wide analysis merely to become familiar
with the project before a narrow task.

When discovery is necessary:

```text
exact target
    -> local references
    -> subsystem references
    -> repository-wide references only if required
```

Stop expanding context once sufficient evidence has been found.

---

## Modification Rules

Apply only the authorized task.

Do not opportunistically:

- refactor unrelated code,
- rename unrelated files,
- reorganize directories,
- rewrite documentation outside scope,
- change architectural policy,
- widen exclusions,
- suppress validation,
- or clean up unrelated issues.

If unrelated problems are discovered, report them separately unless fixing them
is required to complete the authorized task.

Prefer the smallest correct change.

---

## Validation Strategy

Validation should also start narrow.

For a local change:

1. Run the smallest relevant test, lint check, parser check, or command.
2. Expand validation only when the change has broader impact.

For subsystem changes:

1. Run subsystem-specific checks.
2. Run dependent tests when relevant.
3. Run repository-wide validation if the subsystem participates in structural
   rules.

For structural or architectural changes, run:

```bash
python eng.py validate
```

and any other checks required by the affected area.

Run `python eng.py validate` whenever required by governance or when the change
can affect repository structure, manifests, registries, README hierarchy, or
protected rules.

Do not change policy, disable governance checks, or widen exclusions merely to
make validation pass.

Report remaining violations instead.

---

## Root README Protection

The root `README.md` is protected.

Do not:

- edit it,
- replace it,
- rename it,
- delete it,
- or rebase its SHA-256 baseline

without the user's explicit approval of the specific proposed root change.

Broad requests to:

- clean up,
- synchronize,
- improve,
- refactor,
- extend,
- or modernize

the project do not grant permission to modify the root README.

When a root-level architectural change appears necessary, prepare a concrete
proposal under:

```text
docs/proposals/
```

before modifying the protected root charter.

The root navigation migration was approved by the user and applied on
2026-09-05.

`README.md` is the active charter.

Archived proposals are not alternate policies.

---

## Configuration and Environment-Specific Values

Follow the project's Configuration-as-Data principle.

Do not hard-code machine-specific paths, model locations, provider details, or
host-specific values into architectural documentation when they belong in
configuration.

AI-specific runtime and model configuration should follow the rules defined by
the relevant configuration area, including `configs/ai/` when applicable.

Physical infrastructure may change without changing architectural policy.

Do not modify stable architecture documentation merely because:

- a model moved,
- a disk changed,
- a provider changed,
- a cache location changed,
- a machine changed,
- or a runtime endpoint changed.

Update the appropriate configuration instead.

---

## Prompt and Context Efficiency

Stable project rules belong in repository documentation, not repeated task
prompts.

A normal Codex task should usually need only:

```text
Goal
Target area or files
Important constraints
Expected behavior
Validation
```

Do not require the user to restate architecture already represented by project
files.

Likewise, do not repeatedly summarize large project documents back into the
working context unless the task depends on their exact content.

Prefer references over copied context.

---

## Reporting

Final task reports should be concise.

Normally report only:

- what changed,
- which files changed,
- validation performed,
- important architectural implications,
- unresolved violations or risks.

Do not provide large summaries of files that were merely read.

Do not restate project-wide architecture after every local task.

---

## Default Decision Flow

Use the following decision process:

```text
Is the target already known?
    |
    +-- yes --> inspect target + nearest relevant guidance
    |
    +-- no --> targeted search for target
                 |
                 v
        Does the task remain inside one established area?
                 |
          +------+- yes --> stay within subsystem context
          |
          +-- no / unclear
                 |
                 v
        read root README + governance + manifest
                 |
                 v
        resolve architectural boundary
```

For implementation:

```text
minimum context
    -> minimum change
    -> minimum relevant validation
    -> expand only when necessary
```

---

## Governance Priority

When instructions conflict, apply the more authoritative project source.

In general:

```text
root README / approved governance
    -> manifest and schemas
    -> top-level README
    -> nearest child README
    -> registry / skill contract
    -> task-specific implementation detail
```

Surface genuine conflicts rather than silently choosing whichever rule is most
convenient.

These instructions route AI tools to project documents.

They do not replace those documents, create alternate policies, or promise that
every AI tool automatically reads this file.