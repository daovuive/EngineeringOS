Implement the EngineeringOS web application to closely match the five approved mockup images in this conversation.

The mockups are the approved visual specification. Build the working application behind them, preserving their layout, navigation, visual hierarchy, controls, and interaction patterns.

Repository: `/home/daoph/projects/EngineeringOS`

Canonical development checkpoint:
`prompts/Resume_EngineeringOS_Development.md`

Do the implementation, validation, and documentation updates. Do not stop at a plan, static page, or simulated UI.

## 1. Approved visual references

Use the attached mockups as the primary design references:

1. Knowledge — document library and Add knowledge drawer.
2. Ask EOS — RAG conversation, retrieval settings, and source preview.
3. Engineering — workflow selection, input panel, and results with evidence.
4. Models — provider/model status, role mapping, chat, embeddings, and pull plan.
5. Project — project actions, configuration, activity states, and confirmation dialog.

If accessible in this environment, the original images are:

```text
Knowledge:
/mnt/c/Users/daoph/.codex/generated_images/01a09605-9346-7de0-a804-d7d61642e8a9/exec-1a20da4d-3cc8-4763-921e-83a1d81acb26.png

Ask EOS:
/mnt/c/Users/daoph/.codex/generated_images/01a09605-9346-7de0-a804-d7d61642e8a9/exec-d1c95c79-8298-46b5-bff0-740d085203a0.png

Engineering:
/mnt/c/Users/daoph/.codex/generated_images/01a09605-9346-7de0-a804-d7d61642e8a9/exec-7e9c4375-b3b3-4bd3-a71f-0111e7005c54.png

Models:
/mnt/c/Users/daoph/.codex/generated_images/01a09605-9346-7de0-a804-d7d61642e8a9/exec-023470e6-1abd-4b48-84cd-2b17217cac16.png

Project:
/mnt/c/Users/daoph/.codex/generated_images/01a09605-9346-7de0-a804-d7d61642e8a9/exec-97befc28-6c52-449b-b42c-9311b17bf292.png
```

Inspect the images before making visual decisions. If neither attachments nor these files are accessible, complete repository inspection and request the missing references before claiming visual fidelity.

Use the Knowledge image as the canonical shared shell when small differences exist between mockups.

The images contain sample data and occasional illustrative text. Reproduce the design faithfully, but use real application state in the working product. Correct inconsistent counts, misleading labels, and typographical errors.

## 2. Visual implementation contract

Preserve:

- Light, restrained desktop interface.
- Approximately 240px left sidebar at a 1536px viewport.
- EngineeringOS branding and workspace context.
- Navigation: Knowledge, Ask EOS, Engineering, Models, Project.
- Shared Activity entry.
- Top breadcrumb and compact status area.
- White cards, subtle borders, small corner radii, and generous spacing.
- Graphite text, muted secondary text, deep teal primary actions, pale teal active states, amber partial-failure states.
- Outline icons and clear typography.
- The per-screen column proportions and control placement shown in the references.
- English interface labels.

Suggested starting tokens, adjusted after visual comparison:

```text
Background:      #F7F8FA
Surface:         #FFFFFF
Primary text:    #20282B
Secondary text:  #737F89
Primary action:  #166B5B
Selected state:  #E7F2EE
Border:          #E3E8EB
Corner radius:   approximately 8px
```

Do not replace the design with a generic admin template, terminal interface, marketing dashboard, or unrelated component styling.

Use the existing frontend stack. Build a small shared set of components for the shell, buttons, fields, tabs, cards, status badges, drawers, dialogs, source references, and activity results. Avoid introducing a second frontend framework.

Use deterministic sample fixtures for visual tests. Display “DEMO DATA · NOT CONNECTED” only in an actual preview or fixture mode. Production must show truthful runtime state.

Desktop fidelity is the priority. Add responsive behavior:
- Collapse navigation on narrow screens.
- Stack content panels.
- Make the knowledge drawer usable at mobile widths.
- Prevent clipped controls and page-level horizontal overflow.

