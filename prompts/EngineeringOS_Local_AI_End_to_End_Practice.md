# EngineeringOS Local AI End-to-End Practice

- **Purpose:** Step-by-step Codex practice for building, reviewing, validating, and operating the EngineeringOS Local AI stack.
- **Recommended project location:** `prompts/EngineeringOS_Local_AI_End_to_End_Practice.md`
- **Folder policy:** Use the existing `prompts/` directory. Do not create any new folder.
- **Execution model:** Run one phase at a time. Do not treat this entire document as one execution prompt unless the project owner explicitly requests a full end-to-end audit.

---

# Execution Gate

This document is a guided Local AI practice roadmap, not a single execution prompt.

## Mandatory Reading Rule

When an AI tool opens this file, it MUST NOT read or execute all phases by default.

On first entry:

1. Read only this `Execution Gate` section.
2. Do not continue into Phase 1 or any later phase yet.
3. Determine the current phase from `Current Progress`.
4. Ask the project owner which phase to work on unless the user explicitly requested resume/continue behavior.
5. If the user explicitly requested resume/continue behavior:
   - resume the current `IN PROGRESS` phase;
   - if none exists, select the first `NOT STARTED` phase after the completed phases.
6. After a phase is selected, read only:
   - that phase,
   - `AGENTS.md` as required,
   - and the minimum project context required by that phase.
7. Stop reading when the selected phase ends unless additional context is explicitly required to complete it.
8. Do not preload later phases.
9. Do not execute more than one phase unless the project owner explicitly asks for multiple phases.

## Current Progress

The project owner or the AI executing an authorized phase may update this section according to the Phase Completion and Status Update Protocol.

```text
Phase 1  — Local AI Architecture Review             COMPLETED
Phase 2  — Governance Validation                    COMPLETED
Phase 3  — Provider and Model Configuration         COMPLETED
Phase 4  — EngineeringOS -> Ollama Smoke Test       COMPLETED
Phase 5  — Embedding Model                          COMPLETED
Phase 6  — Knowledge Indexing                       COMPLETED
Phase 7  — Retrieval Validation                     COMPLETED
Phase 8  — RAG Integration                          COMPLETED
Phase 9  — RAG Evaluation                           COMPLETED
Phase 10 — Memory Integration                       COMPLETED
Phase 11 — Skills Integration                       COMPLETED
Phase 12 — Agent Integration                        COMPLETED
Phase 13 — Observability and Performance            COMPLETED
Phase 14 — Portability and Final Validation         COMPLETED
```

Status values:

```text
NOT STARTED
IN PROGRESS
BLOCKED
COMPLETED
```

This status list is navigation metadata only. It does not override project architecture, governance, validation results, ADRs, tests, or implementation evidence.

## Phase Completion and Status Update Protocol

The AI executing a phase is responsible for validating and updating that phase's status in this document.

At the end of every selected phase:

1. Compare the actual result against that phase's `Exit Criteria`.
2. Run the validation required by the phase and by `AGENTS.md`.
3. Determine the phase status from evidence, not from task completion alone.

Use these rules:

```text
COMPLETED
    -> every required exit criterion is satisfied
    -> required validation passes
    -> no unresolved blocker remains for this phase

IN PROGRESS
    -> useful work was completed
    -> but one or more exit criteria or validations remain unfinished

BLOCKED
    -> the phase cannot continue because of an external dependency,
       missing authorization, unavailable provider/resource, or another
       blocker that cannot be resolved within the authorized scope

NOT STARTED
    -> no implementation or validation work for the phase has begun
```

4. Update the corresponding entry under `Current Progress` in this file.
5. Do not mark a phase `COMPLETED` merely because code was changed.
6. Do not mark a phase `COMPLETED` when required validation is failing.
7. If the phase is `IN PROGRESS` or `BLOCKED`, record the remaining condition clearly in the final report.
8. If the phase becomes `COMPLETED`, identify the next `NOT STARTED` phase but do not start it automatically.
9. Do not change the status of unrelated phases.
10. Do not infer completion of earlier phases unless their status is explicitly being revalidated as part of the authorized task.

After updating the status, finish with:

```text
Phase <number> — <name>
Status: <COMPLETED | IN PROGRESS | BLOCKED>

Exit criteria:
- PASS/FAIL ...
- PASS/FAIL ...

Validation:
- ...

Roadmap status updated: Yes

Next phase:
Phase <number> — <name>

Stopped before starting the next phase.
```

The status stored in this roadmap is navigation state, not a substitute for implementation evidence, tests, ADRs, or project governance.

## Required First Response

If the project owner has not explicitly requested resume/continue behavior, respond with only a short status summary and ask which phase to work on.

Use this format:

