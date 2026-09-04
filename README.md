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
- Reusable AI Skill Library
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

# AI Skills

AI Skills are reusable workflows used by AI Agents. A skill defines how a
capability is performed, its inputs and outputs, quality checks, and references
to source knowledge. Skills contain workflow instructions; they do not duplicate
knowledge documents, prompts, or agent definitions.

Agents orchestrate skills. Skills use prompts, tools, memory and knowledge as
needed. This separation allows the same skill to be reused by multiple agents.

---

# CLI Runtime

Engineering OS uses Python as the primary CLI and automation runtime.

Common commands:

```bash
python eng.py init
python eng.py sync
python eng.py validate
python eng.py doctor
python eng.py config
```

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


## EngineeringOS — System Context, Requirements, Quality & Constraints

> Goal: practice thinking like an Architect by starting from purpose, stakeholders, requirements, quality attributes, and constraints — before choosing technologies.

---

## 1. EngineeringOS tồn tại để giải quyết vấn đề gì?

### Answer

**EngineeringOS là một Personal Engineering Knowledge Platform + AI Operating System**, được xây dựng để hỗ trợ mục tiêu dài hạn trở thành Architect.

Nó giải quyết một vấn đề chính:

> Kiến thức, kinh nghiệm, architecture decisions và lessons learned của một kỹ sư thường bị phân tán trong nhiều project, tài liệu, cuộc họp và trí nhớ cá nhân. EngineeringOS tập hợp, cấu trúc và biến chúng thành một knowledge base mà Local AI có thể sử dụng để hỗ trợ việc học, phân tích hệ thống, ra quyết định và tự động hóa công việc.

EngineeringOS không chỉ là chatbot.

Nó hướng tới:

```text
Knowledge
    +
Experience
    +
Architecture Decisions
    +
Learning
    +
Local AI
    +
Automation
    ↓
Personal Engineering Operating System
```

### Core outcomes

- Tích lũy kiến thức Architecture.
- Lưu kinh nghiệm thực tế từ nhiều project.
- Lưu ADR, Lessons Learned và Architecture Notes.
- Hỗ trợ tài liệu iSAQB, ISO 26262, AUTOSAR, ASPICE và các nguồn khác.
- Hỗ trợ nhiều định dạng tài liệu.
- Cho Local AI truy cập và sử dụng knowledge.
- Hỗ trợ Architect Learning.
- Về sau hỗ trợ daily-work automation, interview preparation, meetings và engineering tasks.

---

# 2. Ai là 3–5 stakeholders quan trọng?

## 1. The Engineer / Architect — Primary User

Đây là stakeholder quan trọng nhất.

Mục tiêu:
- học Architecture;
- lưu và truy xuất kiến thức;
- phân tích architecture;
- ghi lại decisions;
- sử dụng AI để hỗ trợ công việc;
- tích lũy kinh nghiệm theo thời gian.

## 2. Local AI Agent

Local AI là consumer/operator của EngineeringOS.

Nó cần:
- đọc knowledge;
- tìm kiếm tài liệu;
- hiểu context;
- tạo notes/lessons/ADR;
- hỗ trợ analysis;
- thực hiện automation trong phạm vi được cho phép.

## 3. Project / Engineering Team

EngineeringOS có thể nhận knowledge từ nhiều project.

Team cần:
- architecture decisions rõ ràng;
- lessons learned;
- documentation;
- knowledge có thể tái sử dụng.

## 4. Future Self

Đây là stakeholder đặc biệt nhưng rất quan trọng.

EngineeringOS phải giúp "future self" tìm lại:
- tại sao một decision được đưa ra;
- đã gặp vấn đề gì;
- đã học được gì;
- pattern nào đã được sử dụng;
- kinh nghiệm nào có thể áp dụng lại.

## 5. Knowledge / Standard Sources

Các nguồn như:
- iSAQB
- ISO 26262
- AUTOSAR
- ASPICE
- architecture books
- project documents

là nguồn đầu vào cho knowledge system.

---

# 3. Five Functional Requirements

## FR-01 — Knowledge Ingestion

EngineeringOS phải cho phép thêm và quản lý nhiều loại tài liệu.

Ví dụ:

```text
PDF
DOCX
HTML
TXT
MD
JSON
Excel
PlantUML
Web links
```

Mục tiêu là không khóa knowledge vào một format duy nhất.

---

## FR-02 — Knowledge Organization

EngineeringOS phải tổ chức knowledge theo các nhóm có ý nghĩa.

Ví dụ:

```text
standards/
learning/
architecture/
automotive/
projects/
```

Trong đó có thể lưu:
- iSAQB learning;
- ISO 26262;
- Architecture patterns;
- project knowledge;
- personal engineering experience.

---

## FR-03 — Architecture Knowledge Management

EngineeringOS phải cho phép tạo và quản lý:

```text
ADR
Architecture Notes
Lessons Learned
Architecture Diagrams
Trade-offs
```

Các artifacts này phải có thể version bằng Git.

---

## FR-04 — Local AI Access

Local AI phải có khả năng đọc và sử dụng knowledge của EngineeringOS.

Luồng mục tiêu:

```text
User
  ↓
Local AI
  ↓
Knowledge / Memory
  ↓
Reasoning
  ↓
Answer / Artifact / Action
```