Ensure keyboard navigation, visible focus, accessible labels, dialog focus management, and readable contrast.

## 3. Inspect and preserve EOS

Before editing, read applicable AGENTS.md instructions, the root README, governance documents, structure manifest, relevant child README files, architecture, and the existing resume checkpoint.

Inspect the actual:
- CLI commands and application services.
- Web routes, authentication, and API conventions.
- Runtime abstraction and model configuration.
- Knowledge storage, indexing, retrieval, grounding, and citations.
- Tests, CI, and working-tree changes.

Treat earlier progress reports as snapshots, not verified current state.

Constraints:
- Preserve existing CLI behavior and working RAG functionality.
- Preserve unrelated modifications and untracked files.
- Updating the specified resume document is explicitly authorized, including if it is currently untracked. Read and preserve relevant existing information.
- Keep the root README and its protection baseline unchanged without explicit approval of a concrete diff.
- Follow structure governance and child README navigation rules.
- Reuse the existing runtime and JSON index.
- Do not introduce a vector database, agent framework, new cloud provider, or deployment infrastructure merely for this UI.
- Do not push, deploy, or restart production as part of this task.

## 4. Shared application architecture

CLI and web must use the same application services for equivalent operations.

```text
CLI adapter ─┐
             ├─ Application services ─ Runtime / knowledge / configuration
Web adapter ─┘
```

Keep business rules and persistence out of UI components and argument parsing.

Inventory the requested capabilities and map each to:
- Existing implementation or missing shared service.
- Web screen and action.
- Inputs and results.
- Validation evidence.
- Remaining blocker, if any.

Reuse existing command metadata where useful. Do not create a competing registry or duplicate the same validation in several independent implementations.

If a required service is missing, implement the smallest complete shared capability needed. Never fabricate a successful result to make a screen appear functional.

## 5. Knowledge screen

Match the library and right-hand Add knowledge drawer.

Implement:
- Document list with folder, indexing state, and meaningful actions.
- Search/filter controls.
- Open and inspect a saved document.
- Upload `.md` and `.txt`.
- Paste text.
- Optional document title.
- Automatic indexing enabled by default.
- Save without indexing.
- Duplicate detection.
- Prevention of accidental overwrites.
- Retry indexing after a successful save followed by an indexing failure.
- Rebuild the complete index with preview/confirmation of its effect.

Browser upload must accept files from the user’s device. Do not require arbitrary server paths.

Keep external originals intact. Store documents in governed knowledge locations with useful provenance and durable citation paths.

Use the existing embedding pipeline and configured embedding model. Do not call a chat model merely to rewrite or summarize content before indexing.

Indexing must:
- Preserve unrelated entries.
- Avoid duplicate documents and chunks on retries.
- Replace stale chunks for changed documents.
- Respect embedding-model and vector-dimension compatibility.
- Preserve the last valid index if an update fails.
- Coordinate concurrent writers.
- Make successful CLI and web changes visible to the running application.

For partial failure, show separate save and index outcomes. Keep the saved document and provide a working retry.

### Folder organization

Implement “Suggest folder with local LLM.”

- Derive allowed destinations from actual governance and configuration.
- Ask the installed model to suggest among those destinations.
- Show the suggested folder, filename, and concise explanation.
- Let the user choose another approved folder.
- Do not create arbitrary model-suggested paths.
- Do not copy or move a document until the user confirms the preview.
- Bind execution to the previewed document and destination; revalidate before applying.

For browser uploads, use Copy/import semantics. Move is available only for existing governed project documents.

A move must preview source, destination, collision handling, and effects on indexing/citations. Preserve integrity if any step fails.

### Minimal CLI

Implement or preserve these equivalent commands:

```bash
python3 eng.py add-knowledge "my-document.md"
python3 eng.py add-knowledge --file "my-document.md"
python3 eng.py add-knowledge --file "my-document.md" --auto-index
```

Also support:

