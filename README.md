# EngineeringOS

> Personal Engineering Knowledge Platform powered by Local AI.

## Role of the Root README

This file is the stable constitution of EngineeringOS. It defines the project's purpose, vision, architectural principles, responsibility boundaries, and high-level structure.

Do not modify, replace, rename, or remove this file unless the project owner explicitly approves the specific proposed change.

Routine additions of documents, skills, configurations, tools, or knowledge within an existing responsibility boundary should be handled through the nearest child README and do not require changes to this constitution.

Detailed structural governance is defined in [Structure Governance](docs/STRUCTURE_GOVERNANCE.md).

AI systems begin from this file, read the project manifest, and then follow the README hierarchy toward the relevant responsibility area.

---

## Purpose and Vision

EngineeringOS preserves and organizes engineering knowledge, design experience, architecture decisions, lessons learned, and reusable assets accumulated throughout a professional career.

The value of the platform increases when knowledge can be:

- retrieved reliably,
- traced back to its source,
- evaluated in context,
- connected to previous decisions,
- and reused in future engineering work.

EngineeringOS supports progression from engineering foundations and Feature Ownership toward Solution Architecture by combining:

- continuous learning,
- systems thinking,
- structured decision-making,
- architecture practice,
- evidence-based reasoning,
- and Local AI.

Detailed career direction is maintained under [career](career/README.md).

---

## Scope

EngineeringOS is responsible for:

- Managing engineering knowledge, standards, requirements, architecture, and Architecture Decision Records.
- Supporting continuous architecture learning, exercises, progress tracking, and experience capture.
- Analyzing engineering work and career development using evidence from real sources.
- Reusing skills, prompts, templates, tools, and AI agent roles.
- Using Local AI to search, analyze, connect, and reason over engineering knowledge.
- Providing a stable runtime abstraction so AI providers and models can evolve without redesigning the knowledge repository.

EngineeringOS does **not** replace:

- Git,
- Jira,
- Confluence,
- CI/CD systems,
- source repositories for unrelated software projects,
- or general-purpose infrastructure management.

Code required to operate EngineeringOS itself belongs to its dedicated implementation module.

External integrations are introduced only when there is a clear need, responsibility boundary, and maintenance rationale.

---

## Architectural Principles

### 1. Knowledge First

Preserve sources, context, reasoning, decisions, and long-term retrievability.

Knowledge should remain understandable independently of the AI model or tool currently used to access it.

### 2. Architecture First

Start from:

- the problem,
- stakeholders,
- requirements,
- constraints,
- quality attributes,
- evidence,
- and trade-offs.

Technology choices follow architecture reasoning rather than replacing it.

### 3. Local AI First

Prefer privacy, data control, local execution, and replaceable AI providers.

EngineeringOS must not depend on one specific model, model vendor, provider, runtime, or filesystem layout.

The AI runtime boundary must allow providers and models to change without redesigning the knowledge repository.

### 4. Human in Control

AI assists with reasoning, retrieval, analysis, organization, and execution.

The human owner remains responsible for:

- architectural direction,
- important structural changes,
- final decisions,
- interpretation of professional experience,
- and approval of protected baselines.

AI must not convert assumptions, generated content, or intended goals into claimed real-world experience.

### 5. Configuration as Data

Project structure, runtime behavior, registries, AI bindings, and environment-independent settings should be declared as data rather than hard-coded into application logic.

Machine-specific details must remain outside architectural documentation.

Physical paths, provider installation details, ports, model storage locations, and host-specific settings must be configurable without modifying this root README.

Avoid creating multiple competing configuration mechanisms for the same responsibility.

### 6. One Primary Source per Concept

Each piece of information should have one authoritative source.

Link and reuse instead of duplicating content across:

- knowledge,
- career,
- memory,
- skills,
- agents,
- prompts,
- and documentation.

### 7. Stable Architecture, Replaceable Infrastructure

Stable concepts should be separated from replaceable infrastructure.

In particular:

