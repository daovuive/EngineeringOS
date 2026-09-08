# Skill: career-direction-review

## Purpose

Answer questions about the current career direction, compare Solution Architect
and Feature Owner paths, and recommend next actions using the canonical career
documents.

## Canonical Sources

- `career/career-direction-sa-vs-fo.md`
- `career/Career_Plan_v1.0.md`
- Relevant files under `career/job-market/`

## Workflow

1. Identify whether the question concerns direction, path trade-offs,
   capability gaps, learning priorities or market fit.
2. Read the career direction document first for the current decision and
   rationale.
3. Cross-check the Career Plan for goals, priorities, milestones and risks.
4. Include a relevant job-market document when the question concerns a target
   role or external demand.
5. Separate documented conclusions from new inferences.
6. Answer with: current direction, reasoning, evidence, trade-offs and the next
   practical actions.

## Local AI Integration

- Retrieve canonical career sources through the existing EngineeringOS search
  path (`eng.py knowledge search` or `engineering_os.knowledge.search_index`).
- Use the configured chat or reasoning role through the shared runtime
  (`eng.py llm chat` or `engineering_os.llm.create_runtime`).
- Use the existing RAG path when an answer requires grounded source handling
  (`eng.py knowledge ask` or `engineering_os.rag.answer_question`).
- Do not create provider clients, call provider endpoints directly, load model
  files, or duplicate retrieval, embedding, or model configuration.

## Output Rules

- Treat Solution Architect as the primary direction unless the user explicitly
  asks to reassess the strategy.
- Treat Feature Owner as a supporting or near-term path, not automatically as
  the final destination.
- Do not optimize for a job title alone; evaluate capability growth, scope,
  impact and market value.
- Cite the source file paths used in the answer.
- State uncertainty when the available career evidence is insufficient.

## Quality Checks

- Do not invent experience, qualifications or market facts.
- Preserve the distinction between current direction and future possibility.
- Do not duplicate or modify source career documents as part of an answer.