```bash
python3 eng.py add-knowledge --text "New knowledge"
python3 eng.py add-knowledge --stdin --title "My note" < notes.txt
python3 eng.py add-knowledge "my-document.md" --no-index
```

Index automatically by default. Reject conflicting inputs and flags. Support spaces and Unicode. Require no category, destination, model, or index-path argument for ordinary use.

## 6. Ask EOS screen

Match the conversation area, retrieval settings, source cards, and source preview.

Implement:
- Ask with RAG.
- Search only.
- Model-role selection.
- Optional recent project memory, disabled by default.
- Retrieval limit.
- Confidence threshold using the existing retrieval semantics.
- Answers with supported citations.
- Source excerpts and opening the saved source document.
- Clear behavior when retrieval is empty or evidence is insufficient.

Validate settings server-side. Do not invent confidence scores or evidence claims.

Keep chat without retrieval distinct from knowledge-grounded answers.

Display model output as plain text. Source cards and application controls may be structured UI, but do not interpret model text as HTML.

## 7. Engineering screen

Match the four workflow selectors and the shared input/output workspace:

- Code Review.
- Requirement Review.
- ADR Draft.
- Solution Architecture.

Support uploaded files or pasted text, relevant options, logical model-role selection, and optional supporting project knowledge.

Provide:
- Code findings with evidence and supported source locations.
- Requirement findings and suggested improvements.
- ADR drafts with context, alternatives, consequences, and references.
- Architecture proposals with boundaries, trade-offs, implementation stages, and evidence.
- Mermaid source.
- Copy and Markdown download actions.

Use the mockup’s Proposal/Mermaid source/Evidence pattern where applicable. Adapt result labels to the selected workflow without changing the overall layout.

Keep generated ADRs and architecture proposals explicitly marked Draft. Do not automatically approve them or modify reviewed source files.

Render Mermaid as plain-text source, matching the mockup. Do not execute arbitrary generated HTML or introduce automatic diagram rendering in this scope.

Treat uploaded and retrieved material as untrusted input, not privileged instructions.

## 8. Models screen

Match the provider/status cards, role mapping, chat panel, embedding action, and pull plan.

Implement:
- Configured provider and runtime status.
- Configured and available models.
- Logical role to configured model mapping.
- Chat with an installed model.
- Embeddings for supplied text.
- View the model download/pull plan.
- Refresh status.
- Navigation to read-only runtime configuration.

Use actual model names and availability. Handle unavailable providers and models clearly.

Viewing a pull plan must not automatically download models.

## 9. Project screen

Match the health cards, action cards, read-only configuration, Activity panel, and confirmation dialog.

Implement:
- EngineeringOS version.
- Preview and initialize missing project structure.
- Preview and synchronize missing governed content.
- Governance validation.
- Project and runtime diagnostics.
- Read-only views for Settings, Runtime, Structure, Templates, and Skills.

Previews must describe actual proposed changes and preserve existing content. Confirmation dialogs must show consistent file/folder counts.

Keep the following outside the website:
- Starting or stopping the EOS server.
- Editing repository-root or configuration-file paths.
- Host-level systemd, port, SSH, or Cloudflare diagnostics.
- Automatic ADR approval.
- Deployment or production restart.

Do not add hidden endpoints that expose these excluded operations.

## 10. Activity, progress, and browser state

Provide one shared Activity mechanism across screens.

- Show real execution stages for long-running operations.
- Use indeterminate progress if a percentage cannot be measured.
- Prevent duplicate submissions while an operation is running.
- Allow unrelated safe interactions to continue.
- Remember the latest action result in the browser.
- Avoid persisting secrets or full sensitive documents in browser storage.
- Handle unavailable browser storage gracefully.

On reload, a request that lacked a final result must become “Completion unknown” until authoritative status resolves it.

Do not assume success, failure, or cancellation. Do not automatically repeat a potentially completed mutation.

Provide an appropriate status-check or reconciliation action before retrying.