AI không chỉ trả lời dựa trên model knowledge mà phải có khả năng sử dụng engineering knowledge đã tích lũy.

---

## FR-05 — Engineering Assistance & Automation

EngineeringOS về sau phải hỗ trợ các tác vụ như:

```text
Architect Learning
Meeting preparation
Interview preparation
Daily task support
Requirement analysis
Architecture review
Documentation
Knowledge maintenance
```

Automation phải được phát triển sau khi foundation và knowledge architecture ổn định.

---

# 4. Five Quality Requirements

Đây là phần quan trọng nhất về Architect mindset.

Không chỉ hỏi:

> "EngineeringOS làm được gì?"

Mà phải hỏi:

> "EngineeringOS phải làm tốt như thế nào?"

iSAQB nhấn mạnh rằng quality requirements có ảnh hưởng mạnh tới architecture và cần được đưa vào architecture/design decisions. fileciteturn9file3L1-L18

## QR-01 — Maintainability

EngineeringOS phải dễ:
- hiểu;
- sửa;
- mở rộng;
- thêm knowledge type;
- thêm agent;
- thay đổi implementation mà không phá foundation.

Đây là quality quan trọng vì project có mục tiêu phát triển trong nhiều năm.

---

## QR-02 — Extensibility

Có thể thêm:

```text
new document type
new knowledge domain
new agent
new learning program
new project
new AI runtime
```

mà không phải redesign toàn bộ system.

---

## QR-03 — Reliability

Knowledge và configuration phải được bảo vệ khỏi mất mát hoặc corruption.

Đặc biệt:
- ADR;
- lessons learned;
- architecture notes;
- project knowledge;
- configuration.

Git/version control là một phần quan trọng của reliability và traceability.

---

## QR-04 — Privacy / Security

Knowledge có thể chứa thông tin engineering nội bộ.

Do đó architecture phải ưu tiên:

```text
Local-first
Controlled access
Explicit data boundaries
No unnecessary cloud dependency
```

Đặc biệt Local AI là một architectural constraint/strategy quan trọng của project.

---

## QR-05 — Usability / Findability

Người dùng phải có thể nhanh chóng tìm được knowledge cần thiết.

Một knowledge platform rất lớn nhưng không tìm được thông tin thì về thực tế không tạo ra giá trị.

Vì vậy cần quan tâm:

```text
Organization
Metadata
Search
Semantic retrieval
Clear naming
Traceability
```

iSAQB cũng nhấn mạnh documentation cần hỗ trợ giao tiếp lâu dài về decisions, structures và concepts; đồng thời tránh redundancy và hỗ trợ version/configuration management. fileciteturn9file19L1-L18

---

# 5. Three Major Constraints

## C-01 — Local AI First

EngineeringOS được thiết kế để sử dụng **Local AI**.

Không được giả định rằng mọi capability đều phụ thuộc vào cloud AI.

Điều này ảnh hưởng trực tiếp đến:
- runtime;
- data access;
- privacy;
- model selection;
- infrastructure;
- agent design.

---

## C-02 — Heterogeneous Knowledge Sources

Knowledge không chỉ là Markdown.

System phải có khả năng tiếp nhận nhiều loại:

```text
PDF
DOCX
HTML
TXT
MD
JSON
Excel
PlantUML
Web links
...
```

Do đó knowledge architecture không nên coupling với một parser hoặc một format duy nhất.

---

## C-03 — Long-term Evolution

EngineeringOS không phải project ngắn hạn.

Nó phải có khả năng phát triển cùng với career của người dùng:

```text
Engineer
   ↓
Senior Engineer
   ↓
Feature Owner
   ↓
Solution Architect
   ↓
Senior Architect
```

Vì vậy architecture phải ưu tiên:
- simplicity;
- maintainability;
- extensibility;
- clear boundaries;
- controlled evolution.

Không nên xây một hệ thống agent quá phức tạp ngay từ đầu.

---

# Architecture Statement

Sau khi phân tích 5 nhóm trên, tôi chọn:

> **Architecture của EngineeringOS cần ưu tiên maintainability, extensibility và local-first privacy vì đây là một hệ thống knowledge/AI dài hạn, phải tích lũy và phát triển qua nhiều năm mà không biến thành một hệ thống quá phức tạp.**

---

# Architect Reflection

Điểm quan trọng nhất của exercise này:

EngineeringOS có rất nhiều functional requirements, nhưng **không phải functional requirement nào cũng quyết định architecture**.

Theo tài liệu Software Architecture with C++, functional requirement trở thành architecturally significant khi những đặc tính của nó có thể ảnh hưởng đến kiến trúc; quality attributes và constraints cũng là những yếu tố quan trọng cần xem xét. fileciteturn9file12L1-L18

Vì vậy bước tiếp theo của Architect không phải là:

> "Bắt đầu code Agent."

Mà là:

> "Requirement nào thực sự là Architecturally Significant Requirement?"

Đó sẽ là bước chuyển từ **requirements → architecture decisions**.

---

# Day 1 Key Takeaway

```text
Purpose
   ↓
Stakeholders
   ↓
Functional Requirements
   ↓
Quality Requirements
   ↓
Constraints
   ↓
Architecturally Significant Requirements
   ↓
Architecture Decisions
```

**Architecture không bắt đầu từ framework.**

Architecture bắt đầu từ **problem, context, requirements, quality và constraints**.