```text
Local AI practice roadmap loaded.

Current phase: Phase <number> — <name>
Status: <status>

Next available phase: Phase <number> — <name>

Which phase should I work on?
```

Do not inspect the implementation, execute commands, modify files, or read later phase prompts until the project owner selects a phase.

If the project owner explicitly requested resume/continue behavior, select the correct phase using the rules above and proceed without asking again.

## Phase Selection

If the project owner replies with a phase number, for example:

```text
Phase 5
```

then:

1. Read only the selected phase section of this file.
2. Follow its objective, prompt, and exit criteria.
3. Load additional project context according to `AGENTS.md`.
4. Complete only the selected phase.
5. Apply the Phase Completion and Status Update Protocol.
6. Report the result.
7. Stop before proceeding to the next phase.

If the selected phase is already `COMPLETED`, ask whether the owner wants to:

- revalidate it, or
- continue to the next incomplete phase.

Do not assume that `COMPLETED` means the implementation cannot have changed.

## Context-Efficiency Rule

The existence of this roadmap does not authorize full-file or full-repository loading.

Use:

```text
Execution Gate
    -> selected phase
    -> minimum required project context
    -> execute
    -> validate
    -> update phase status
    -> stop
```

Never use:

```text
Execution Gate
    -> read all 14 phases
    -> scan repository
    -> decide what to do
```

The second behavior is explicitly prohibited unless the project owner requests a full end-to-end audit.

---

# Phase 1 — Review Local AI Architecture

## Objective

Verify that the repository architecture has the correct ownership boundaries before building more AI functionality.

## Codex Prompt

```text
Review the current EngineeringOS repository against the intended Local AI architecture.

Follow AGENTS.md and use the smallest context necessary.

Target architecture:

- EngineeringOS source and Linux runtime live in WSL ext4.
- Ollama runs as an external provider.
- Reusable model binaries live outside the EngineeringOS repository.
- EngineeringOS does not depend on physical provider model-storage paths.
- AI configuration is separated from application code.
- EngineeringOS runtime contains only project-owned generated state.
- Provider, model, disk, and host changes should not redesign the knowledge repository.

Tasks:

1. Inspect the relevant current architecture and configuration.
2. Identify what is already correct.
3. Identify mismatches or unnecessary coupling.
4. Check for assumptions that reusable models belong under `runtime/`.
5. Check for provider-specific details leaking into stable architecture.
6. Propose only the smallest necessary changes.
7. Do not modify the root README without explicit approval.
8. Do not perform unrelated cleanup.

Report:

## Summary
- Status: Correct / Mostly correct / Needs changes
- Main conclusion

## What Is Correct
- ...

## Mismatches
| Area | Current | Target | Severity |
| --- | --- | --- | --- |

## Minimal Changes
1. ...
2. ...

## Validation
- Checks performed
- Remaining risks
```

## Exit Criteria

- Architecture ownership is clear.
- Model binaries are outside repository ownership.
- Stable architecture is not tied to a physical disk or provider.

---

# Phase 2 — Validate Governance and Protected Architecture

## Objective

Ensure Local AI work respects EngineeringOS governance.

## Codex Prompt

```text
Validate governance for the current EngineeringOS Local AI architecture work.

Follow AGENTS.md.

Tasks:

1. Run the validation required for the current scope.
2. Verify that the root README protection is functioning.
3. Verify manifests, README hierarchy, registries, and protected baselines relevant to the current changes.
4. Do not weaken or bypass governance checks.
5. Do not modify policy merely to make validation pass.
6. Report any remaining violations and their exact cause.

If the root README has an approved change but its protected SHA-256 baseline has not yet been updated, stop and report that explicit owner authorization is required before rebasing the baseline.

Report:

| Check | Result | Evidence |
| --- | --- | --- |
| Project validation | PASS/FAIL | ... |
| Root protection | PASS/FAIL | ... |
| Structure/manifest consistency | PASS/FAIL | ... |
| Registry consistency | PASS/FAIL | ... |

List the smallest required fix for each failure.
```

## Exit Criteria

- Applicable governance validation passes.
- No validation rule has been disabled or weakened.

---

# Phase 3 — Validate Provider and Model Configuration

## Objective

Ensure model and provider selection is configuration-driven.

## Codex Prompt

```text
Review the current EngineeringOS AI configuration boundary.

Follow AGENTS.md and keep context within the relevant configuration subsystem.

Tasks:

1. Identify the configured logical primary LLM.
2. Identify its provider.
3. Identify its provider model ID.
4. Identify how the provider endpoint is configured.
5. Verify logical model identity is separate from physical model storage.
6. Verify model/provider selection is not hard-coded in application logic.
7. Verify machine-specific values are not embedded in stable architecture documentation.
8. Check for duplicate AI configuration mechanisms.
9. Do not modify unrelated files.

Report:

## Resolved Configuration
- Logical model:
- Provider:
- Provider model ID:
- Endpoint source:
- Physical model path known by EngineeringOS: Yes/No

## Findings
| Check | Result | Evidence |
| --- | --- | --- |

## Minimal Fixes
Only list changes that are required.
```