Reuse existing execution infrastructure. If needed, add a small bounded operation-status mechanism without introducing an unnecessary external queue service.

## 11. Web safety and mutation boundaries

Implement these requirements in the server, not only in the interface:

- Restrict document access to governed knowledge locations.
- Validate upload type, encoding, size, filenames, and destination.
- Prevent traversal and symlink escape.
- Reject arbitrary shell commands and arbitrary server paths.
- Invoke explicit application actions rather than constructing shell commands from input.
- Require same-origin mutation requests and apply CSRF protection appropriate to existing authentication.
- Preserve existing access protection across APIs, uploads, downloads, and operation results.
- Render untrusted/model content through safe text rendering.
- Require confirmation for consequential mutations such as moves, full index rebuilds, and structure synchronization.
- Revalidate previewed changes before execution.
- Return useful errors without exposing credentials or unrelated filesystem content.

Do not treat a confirmation dialog as a replacement for server authorization.

## 12. Incremental execution and checkpoints

Work in coherent increments:

1. Baseline inspection, capability map, and shared visual shell.
2. Knowledge ingestion, indexing, and folder preview.
3. Search, RAG, citations, and source inspection.
4. Engineering workflows.
5. Models and Project operations.
6. Cross-screen activity, regression verification, and visual refinement.

Integrate safety and testing into each increment rather than postponing them.

Update `prompts/Resume_EngineeringOS_Development.md`:
- After initial inspection.
- After each coherent implementation and verification step.
- When a blocker or next action changes.
- Before ending the session.

Include:
- Timestamp and objective.
- Constraints and approval boundaries.
- Dated branch/working-tree snapshot.
- Completed, implemented-but-unverified, in-progress, and blocked items.
- Relevant changed files.
- Exact tests run and results.
- Outstanding visual differences.
- Next concrete action and commands.
- Links to canonical backlog, design, workflow, and architecture documents.

Keep one concise current checkpoint. Preserve relevant context and avoid an ever-growing transcript.

Tell the next agent to verify current repository state, reconcile changes since the checkpoint, continue unfinished work, and update the same file.

## 13. Documentation, workflows, and ADRs

Documentation is part of every completed increment.

Update:
- CLI and web usage guides.
- Knowledge ingestion, indexing, retry, and organization workflows.
- Engineering workflow instructions.
- Relevant testing and operational instructions.
- Architecture documentation.
- Roadmap/backlog status.
- Child README navigation.
- Resume checkpoint.

Review existing ADRs. Create or supersede an ADR for significant decisions such as shared CLI/web services, index-write coordination, or operation recovery. Record context, alternatives, consequences, and validation evidence.

Do not create an ADR for every minor UI change. Follow approval policy and never label a proposal as approved without evidence.

Maintain canonical documents and references rather than duplicating instructions.

## 14. Functional and visual verification

Use the existing test framework and temporary test data.

Verify:
- Shared CLI/web behavior.
- Upload and text ingestion.
- Automatic indexing and save-only mode.
- Duplicate/collision handling.
- Partial failure and safe retry.
- Incremental indexing and unrelated-entry preservation.
- Folder suggestions restricted to approved destinations.
- Preview/confirmation and copy/move consistency.
- RAG retrieval, citations, memory option, and settings.
- Engineering workflow contracts and draft status.
- Model operations and Project actions.
- Access controls, same-origin mutations, and unsafe-input rejection.
- Duplicate submission prevention.
- Reload and completion-unknown behavior.

Ordinary tests must not require live Ollama, private knowledge, or network access.

When available, run live smoke tests with synthetic documents and configured local models. Verify retrieval and citations rather than merely checking HTTP success. Clean up only test-created artifacts.

For visual verification:
1. Run the application in a local development/test environment.
2. Capture all five screens using deterministic fixtures.
3. Reproduce the important states shown in the mockups, including the knowledge drawer and Project confirmation.
4. Compare at approximately 1536×1024 and against each reference’s native dimensions where useful.
5. Fix substantial differences in layout, spacing, typography, colors, and control placement.
6. Check at least one narrow viewport and keyboard interaction.

