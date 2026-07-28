# Engineering OS

> Personal Engineering Knowledge Platform powered by Local AI.

---

# Vision

Engineering OS is a Personal Engineering Knowledge Platform and AI Operating System.

Its purpose is to preserve engineering knowledge, architecture decisions, design experience, lessons learned and reusable assets throughout an engineering career.

The platform is designed to become a long-term Engineering Brain that continuously grows with its owner.

The primary career objective supported by Engineering OS is becoming a Solution Architect.

---

# Mission

Engineering OS helps engineers:

- Capture engineering knowledge
- Preserve architecture decisions
- Organize project experience
- Learn from previous work
- Reuse engineering assets
- Accelerate engineering tasks using Local AI

---

# Objectives

The platform should:

- Preserve knowledge permanently
- Reduce repeated work
- Improve engineering productivity
- Improve architecture thinking
- Build reusable engineering assets
- Support continuous learning
- Support AI-assisted engineering workflows

---

# Scope

Engineering OS is responsible for:

- Knowledge Management
- Architecture Knowledge
- Engineering Standards
- Requirement Analysis
- Architecture Decision Records (ADR)
- Lessons Learned
- Project Knowledge
- Prompt Management
- AI Agent Management
- Local AI Runtime Integration
- Semantic Search
- Retrieval Augmented Generation (RAG)

---

# Non-Goals

Engineering OS is NOT intended to become:

- A source code repository
- A project management tool
- A CI/CD platform
- A replacement for Git
- A replacement for Jira
- A replacement for Confluence

Engineering OS integrates with these tools instead of replacing them.

---

# Design Principles

## Knowledge First

Knowledge is the primary asset.

Engineering knowledge should be accumulated, categorized, searchable and reusable.

---

## Architecture First

Architecture decisions are more valuable than implementation details.

Architecture knowledge should outlive technologies and frameworks.

---

## Local AI First

Engineering OS primarily works with Local AI.

Benefits include:

- Privacy
- Offline capability
- Lower operating cost
- Vendor independence
- Full control of engineering knowledge

---

## Human in Control

AI assists.

Engineers make the final decisions.

---

## Configuration as Data

Project structure, templates and runtime configuration are stored as configuration files.

Automation scripts and AI Agents read configuration instead of hard-coded logic.

---

## Single Source of Truth

Project structure is defined only once.

```
configs/project-structure.json
```

All automation must use this manifest.

---

# Functional Requirements

Engineering OS should provide:

- Knowledge Repository
- Architecture Repository
- Standards Repository
- ADR Repository
- Lessons Learned Repository
- Requirement Repository
- Prompt Library
- AI Agent Library
- Local AI Runtime
- Engineering Templates
- Semantic Search
- Document Indexing
- RAG
- Requirement Analysis
- Architecture Review
- Code Review
- Document Summarization
- Meeting Summarization

---

# Supported Knowledge Sources

The platform should support importing:

- Markdown
- PDF
- DOCX
- TXT
- HTML
- Web Pages
- JSON
- YAML
- XML
- CSV
- Excel
- PlantUML
- Mermaid
- Draw.io
- Images
- Source Code
- Git Repositories

Future integrations:

- Jira
- Confluence
- AUTOSAR ARXML
- Enterprise Architect
- OpenAPI

---

# AI Runtime

Engineering OS is AI Runtime independent.

Supported runtimes may include:

- Ollama
- llama.cpp
- LM Studio
- vLLM

Changing AI runtime should not require changing the repository architecture.

---

# High-Level Architecture

```
                 Engineering OS

                       │

                 Engineering CLI

                       │

          Configuration & Automation

                       │

     +-----------------+------------------+

     |                                    |

 Knowledge Platform                 AI Platform

     |                                    |

 Knowledge Repository             AI Agents

 ADR Repository                   Local AI Runtime

 Standards                         Embedding Models

 Lessons Learned                   Vector Database

     |                                    |

     +-----------------+------------------+

                       │

                 Engineering Services
```

---

# Repository Layout

The repository structure is generated from:

```
configs/project-structure.json
```

This file is the single source of truth.

Automation scripts and AI Agents should never assume folder names.

---

# Long-Term Vision

Engineering OS should become a lifelong engineering companion that continuously accumulates engineering knowledge, architecture decisions and practical experience.

Its value should increase over time as more knowledge is collected and reused.