## Exit Criteria

- Provider selection is configuration-driven.
- Model selection is configuration-driven.
- Physical provider storage is opaque to EngineeringOS.

---

# Phase 4 — Smoke Test EngineeringOS to Local Provider

## Objective

Verify a complete inference path through EngineeringOS.

## Codex Prompt

```text
Perform a minimal EngineeringOS -> local model provider smoke test.

Follow AGENTS.md and keep context narrow.

Tasks:

1. Resolve the configured logical primary LLM.
2. Resolve its provider and endpoint.
3. Verify the endpoint is reachable from the EngineeringOS runtime environment.
4. Verify the configured provider model exists.
5. Send one minimal inference request through the existing EngineeringOS provider/runtime abstraction.
6. Do not hard-code a different provider endpoint or model for the application-level test.
7. Verify EngineeringOS does not know the physical model storage path.
8. If something fails, identify the exact failing boundary before making changes.

Use this smoke-test prompt:

Reply with exactly: EngineeringOS Local AI smoke test passed

Report:

| Check | Result | Evidence |
| --- | --- | --- |
| Logical model resolved | PASS/FAIL | ... |
| Provider resolved | PASS/FAIL | ... |
| Endpoint reachable | PASS/FAIL | ... |
| Model available | PASS/FAIL | ... |
| No physical model-path dependency | PASS/FAIL | ... |
| Inference through EngineeringOS | PASS/FAIL | ... |

If a check fails, report the boundary:

config
    -> provider resolution
    -> networking
    -> provider API
    -> model resolution
    -> inference
```

## Exit Criteria

A response successfully travels through:

```text
EngineeringOS
    -> configuration
    -> provider abstraction
    -> local model provider
    -> model
    -> response
```

---

# Phase 5 — Establish the Embedding Model

## Objective

Add and validate an embedding model without coupling knowledge storage to one implementation.

## Codex Prompt

```text
Design, implement, and validate the embedding-model contract for EngineeringOS.

Follow AGENTS.md. Treat this as an AI subsystem task and keep context narrow.

Current expected direction:

- Logical role: embedding
- Provider: configured AI provider
- Model identity: configuration-driven
- Vector dimensions: explicit compatibility metadata
- Model binaries remain provider-owned
- Indexes must not silently reuse embeddings produced by an incompatible embedding contract

Tasks:

1. Inspect the current AI configuration and retrieval/index architecture.
2. Resolve the configured embedding role, provider, model ID, and dimensions.
3. If dimensions are known from runtime but not represented in configuration, add the smallest appropriate configuration metadata.
4. Define an embedding compatibility contract containing at least:
   - embedding contract/schema version,
   - provider ID,
   - model ID,
   - vector dimensions.
5. Persist that embedding contract with newly built knowledge indexes.
6. Validate the stored contract when an index is loaded or searched.
7. Reject incompatible indexes clearly when provider, model ID, dimensions, or embedding contract version changes.
8. Connect the existing CLI/runtime path to this compatibility validation.
9. Keep model binaries and physical provider storage paths outside EngineeringOS.
10. Do not modify unrelated files or the root README.

Validation:

1. Current embedding generation succeeds.
2. Returned vector dimensions match configured dimensions.
3. A newly built index stores the embedding compatibility contract.
4. The current compatible index loads successfully.
5. Changing the configured model ID causes the old index to be rejected clearly.
6. Changing configured dimensions causes the old index to be rejected clearly.
7. No physical model-storage path is required by EngineeringOS.

Report:

## Embedding Contract
- Logical role:
- Provider:
- Model ID:
- Dimensions:
- Contract version:

## Files Changed
| File | Change | Reason |
| --- | --- | --- |

## Validation
| Check | Result | Evidence |
| --- | --- | --- |

If every Phase 5 exit criterion passes, update Phase 5 to COMPLETED.
Otherwise keep it IN PROGRESS or BLOCKED according to the Execution Gate protocol.

Stop after Phase 5.
Do not start Phase 6.
```

## Exit Criteria

- Embedding model has a clear logical role.
- Provider/model selection is configuration-driven.
- Vector dimensions are explicit compatibility metadata.
- Indexes store the embedding compatibility contract.
- Incompatible indexes are rejected instead of silently reused.
- Model binaries remain provider-owned.

---

# Phase 6 — Build Knowledge Indexing

## Objective

Create a reproducible index from authoritative EngineeringOS knowledge.

## Codex Prompt