Use real browser tooling when available. Do not claim visual equivalence from code inspection alone.

Run governance validation and relevant regression checks. Update existing CI checks where appropriate.

If tooling or live services are unavailable, report the exact unverified checks and continue independent work.

## 15. Completion and final report

Completion requires a working application faithful to the approved mockups, not static pages or hardcoded successful responses.

Report:
- Implemented capabilities by screen.
- Main changed files.
- Local run instructions and navigation.
- Actual test results.
- Screenshots of the implemented screens.
- Remaining visual differences or functional blockers.
- Updated guides, workflows, and ADRs.
- Current resume checkpoint and next action if anything remains.

Do not claim complete visual fidelity, security verification, or end-to-end functionality without the corresponding evidence.

Start by inspecting the repository and reference images, then implement the work.

## Required WebUI decision record and implementation tracking

This section supplements the existing documentation and checkpoint requirements. Treat these records as implementation deliverables.

### 1. Record the WebUI decision before implementation

Inspect the repository’s existing ADR location, numbering, template, and approval policy.

Create or update a dedicated ADR for:

“Extend the existing EngineeringOS WebUI to provide a governed interface for knowledge, RAG, engineering workflows, model operations, and project operations.”

Document:
- Context: EOS already has a CLI, local runtime, RAG capabilities, and an existing web application.
- User requirement: implement the five referenced mockups and their functional requirements.
- Decision drivers: usability, visual fidelity, shared CLI/web behavior, maintainability, extensibility, and governance.
- Alternatives considered and the rationale for the selected approach.
- Integration with the existing application and runtime.
- Supported operations and explicit exclusions.
- Consequences for document storage, indexing, concurrency, access control, and interrupted operations.
- Validation and completion criteria.
- Decision status, date, and approval evidence where available.

Distinguish approval of the visual direction from approval of additional architectural changes. Follow existing approval rules without inventing new approval requirements.

Use this ADR as the canonical record. Create additional ADRs only for independently significant decisions. Link related decisions rather than duplicating their rationale.

If later findings change a recorded decision, update its status or supersede it according to repository conventions. Preserve the decision history.

### 2. Maintain a persistent implementation log

Reuse a suitable existing development log. If none exists, create one governance-compliant Markdown log dedicated to the WebUI implementation.

Record its exact path in the resume checkpoint and relevant documentation.

Append a concise entry after each meaningful implementation step, failed verification that changes the plan, blocker, or architectural deviation.

Each entry must contain:
- Timestamp with timezone.
- Step identifier or backlog item.
- What changed and why.
- Relevant files and related ADR identifiers.
- Verification performed and actual results.
- Remaining issues or limitations.
- Next action.
- Commit reference only when an actual commit exists.

Preserve earlier entries. Correct mistakes through a clearly identified correction rather than silently rewriting history.

Keep the log useful for auditing implementation. Do not store raw conversation transcripts, credentials, personal document contents, or verbose internal reasoning.

### 3. Keep the three records consistent

Use clear responsibilities:

- ADR: what was decided, why, alternatives, and consequences.
- Implementation log: what happened over time and the evidence.
- `prompts/Resume_EngineeringOS_Development.md`: current verified state and the next concrete action.

Link these records to each other and to the canonical backlog. Avoid copying the same detailed content into all three.

Update the implementation log and resume checkpoint after each completed step and before ending the session. Record incomplete or blocked work honestly.

### 4. Completion gate

Before declaring the WebUI complete:
- Reconcile the implemented architecture with its ADRs.
- Record any deviations and unresolved approvals.
- Add a final implementation-log entry with validation evidence and remaining limitations.
- Update the resume checkpoint with the final state.
- Verify documentation links and governance compliance.

The final report must provide the exact paths to the WebUI ADR, implementation log, and resume checkpoint, together with their current status.