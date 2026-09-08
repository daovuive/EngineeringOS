# Skill: analyze-job-description

## Purpose

Analyze a job description and compare its capability requirements with a
candidate career plan. This skill is reusable across companies and roles.

## Inputs

- One job description document.
- One career plan or capability profile.

## Outputs

- Structured job requirement summary.
- Capability gap analysis.
- Prioritized learning and application actions.
- Assumptions and missing information.

## Workflow

1. Read the job description and identify responsibilities, mandatory
   requirements, preferred requirements, domain knowledge and success criteria.
2. Normalize requirements into capability categories: product, architecture,
   engineering, domain, leadership and communication.
3. Read the career plan and map evidence to each capability.
4. Classify each capability as `evidenced`, `partial`, `missing` or `unknown`.
5. Prioritize gaps by job importance, current gap and achievable next action.
6. Produce the output with references to the source documents.

## Dependencies

- Knowledge paths: the supplied job description and career plan.
- Prompts: use a dedicated analysis prompt if one is registered.
- Tools: document reader and optional semantic search through the existing
  EngineeringOS retrieval path (`eng.py knowledge search` or
  `engineering_os.knowledge.search_index`).
- Runtime capabilities: chat or reasoning model through the configured
  EngineeringOS runtime (`eng.py llm chat` or `engineering_os.llm.create_runtime`).
- Grounded answers: use the existing RAG path when generation needs source
  citations (`eng.py knowledge ask` or `engineering_os.rag.answer_question`).

Skills do not create provider clients, call provider endpoints directly, load
model files, or define their own retrieval, embedding, or model configuration.

## Quality Checks

- Separate explicit job requirements from inferred requirements.
- Do not claim experience that is not supported by the career plan.
- Preserve the distinction between mandatory and preferred requirements.
- State unresolved questions instead of silently filling gaps.
- Keep source documents as the single source of truth; do not copy their content
  into the skill package.