```text
Review or implement the smallest viable knowledge-indexing pipeline for EngineeringOS.

Follow AGENTS.md and the nearest knowledge/runtime guidance.

Tasks:

1. Identify the authoritative sources eligible for indexing.
2. Preserve source paths and traceability metadata.
3. Define chunking behavior explicitly.
4. Use the configured embedding abstraction.
5. Store generated indexes under the approved EngineeringOS runtime boundary.
6. Do not make the index an authoritative knowledge source.
7. Ensure the index can be rebuilt from repository knowledge.
8. Avoid indexing unrelated runtime, logs, generated files, or model binaries.
9. Add only the smallest required implementation and tests.

Report:

## Indexed Sources
- ...

## Excluded Sources
- ...

## Index Contract
- chunking:
- metadata:
- embedding identity:
- storage:
- rebuild behavior:

## Validation
- ...
```

## Exit Criteria

- Index is rebuildable.
- Every indexed chunk remains traceable to an authoritative source.
- Runtime index is clearly non-authoritative.

---

# Phase 7 — Validate Retrieval Quality

## Objective

Prove retrieval works before connecting it to generation.

## Codex Prompt

```text
Evaluate EngineeringOS knowledge retrieval without using LLM generation to hide retrieval errors.

Follow AGENTS.md.

Tasks:

1. Select a small representative set of questions whose answers exist in EngineeringOS knowledge.
2. Run retrieval only.
3. Inspect the top retrieved chunks for relevance and source correctness.
4. Measure or record retrieval rank where practical.
5. Identify failures caused by chunking, metadata, embedding choice, or query formulation.
6. Do not tune the LLM in this phase.
7. Make only evidence-based retrieval changes.

Report:

## Retrieval Cases
| Question | Expected Source | Top Result | Relevant? | Notes |
| --- | --- | --- | --- | --- |

## Findings
- ...

## Recommended Minimal Changes
- ...

## Re-test Result
- ...
```

## Exit Criteria

- Retrieval reliably surfaces relevant authoritative sources.
- Failures are understood before RAG is added.

---

# Phase 8 — Integrate RAG

## Objective

Combine retrieval and generation while preserving source traceability.

## Codex Prompt

```text
Integrate or review the EngineeringOS RAG pipeline.

Follow AGENTS.md and keep the implementation minimal.

Tasks:

1. Use the existing retrieval layer rather than duplicating retrieval logic.
2. Feed retrieved context to the configured logical LLM through the provider abstraction.
3. Preserve source references in the generated answer.
4. Keep retrieved knowledge distinct from model-generated statements.
5. Define behavior when retrieval returns insufficient evidence.
6. Avoid silently answering unsupported EngineeringOS-specific claims from model memory.
7. Add focused tests for grounded and insufficient-evidence cases.
8. Do not add agent orchestration in this phase.

Report:

## RAG Flow
config
    -> query
    -> retrieval
    -> context
    -> LLM
    -> grounded answer + sources

## Grounding Checks
| Check | Result | Evidence |
| --- | --- | --- |

## Remaining Risks
- ...
```

## Exit Criteria

- RAG uses authoritative retrieved context.
- Source traceability is preserved.
- Insufficient evidence has explicit behavior.

---

# Phase 9 — Evaluate RAG Quality

## Objective

Measure whether RAG answers are useful, grounded, and stable.

## Codex Prompt

```text
Create a small repeatable evaluation for the EngineeringOS RAG pipeline.

Follow AGENTS.md.

Tasks:

1. Define a representative evaluation set from existing EngineeringOS knowledge.
2. Include:
   - direct factual retrieval,
   - synthesis across multiple notes,
   - no-answer / insufficient-evidence cases,
   - architecture reasoning where source evidence exists.
3. Evaluate retrieval relevance separately from answer quality.
4. Evaluate whether citations/source references support the answer.
5. Record failures rather than hiding them with prompt changes.
6. Keep the evaluation lightweight and repeatable.
7. Do not introduce a new evaluation framework unless the existing project cannot support the requirement.

Report:

## Evaluation Set
| Case | Expected Behavior | Result |
| --- | --- | --- |

## Metrics or Review Criteria
- retrieval relevance
- grounding
- source correctness
- unsupported claims
- answer usefulness

## Baseline Result
- ...

## Highest-Priority Failure
- ...
```

## Exit Criteria

- A repeatable quality baseline exists.
- Retrieval and generation failures can be distinguished.

---

# Phase 10 — Integrate Project Memory

## Objective

Use long-term project memory without turning generated assumptions into facts.

## Codex Prompt