- knowledge should not depend on a specific model,
- model identity should not depend on a physical filesystem path,
- AI behavior should not depend on one provider,
- runtime state should not become permanent knowledge,
- and machine-specific configuration should not become architecture.

### 8. Maintainability over Accidental Complexity

Prefer maintainability, extensibility, reliability, findability, traceability, and clear responsibility boundaries.

New mechanisms should only be introduced when an existing mechanism cannot reasonably support the requirement.

---

## Responsibility Model

```text
User / AI
    |
    v
Read root README
    |
    v
Read project manifest
    |
    v
Follow README hierarchy to the relevant area
    |
    v
Agent coordinates roles when needed
    |
    v
Skill executes a reusable workflow
    |
    +--> career / knowledge / memory provide context and evidence
    |
    +--> prompts / tools / templates provide reusable support
    |
    +--> configs provide declarative configuration
    |
    +--> engineering_os provides CLI and runtime abstractions
    |
    +--> AI provider/model bindings resolve through configs/ai
    |
    +--> runtime / logs contain generated local state
    |
    v
Validate result
    |
    v
Return result to the user
```

This describes responsibility boundaries.

It does not imply that every component is fully automated.

The currently implemented architecture is documented in [Architecture](docs/ARCHITECTURE.md).

Planned development is maintained in [Roadmap](docs/ROADMAP.md).

---

## Project Structure and Content Ownership

The [Project Structure Manifest](configs/project-structure.json) is the machine-readable inventory of the repository.

The following table is a stable map of high-level responsibilities. It is not an
exhaustive index of every folder or file in the repository.

The manifest is the authoritative machine-readable inventory. Do not add a row
or link to any README for each new folder or file. Add new content to the
nearest responsibility area and update its README only when the responsibility,
local rules, or retrieval boundary changes. Update this root README only when a
responsibility boundary or another stable architectural contract changes.

Each child README defines:

- what belongs in that area,
- what does not belong there,
- its primary sources,
- extension rules,
- and relationships with neighboring areas.

| Directory | Responsibility |
| --- | --- |
| [ADR/](ADR/README.md) | Architecture Decision Records for EngineeringOS itself. |
| [docs/](docs/README.md) | Operational, architectural, governance, and project documentation for EngineeringOS. |
| [career/](career/README.md) | Career direction, competency planning, evidence of real experience, development plans, and market references. |
| [templates/](templates/README.md) | Reusable artifact templates used across EngineeringOS workflows. |
| [scripts/](scripts/README.md) | Supporting operational scripts used by EngineeringOS when scripting is justified. |
| [configs/](configs/README.md) | Configuration as data: project manifest, schemas, runtime settings, AI configuration, registries, and other declarative system configuration. |
| [agents/](agents/README.md) | AI role definitions, coordination rules, responsibilities, and delegation boundaries. |
| [runtime/](runtime/README.md) | Generated EngineeringOS runtime state such as caches, indexes, sessions, temporary files, and other rebuildable local execution data. Reusable model binaries are not owned by this directory. |
| [memory/](memory/README.md) | Long-term project context represented as dated, source-aware notes. |
| [logs/](logs/README.md) | Logs generated by EngineeringOS tools and runtime processes. |
| [tests/](tests/README.md) | Tests for CLI behavior, modules, configuration, and EngineeringOS system behavior. |
| [experiments/](experiments/README.md) | Bounded experiments with explicit hypotheses, execution methods, observations, and results. |
| [prompts/](prompts/README.md) | Reusable prompts and prompt fragments. |
| [tools/](tools/README.md) | External integrations and supporting tools used by EngineeringOS. |
| [engineering_os/](engineering_os/README.md) | EngineeringOS Python implementation: CLI, configuration loading, structure management, validation, runtime abstraction, and knowledge search. |
| [skills/](skills/README.md) | Primary source for reusable AI workflows. |
| [knowledge/](knowledge/README.md) | Accumulated engineering and architecture knowledge. |

The repository root is intentionally minimal.

It contains only files allowed by the root allowlist defined in the project manifest, including:

```text
README.md
AGENTS.md
eng.py
pyproject.toml
LICENSE
.gitignore
```

