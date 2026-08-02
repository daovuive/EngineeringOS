# Software Architecture Learning Plan

This plan uses the files already in this folder:

- `iSAQB_Software Architecture Fundamentals 1st Edition.Pdf`
- `Software Architecture with C++ - Adrian Ostrowski; Piotr Gaczkowski.epub`
- Scrum materials as supporting context for working in agile teams

## Goal

Learn enough software architecture to:

- Explain what architecture is and why it matters.
- Identify architecturally significant requirements.
- Design a small or medium system using clear building blocks.
- Document architecture using views and diagrams.
- Reason about quality attributes such as maintainability, performance, availability, security, and modifiability.
- Communicate trade-offs and architecture decisions.

## 6-Week Path

### Week 1 - Architecture Foundations

Read:

- iSAQB Chapter 1: Introduction
- iSAQB Chapter 2: Software Architecture Fundamentals
- C++ book: "Importance of Software Architecture and Principles of Great Design"

Focus:

- Software-intensive systems
- Building blocks, interfaces, relationships, and constraints
- Difference between architecture, design, code structure, and project goals
- Stakeholders and architecture context

Exercise:

Choose a familiar system, such as an online shop, learning app, banking app, or booking system.
Write one page with:

- System purpose
- Main users
- Important external systems
- 5 functional requirements
- 5 quality requirements
- 3 constraints

### Week 2 - Design Principles

Read:

- iSAQB Chapter 3 sections 3.2 to 3.5
- C++ book sections on SOLID, DRY, coupling, and cohesion

Focus:

- Top-down and bottom-up design
- Decomposition
- Separation of concerns
- Information hiding
- Loose coupling and high cohesion
- Dependency inversion
- Avoiding cyclic dependencies

Exercise:

For your chosen system, split it into 5-8 major building blocks.
For each block, write:

- Responsibility
- Public interface
- Dependencies
- What should be hidden inside the block

### Week 3 - Architecture Styles and Patterns

Read:

- iSAQB Chapter 3 sections 3.6 and 3.7
- C++ book: "Architectural Styles"

Focus:

- Layered architecture
- Pipes and filters
- MVC/MVP/PAC
- Broker
- Service orientation
- Microservices
- Adapter, Observer, Decorator, Proxy, Facade, Bridge, State, Mediator

Exercise:

Pick 2 possible architecture styles for your system.
Compare them using this table:

| Option | Benefits | Risks | Best fit when | Worst fit when |
| --- | --- | --- | --- | --- |
| Layered architecture | | | | |
| Microservices or modular monolith | | | | |

Then choose one and explain why.

### Week 4 - Architecture Documentation

Read:

- iSAQB Chapter 4: Description and Communication of Software Architectures
- C++ book: "Documenting architecture", especially 4+1 and C4

Focus:

- Context view
- Building block view
- Runtime view
- Deployment/infrastructure view
- Cross-cutting concepts
- Architecture decision records
- Diagrams that communicate instead of decorate

Exercise:

Create these artifacts for your chosen system:

- Context diagram
- Building block diagram
- One runtime sequence for a key use case
- Deployment sketch
- 3 architecture decision records

Use simple tools first: Markdown, Mermaid, PlantUML, draw.io, or whiteboard photos are enough.

### Week 5 - Quality and Evaluation

Read:

- iSAQB Chapter 5: Software Architectures and Quality
- C++ book sections on availability, fault tolerance, scaling, caching, CQRS/event sourcing, and deployment

Focus:

- Quality attributes
- Architecture tactics
- Trade-offs
- Prototypes and proof of concept
- ATAM-style evaluation
- Metrics and architecture compliance

Exercise:

Make a quality attribute scenario table:

| Quality | Scenario | Stimulus | Response | Measure |
| --- | --- | --- | --- | --- |
| Performance | Search products | 500 concurrent users search | Return results | p95 under 300 ms |
| Availability | Service fails | Payment provider unavailable | Checkout degrades safely | No order lost |

Then evaluate your design against the scenarios.

### Week 6 - Tools and Practice

Read:

- iSAQB Chapter 6: Tools for Software Architects
- Relevant Scrum material only if you need team/process context

Focus:

- Requirements tools
- Modeling tools
- Static and dynamic analysis
- Build/version management
- Testing tools
- Documentation tools

Exercise:

Package your architecture work into a mini architecture document:

- Executive summary
- Goals and constraints
- Context view
- Building block view
- Runtime view
- Deployment view
- Quality scenarios
- Architecture decisions
- Risks and open questions

## Daily Study Routine

Use this 45-60 minute loop:

1. Read 10-15 pages.
2. Write 5 bullet notes in your own words.
3. Add 1 example from a real system.
4. Draw or update 1 diagram.
5. Write 1 question you still cannot answer.

## What To Ask Codex

Useful prompts:

- "Explain this architecture topic with a concrete example."
- "Quiz me on iSAQB Chapter 2."
- "Review my context diagram."
- "Help me identify architecturally significant requirements."
- "Compare layered architecture, modular monolith, and microservices for my system."
- "Create an ADR for this decision."
- "Evaluate this design for performance and maintainability."

## First Practice System

Recommended beginner project: online learning platform.

Main features:

- User registration and login
- Course catalog
- Lesson playback
- Progress tracking
- Quiz submission
- Payment or subscription
- Admin course management

Good architecture questions:

- Which parts need strong consistency?
- Which parts can be asynchronous?
- What happens if payment fails?
- How should progress tracking scale?
- What data should each module own?
- What quality attribute matters most: speed, reliability, security, maintainability, or cost?
