# Architect Daily Learning — Progress

## Locked Rules
- 15 minutes/day.
- Each lesson spans 2 days: Day 1 Lesson, Day 2 Review.
- Do not change roadmap/order/template unless explicitly requested.
- Lesson template: English → Vietnamese → Architect Mindset → Real-world Case Study → iSAQB Mapping → Mini Exercise → Reflection → Summary → Flashcards → Keywords.
- Lessons, Reviews, Appendices and Architecture Notes are separate document types.
- Role: Software Architect Mentor; challenge assumptions and correct thinking.
- Focus: essence, mindset, trade-offs, architecture decisions; not memorization.

## Progress
- Lesson 001 — Software Architecture — Completed
- Lesson 002 — Stakeholders & Quality Requirements — Completed
- Lesson 003 — ASRs — Completed
- Lesson 004 — Architecture Constraints — Completed
- Lesson 005 — Architecture Decisions — Completed
- Lesson 006 — Decomposition & Separation of Concerns — Completed
- Lesson 007 — Information Hiding — Completed
- Lesson 008 — Loose Coupling & High Cohesion — Completed
- Lesson 009 — Dependency Inversion — In progress

## Key User Insights
1. “Cần phải biết mỗi component có responsibility rõ ràng thì mới chia tách được.”
2. “Đề bài chưa cụ thể thì phải?” — Architect must recognize insufficient information before deciding.
3. Campaign vs Download:
   - Campaign: which vehicle/software should be updated.
   - Download Manager: how/when download is performed.
4. Information Hiding:
   - expose meaningful domain inputs;
   - hide implementation mechanisms.
5. Coupling:
   - communication volume is not the same as semantic coupling;
   - dependency is not automatically bad;
   - failure propagation must be considered separately.
6. Architecture design:
   - do not add retry/Kafka/etc. merely because they are common solutions if the requirement does not justify them.
7. Dependency Inversion:
   - abstraction should be designed from high-level business needs;
   - provider knowledge belongs on payment/provider side, not OrderService.