New content must belong to an existing responsibility area whenever possible.

A new top-level directory must still be registered in the manifest and contain
its own README, but it does not require a new row or link in this file. A new
top-level responsibility boundary requires explicit architectural review; a
folder or file within an existing boundary does not.

---

## AI Configuration Boundary

EngineeringOS treats AI models as replaceable infrastructure rather than repository-owned knowledge.

The repository owns:

- logical model identities,
- AI role bindings,
- provider definitions,
- runtime behavior,
- model selection rules,
- configuration schemas,
- and integration logic.

The repository does **not** require reusable model binaries to reside inside the EngineeringOS directory.

Physical model storage may change independently from the repository.

For example, models may be stored on:

- the local Linux filesystem,
- another local disk,
- a dedicated model volume,
- network-attached storage,
- a provider-managed store,
- or another runtime-specific location.

EngineeringOS must resolve these locations through configuration rather than architectural documentation.

AI-specific configuration belongs under:

```text
configs/ai/
```

A typical responsibility split is:

```text
configs/
└── ai/
    ├── README.md
    ├── models.json
    ├── providers.json
    ├── runtime.json
    └── local.env
```

Conceptually:

```text
models.json
    -> logical model identities and roles

providers.json
    -> provider definitions and provider capabilities

runtime.json
    -> AI runtime behavior and bindings

local.env
    -> machine-specific values when required
```

Machine-specific configuration such as physical paths should not be committed when it is specific to one host.

Such files must be protected through `.gitignore` when appropriate.

The exact filenames and schemas are governed by the README and schemas inside `configs/ai/`, not by this root document.

---

## Logical Models vs Physical Storage

EngineeringOS distinguishes between a **logical model reference** and a **physical model location**.

For example, EngineeringOS may conceptually refer to:

```text
primary_llm
embedding_model
reranker
coding_model
```

These names describe responsibilities.

They do not define where model files are stored.

A logical binding may resolve to:

```text
primary_llm
    -> provider: Ollama
    -> model: <provider model identifier>
```

or:

```text
embedding_model
    -> provider: Hugging Face compatible runtime
    -> model: <model identifier>
```

The provider layer is responsible for resolving the model to its actual runtime representation.

This separation ensures that changes such as:

- moving models to another disk,
- replacing a disk,
- moving from WSL to native Linux,
- introducing shared model storage,
- switching from Ollama to llama.cpp,
- switching from llama.cpp to vLLM,
- changing model formats,
- or replacing one model family with another

do not require changes to this root README.

Ideally, machine-level changes should require modification only to the relevant environment-specific configuration.

---

## Runtime Boundary

The `runtime/` directory contains state generated by operating EngineeringOS.

Typical examples include:

```text
runtime/
├── cache/
├── indexes/
├── sessions/
├── generated/
└── temporary/
```

Runtime state should generally be:

- reproducible,
- regeneratable,
- local,
- implementation-oriented,
- and separate from authoritative knowledge.

Reusable model binaries are intentionally outside this ownership boundary.

A model may be used by EngineeringOS without becoming part of the EngineeringOS repository.

Similarly, runtime indexes derived from knowledge are not themselves the authoritative knowledge source.

The original knowledge remains authoritative.

---

## Skills and Agents

[Skills](skills/README.md) are the primary source for reusable AI workflows.

Each skill uses:

```text
skills/<skill-id>/SKILL.md
```

as its primary workflow definition and is registered through the appropriate skill registry under `configs/`.

Skills may read from:

- `career/`,
- `knowledge/`,
- `memory/`,
- configuration,
- and other approved sources.

Skills must not create independent copies of authoritative data unless explicitly required by their workflow.

[Agents](agents/README.md) define:

- AI roles,
- responsibilities,
- coordination behavior,
- delegation rules,
- and boundaries between roles.

Agents reference reusable skills rather than copying skill workflows into agent definitions.

Skill-specific helper code belongs inside the skill package when it is not generally reusable elsewhere.

---

## Architecture Learning

When working on Solution Architecture learning, begin from:

[Architect Knowledge](knowledge/architect/README.md)