```text
Review how EngineeringOS memory should participate in Local AI retrieval and reasoning.

Follow AGENTS.md and the memory README.

Tasks:

1. Identify the authoritative role of `memory/`.
2. Determine when memory should be included in retrieval.
3. Preserve source and update-date metadata.
4. Keep memory separate from verified career experience and authoritative technical knowledge where their semantics differ.
5. Define how stale memory is detected or surfaced.
6. Prevent generated assumptions from becoming recorded facts.
7. Reuse existing retrieval/index mechanisms where appropriate.
8. Do not create a second memory mechanism.

Report:

## Memory Contract
- source:
- freshness:
- authority:
- retrieval role:

## Risks
- ...

## Minimal Integration Changes
- ...
```

## Memory Contract

- source: human-maintained Markdown notes under `memory/`, with the source path
  and `Last updated: YYYY-MM-DD` metadata preserved in the shared index.
- freshness: retrieval accepts memory only when the update date is within the
  configured 90-day window; missing or invalid dates are treated as stale and
  excluded.
- authority: memory is contextual and non-authoritative. Technical knowledge,
  architecture decisions, and verified career experience remain owned by their
  primary sources.
- retrieval role: memory is opt-in context for project intent, current state,
  preferences, and continuity. It uses the existing Markdown index and RAG
  path; no second memory mechanism was added.

## Risks

- Memory can become stale or contain a human-entered assumption; stale or
  undated notes are excluded, and memory chunks cannot ground authoritative
  RAG claims.
- Memory is not automatically used for every question; callers must explicitly
  request contextual memory retrieval.

## Minimal Integration Changes

- Added source type, authority, and update-date metadata to indexed chunks.
- Indexed `memory/` into the existing knowledge index and added opt-in
  `--include-memory` retrieval for search and RAG.
- Added configurable freshness validation through
  `memory.retrieval.maxAgeDays`.
- Added RAG prompt and grounding safeguards so model-generated assumptions or
  memory-only content cannot silently become authoritative facts.
- Documented the contract in `memory/README.md` and added focused tests.

## Validation

- PASS — `python3 -m unittest discover -s tests` (28 tests).
- PASS — `python3 -m py_compile engineering_os/knowledge.py
  engineering_os/rag.py engineering_os/cli.py`.
- PASS — `python3 eng.py validate`.
- PASS — memory indexing smoke check preserved source type, contextual
  authority, and `2026-08-08` update metadata for 11 project-context chunks.

Status: COMPLETED

## Exit Criteria

- Memory semantics are explicit.
- AI-generated assumptions cannot silently become authoritative memory.

---

# Phase 11 — Integrate Skills

## Objective

Let reusable workflows use Local AI without duplicating knowledge or provider logic.

## Codex Prompt

```text
Review Local AI integration with EngineeringOS skills.

Follow AGENTS.md, `skills/README.md`, and the skill registry only as needed.

Tasks:

1. Identify skills that need Local AI capabilities.
2. Verify skills reference canonical knowledge rather than copying it.
3. Verify skills call existing retrieval/provider abstractions rather than implementing their own model clients.
4. Keep one canonical workflow per skill.
5. Identify opportunities where an existing prompt practice should become a skill only if it is stable, reusable, and multi-step.
6. Do not convert every prompt into a skill.
7. Do not duplicate provider configuration inside skills.

Report:

## Skill Integration Review
| Skill | AI Capability Needed | Existing Abstraction Reused? | Action |
| --- | --- | --- | --- |

## Recommended Promotions from Prompt to Skill
Only include mature candidates.
```

## Skill Integration Review

| Skill | AI Capability Needed | Existing Abstraction Reused? | Action |
| --- | --- | --- | --- |
| `analyze-job-description` | Optional semantic retrieval, reasoning/chat generation, and grounded source handling | Yes — `engineering_os.knowledge`, `engineering_os.rag`, and `engineering_os.llm` via the canonical CLI/runtime | Keep the workflow; make its shared Local AI boundary explicit. |
| `career-direction-review` | Canonical-source retrieval and reasoning generation with source references | Yes — `engineering_os.knowledge`, `engineering_os.rag`, and `engineering_os.llm` via the canonical CLI/runtime | Keep the workflow; make its shared Local AI boundary explicit. |

Both active skills reference source documents in `career/` and do not copy
career or knowledge content into their packages. No skill contains a provider
client, provider endpoint, model ID, embedding implementation, or independent
retrieval policy.

## Recommended Promotions from Prompt to Skill

None. `Resume_Local_AI_Practice.md` is a small entrypoint that delegates to the
master roadmap, while `EngineeringOS_Local_AI_End_to_End_Practice.md` is a
phase-gated practice roadmap. Neither is a stable, reusable, multi-step
workflow independent of the roadmap's execution gate.

## Validation

- PASS — both registered active skills now name the shared retrieval, RAG, and
  runtime abstractions.
