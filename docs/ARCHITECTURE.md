# Architecture

Engineering OS follows a modular architecture. Configuration files describe
the modules, while Python provides the execution layer.

```text
User
 |
 v
Python CLI / AI Agent
 |
 +--> Skills ------> Prompts / Tools
 |
 +--> Memory ------> Knowledge Repository
 |
 +--> AI Runtime --> Local AI Model
```

Module boundaries:

- `agents/` contains role-specific orchestration and decides which skills to use.
- `skills/` contains reusable capability workflows. It is the canonical home
  for AI skills and must not duplicate knowledge or prompt content.
- `prompts/` contains reusable prompt fragments and prompt templates.
- `tools/` contains integrations with external systems and utilities.
- `memory/` contains persistent context about the project and its owner.
- `knowledge/` contains source documents and engineering knowledge.
- `runtime/` contains the integration layer for local model runtimes.

The intended execution flow is:

```text
Request -> Agent -> Skill -> Retrieve knowledge/memory -> Call AI Runtime
        -> Validate output -> Return result for human review
```

Every module should remain loosely coupled. A skill should be callable by more
than one agent, and a runtime change should not require changing skill logic.
