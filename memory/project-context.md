# Engineering OS Project Context

Last updated: 2026-08-08

## Project Identity

Engineering OS is a personal engineering knowledge platform powered by local AI.

It is intended to become a long-term engineering brain that preserves engineering knowledge, architecture decisions, lessons learned, reusable templates, prompts, and AI-assisted workflows across an engineering career.

The primary career objective supported by the project is becoming a Solution Architect.

## Mission

Engineering OS helps engineers:

- Capture and preserve engineering knowledge.
- Record architecture decisions and tradeoffs.
- Organize project experience and lessons learned.
- Reuse engineering assets.
- Accelerate engineering work with local AI.
- Support continuous learning and architecture thinking.

## Scope

Core responsibilities:

- Knowledge management.
- Architecture knowledge repository.
- Engineering standards.
- Requirement analysis.
- ADR management.
- Lessons learned.
- Project knowledge.
- Prompt management.
- AI agent management.
- Local AI runtime integration.
- Semantic search, indexing, and RAG.

Explicit non-goals:

- It is not a source code repository.
- It is not a project management tool.
- It is not a CI/CD platform.
- It does not replace Git, Jira, or Confluence.
- It should integrate with those tools instead.

## Design Principles

- Knowledge first: engineering knowledge is the primary asset.
- Architecture first: decisions and rationale should outlive technologies.
- Local AI first: privacy, offline capability, lower cost, vendor independence, and control.
- Human in control: AI assists, engineers decide.
- Configuration as data: automation and agents read configuration files instead of hard-coded structure.
- Single source of truth: `configs/project-structure.json` defines the repository structure.

## Current Architecture

High-level flow:

```text
Engineering CLI
  -> Configuration and Automation
  -> Knowledge Platform + AI Platform
  -> Engineering Services
```

Current CLI entrypoint:

- `eng.py`: primary Python CLI.

Current implemented commands:

- `init`
- `validate`
- `sync`
- `config`
- `doctor`
- `version`
- `help`

Business logic lives under `engineering_os/`.

`scripts/` is retained as a placeholder/documentation folder only.

## Current Repository Shape

Important folders:

- `ADR`: architecture decision records.
- `agents`: AI agent definitions.
- `configs`: project, runtime, and settings configuration.
- `docs`: project documentation.
- `knowledge`: engineering knowledge repository.
- `memory`: persistent AI memory.
- `prompts`: prompt library.
- `scripts`: automation scripts.
- `templates`: file templates.
- `tests`: tests.
- `tools`: external tools.

Important configuration:

- `configs/project-structure.json`: intended single source of truth for folder/file structure.
- `configs/settings.json`: project settings, logging, knowledge, memory, agents, prompts, and runtime config paths.
- `configs/ai-runtime.json`: local AI runtime definitions and model defaults.

Current runtime defaults:

- Default runtime: `ollama`.
- Chat model: `qwen3:8b`.
- Reasoning model: `qwen3:14b`.
- Coding model: `qwen2.5-coder:14b`.
- Embedding model: `nomic-embed-text`.

## Roadmap Snapshot

- Sprint 1: foundation, local CLI, Ollama.
- Sprint 2: Open WebUI, local chat.
- Sprint 3: knowledge base, RAG.
- Sprint 4: engineering agent.
- Sprint 5: solution architect agent.

## Current Notes

- Python is now the primary CLI runtime per ADR-0003.
- All PowerShell scripts were removed to avoid maintaining duplicate CLI implementations.
- The project now validates successfully through `python eng.py validate`.

## Known Gaps To Address

- The README describes semantic search, indexing, and RAG, but no implementation is visible yet.
- Future work should keep all structure validation driven by `configs/project-structure.json`.
- Ollama is optional in `doctor`; it is currently not installed or not on PATH in this machine.

## Recommended Next Implementation Order

1. Define a document schema for knowledge entries, ADRs, lessons learned, prompts, and agent definitions.
2. Add an indexing pipeline for Markdown first, then expand to PDF, DOCX, HTML, and source code.
3. Add a local vector store abstraction that is independent from the AI runtime.
4. Add concrete agent specs for requirement analysis, architecture review, code review, summarization, and Solution Architect workflows.