- PASS — repository search found no provider client, provider endpoint, model
  ID, embedding implementation, or duplicate retrieval policy under `skills/`.
- PASS — both skill packages retain canonical-source and human-approval
  boundaries.

Status: COMPLETED

## Exit Criteria

- Skills reuse common AI infrastructure.
- No duplicate provider/retrieval implementations appear.

---

# Phase 12 — Integrate Agents

## Objective

Add role coordination only after skills and AI primitives are stable.

## Codex Prompt

```text
Review EngineeringOS agent integration with the Local AI stack.

Follow AGENTS.md and the agents README.

Tasks:

1. Identify what responsibilities truly require agent coordination.
2. Keep provider, retrieval, memory, and skill logic outside agent definitions.
3. Agents should coordinate roles and invoke canonical skills rather than duplicate workflows.
4. Define explicit boundaries for important architectural decisions that require human approval.
5. Avoid adding autonomous behavior where a deterministic workflow is sufficient.
6. Keep agent context loading scoped to the current task.
7. Do not create new agents merely to mirror directory structure.

Report:

## Agent Responsibilities
| Agent/Role | Responsibility | Skills Used | Human Approval Boundary |
| --- | --- | --- | --- |

## Unnecessary Agent Complexity
- ...

## Minimal Integration Plan
- ...
```

## Agent Responsibilities

| Agent/Role | Responsibility | Skills Used | Human Approval Boundary |
| --- | --- | --- | --- |
| Task coordinator (planned, not executable) | Classify a request, select registered skills, pass scoped context, verify outputs, and preserve source references | Only the registered skill(s) needed by the task | Required before changing architecture/policy, recording memory, asserting career experience, or modifying authoritative sources |
| Direct skill execution | Handle a request that fits one reusable workflow without agent coordination | `analyze-job-description` or `career-direction-review` | The skill's existing evidence and decision boundaries remain in force |

No executable agent currently exists in `agents/`; the README now defines the
coordination boundary without introducing a new agent or a second runtime.
Provider configuration, retrieval, RAG, memory semantics, and workflow logic
remain owned by their existing abstractions.

## Unnecessary Agent Complexity

- One agent per directory or per skill when direct skill execution is enough.
- Provider clients, embedding logic, retrieval policy, or memory writeback in
  agent definitions.
- Autonomous loops that make architecture, career, repository, or memory
  changes without human approval.
- Loading the entire repository when the current task needs only one skill and
  its canonical sources.

## Minimal Integration Plan

- Keep the current agent layer declarative until a real multi-skill use case
  requires executable coordination.
- If implemented, load the skill registry, invoke the existing skill workflow,
  retrieval/RAG, and configured runtime abstractions, then verify the result.
- Require explicit human approval before persisting decisions, memory, career
  evidence, or policy changes.
- Add integration tests at the time an executable coordinator is introduced;
  do not create an agent solely to mirror the directory structure.

## Validation

- PASS — `agents/README.md` explicitly separates coordination from skills,
  provider configuration, retrieval/RAG, and memory.
- PASS — the registry contains the two active skills used by the plan, with no
  agent definitions to duplicate their workflows.
- PASS — human approval boundaries are explicit for consequential changes.
- PASS — no executable agent or autonomous behavior was added without a
  concrete multi-skill requirement.

Status: COMPLETED

## Exit Criteria

- Agents orchestrate rather than duplicate.
- Human approval boundaries remain explicit.

---

# Phase 13 — Add Observability, Failure Handling, and Performance Review

## Objective

Make the Local AI system diagnosable and efficient without prematurely optimizing.

## Codex Prompt

```text
Review EngineeringOS Local AI observability, failure handling, and performance.

Follow AGENTS.md.

Tasks:

1. Identify the important runtime boundaries:
   - configuration resolution,
   - provider connectivity,
   - model availability,
   - embedding,
   - indexing,
   - retrieval,
   - generation.
2. Verify failures can be attributed to the correct boundary.
3. Ensure logs contain useful diagnostics without storing sensitive prompt/context data unnecessarily.
4. Review cold model load time, inference latency, retrieval latency, and index rebuild cost where measurable.
5. Identify storage growth in runtime indexes and caches.
6. Do not optimize without evidence.
7. Do not add a heavyweight observability platform unless justified.

Report:

## Runtime Boundaries
| Boundary | Observable? | Failure Message Useful? | Improvement |
| --- | --- | --- | --- |

## Performance Baseline
- model load:
- inference:
- retrieval:
- index build:
- runtime storage:

## Highest-Value Improvements
1. ...
2. ...
```

## Runtime Boundaries