That area provides the architecture learning structure, roadmap, exercises, progress references, and supporting knowledge.

The AI should inspect the relevant learning state before selecting or generating the next activity.

---

## Career Work

Career-related requests begin from:

[Career](career/README.md)

Career information should distinguish clearly between:

- verified real experience,
- goals,
- inferred capabilities,
- learning activities,
- market evidence,
- and AI-generated suggestions.

AI must not present a target capability or generated scenario as historical experience.

---

## Extension Workflow

When extending EngineeringOS:

1. Read this root README.
2. Read the project structure manifest.
3. Read the structural governance rules.
4. Follow the README hierarchy from parent to target directory.
5. Search for an existing primary source before creating new content.
6. Select a location based on responsibility rather than convenience.
7. Add or update a README only when its responsibility, local rules, or
   retrieval boundary changes; do not add routine file or folder entries.
8. Register new structural elements in the appropriate manifest or registry.
9. Keep links synchronized when moving or renaming content.
10. Do not modify protected architectural baselines without explicit approval.
11. Run:

```bash
python eng.py validate
```

12. Review validation results and report any remaining limitations.

A new directory should generally include:

- a clear responsibility,
- a README when required by structural rules,
- a manifest entry when applicable,
- and a parent link.

A new skill should include:

- its `SKILL.md`,
- required supporting files,
- and the appropriate registry entry.

---

## Structural Change Policy

Not every repository change is an architectural change.

Changes inside an existing responsibility boundary can normally proceed through the local governance defined by that area's README.

Examples include:

- adding a new knowledge note,
- adding an architecture exercise,
- adding a prompt,
- adding a skill inside the existing skills system,
- adding a provider configuration,
- adding a model binding,
- adding a template,
- or adding a test.

Changes that alter high-level responsibility boundaries require architectural review.

Examples include:

- adding a new top-level directory,
- changing the ownership of an existing top-level directory,
- moving authoritative knowledge into runtime state,
- introducing a second configuration mechanism,
- changing the repository's architectural purpose,
- or modifying the principles defined in this README.

---

## Stability Expectations

This README is intentionally designed to change rarely.

Routine changes should happen below this level.

The following should **not** require modification of this file:

- changing the primary LLM,
- adding an embedding model,
- adding a reranker,
- moving model files,
- changing model storage disks,
- changing host machines,
- changing WSL distributions,
- switching between local AI providers,
- changing provider endpoints,
- changing model formats,
- rebuilding indexes,
- changing cache locations,
- introducing new skills,
- adding new engineering knowledge,
- or updating career plans.

Those changes belong to their respective configuration or responsibility areas.

This file should change only when the project's fundamental architectural contract changes.

---

## Documentation Hierarchy

EngineeringOS documentation follows a hierarchical responsibility model.

```text
README.md
    |
    +--> docs/
    |
    +--> configs/
    |      |
    |      +--> ai/
    |
    +--> knowledge/
    |
    +--> career/
    |
    +--> skills/
    |
    +--> agents/
    |
    +--> runtime/
    |
    +--> ...
```

The root README defines stable boundaries.

Child READMEs define local rules.

Configuration files define variable behavior.

Runtime state records execution.

Knowledge remains the authoritative long-term information source.

---

## Extended Documentation

- [Structure Governance](docs/STRUCTURE_GOVERNANCE.md)
- [Current Architecture](docs/ARCHITECTURE.md)
- [Operations and Validation](docs/OPERATIONS.md)
- [Initial Architecture Context and Exercises](docs/ARCHITECTURE_CONTEXT.md)
- [Project Documentation and Roadmap](docs/README.md)
- [Architecture Decision Records](ADR/README.md)

---

## Core Architectural Rule

When deciding where something belongs, ask:

> Is this architecture, configuration, authoritative knowledge, reusable workflow, implementation, or generated runtime state?

Then place it in the area responsible for that category.

Do not place content according to whichever location is easiest for the current tool.

EngineeringOS should remain understandable, maintainable, and portable even when its AI models, providers, machines, storage devices, and supporting tools change.