| Boundary | Observable? | Failure Message Useful? | Improvement |
| --- | --- | --- | --- |
| Configuration resolution | Yes — typed configuration errors reach the CLI failure boundary | Yes — names the missing or invalid setting | Add a low-volume command/boundary label to structured logs. |
| Provider connectivity | Yes — `LLMError`, `doctor`, and `llm status` report endpoint/connectivity | Yes — distinguishes HTTP, connection, and timeout failures | Log endpoint, operation, and elapsed time; never prompt/context contents. |
| Model availability | Yes — `llm status` lists runtime models; provider failures remain visible | Mostly — provider-specific missing-model responses may still vary | Record configured role and availability result without duplicating provider logic. |
| Embedding | Yes — response shape and configured dimension checks fail explicitly | Yes — identifies missing vector, invalid values, or dimension mismatch | Measure per-request latency and batch/index throughput before optimizing. |
| Indexing | Yes — missing/invalid index and empty embeddings raise `KnowledgeIndexError` | Yes — identifies the index path and rebuild condition | Record chunk count, build duration, and index size. |
| Retrieval | Yes — invalid limits, stale memory, and embedding-contract mismatches are explicit | Yes — retrieval returns clear insufficient-evidence behavior | Record query-independent counts and duration, not query text or retrieved content. |
| Generation | Yes — empty output, HTTP errors, connection errors, and timeouts are explicit | Yes — failure type and configured timeout are visible | Record role, outcome, and duration without logging prompts or answers. |

The existing CLI and typed exceptions make major failures diagnosable. Runtime
telemetry is intentionally lightweight rather than a new observability
platform; `logs/` currently contains only its repository README.

## Performance Baseline

- model load: not isolated; one configured chat request completed in **5.44 s**
  wall time, including provider request and model behavior.
- inference: **5.44 s** for one minimal configured chat request returning `OK`.
- embedding: **1.63 s** for one configured 768-dimensional embedding request.
- retrieval: **48.1–78.1 ms** for cosine search over 347 chunks using a
  deterministic local test vector; this excludes provider embedding latency.
- index build: **44.7 ms** for Markdown parsing/chunking with a deterministic
  fake embedding runtime; provider embedding time is excluded.
- runtime storage: **5,912,175 bytes / 5.7 MiB** for
  `runtime/index/knowledge.json` containing 347 chunks; no runtime log data is
  currently stored.

## Highest-Value Improvements

1. Add structured, low-volume boundary timings and failure categories for
   provider, embedding, indexing, retrieval, and generation, excluding prompts,
   retrieved text, and generated answers.
2. Measure cold versus warm model latency and full index rebuild throughput
   separately before changing concurrency, caching, or model selection.
3. Add index statistics and storage-growth checks so rebuild cost and generated
   state remain visible over time.

## Validation

- PASS — one configured chat request completed through EngineeringOS and the
  provider abstraction in 5.44 s.
- PASS — one configured embedding request returned 768 dimensions in 1.63 s.
- PASS — deterministic retrieval/index measurements were captured without
  calling the provider for bulk work.
- PASS — `python3 -m unittest discover -s tests` (28 tests).
- PASS — `python3 eng.py validate`.

Status: COMPLETED

## Exit Criteria

- Major runtime failures are diagnosable.
- A basic performance baseline exists.
- Optimization decisions are evidence-based.

---

# Phase 14 — Portability, Backup, Recovery, and Final End-to-End Validation

## Objective

Prove EngineeringOS Local AI can survive infrastructure changes and can be rebuilt.

## Codex Prompt

```text
Perform the final EngineeringOS Local AI portability and end-to-end validation.

Follow AGENTS.md. Do not perform unrelated refactoring.

Tasks:

1. Verify the authoritative repository does not depend on provider-owned model binaries.
2. Verify model storage can move without changing the root architecture.
3. Verify provider endpoint changes are configuration-only.
4. Verify the primary LLM can be changed through configuration.
5. Verify indexes can be rebuilt from authoritative knowledge.
6. Identify what must be backed up versus what can be regenerated.
7. Verify machine-specific configuration is clearly separated from portable project configuration.
8. Run the complete supported Local AI path:
   - config resolution,
   - provider resolution,
   - model inference,
   - embedding,
   - indexing,
   - retrieval,
   - RAG,
   - relevant memory integration,
   - relevant skill invocation.
9. Verify important failures are surfaced clearly.
10. Run the final validation required by project governance.

Report:

## Portability
| Scenario | Supported? | Required Change |
| --- | --- | --- |
| Move model storage to another disk | Yes/No | ... |
| Move Ollama to another host | Yes/No | ... |
| Replace Ollama with another provider | Yes/No | ... |
| Change primary LLM | Yes/No | ... |
| Rebuild indexes from scratch | Yes/No | ... |
| Restore EngineeringOS on a new machine | Yes/No | ... |

## Backup Classification

### Must Back Up
- ...

### Can Regenerate
- ...

### Machine-Specific
- ...

## End-to-End Result
- PASS/FAIL

## Remaining Risks
- ...

## Final Recommendation
- ...
```

## Portability

| Scenario | Supported? | Required Change |
| --- | --- | --- |
| Move model storage to another disk | Yes | Change provider-owned storage only; EngineeringOS has no model-storage path dependency. |
| Move Ollama to another host | Yes | Change the configured endpoint or `ENGINEERINGOS_OLLAMA_ENDPOINT`. |
| Replace Ollama with another provider | No, not currently | Add a provider adapter implementing the existing runtime contract and validate it; no repository architecture change is required. |
| Change primary LLM | Yes | Change the logical model binding in `configs/ai/models.json` and ensure the model is available from the configured provider. |
| Rebuild indexes from scratch | Yes | Run `python3 eng.py knowledge index`; the final rebuild produced 363 chunks. |
| Restore EngineeringOS on a new machine | Yes, with provider prerequisites | Restore the repository/configuration, install compatible Python/provider tooling, make the endpoint reachable, and rebuild generated indexes. |

## Backup Classification

### Must Back Up

- Tracked repository sources and governance: code, `configs/`, `knowledge/`,
  `memory/`, `career/`, `skills/`, `agents/`, and prompts.
- Provider-neutral configuration and the endpoint environment contract; do not
  place secrets or machine-specific paths in tracked files.

### Can Regenerate

- `runtime/index/knowledge.json` and other generated runtime caches.
- Logs and Python cache files.
- Embeddings and retrieval state derived from tracked sources and the configured
  embedding contract.

### Machine-Specific

- Ollama installation, downloaded model binaries, provider host/port, and the
  `ENGINEERINGOS_OLLAMA_ENDPOINT` override.
- Python environment and other local operating-system dependencies.

## End-to-End Result

- PASS — configuration and provider resolution succeeded.
- PASS — configured model availability, inference, and 768-dimensional
  embedding succeeded.
- PASS — authoritative knowledge plus controlled memory rebuilt into one shared
  index with 363 chunks.
- PASS — retrieval returned the expected memory and authoritative knowledge
  sources.
- PASS — grounded RAG succeeded with `--include-memory`; memory remained
  contextual and did not become an authoritative citation.
- PASS — `career-direction-review` ran against canonical career sources without
  modifying them.
- PASS — important failure handling exposed a clear missing-index error.

## Remaining Risks

- Only the Ollama provider adapter is implemented; provider replacement remains
  a planned extension.
- Full rebuild cost depends on provider availability, model warm-up, and one
  embedding request per chunk; cold versus warm behavior was not isolated.
- Ambiguous questions whose retrieved context is memory-only may correctly
  return insufficient evidence; callers should ask a source-grounded question
  when an authoritative answer is required.

## Final Recommendation

- PASS the current Local AI path for the configured Ollama provider.
- Back up tracked sources/configuration and regenerate the runtime index after
  restoring or changing provider infrastructure.
- Add another provider adapter or structured runtime telemetry only when a
  concrete portability/diagnostic need justifies it.

Status: COMPLETED

## Exit Criteria

EngineeringOS Local AI is considered operational when:

```text
stable architecture
    -> configuration-driven providers/models
    -> successful inference
    -> reproducible embeddings/indexes
    -> reliable retrieval
    -> grounded RAG
    -> controlled memory
    -> reusable skills
    -> bounded agents
    -> observable runtime
    -> portable/recoverable system
```

---

# Suggested Practice Order

Run the phases in this order:

```text
1  Architecture
2  Governance
3  Provider/model configuration
4  Provider smoke test
5  Embedding
6  Indexing
7  Retrieval
8  RAG
9  Evaluation
10 Memory
11 Skills
12 Agents
13 Observability/performance
14 Portability/final validation
```

Do not skip directly to agents before retrieval, RAG, and evaluation are stable.

---

# Compact Prompt Template for Future EngineeringOS AI Work

```text
Goal:
<one concrete outcome>

Scope:
<target subsystem, files, or responsibility area>

Constraints:
- Follow AGENTS.md.
- Keep context narrow.
- Reuse existing abstractions.
- Do not modify unrelated files.
- Do not modify protected architecture without explicit approval.

Tasks:
1. ...
2. ...
3. ...

Validation:
<smallest relevant checks>

Report:
- result
- evidence
- files involved
- remaining risks
- smallest required fix
```

---

# Storage Decision

Save this file in the existing prompt area:

```text
prompts/EngineeringOS_Local_AI_End_to_End_Practice.md
```

Do not create a new folder.

This file is a practice roadmap, not an alternate architecture policy. The root README, governance documents, local READMEs, manifests, registries, ADRs, tests, and skills remain authoritative for their respective responsibilities.
