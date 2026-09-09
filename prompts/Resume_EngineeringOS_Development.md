# EngineeringOS — Development Checkpoint

Last updated: 2026-09-13T15:43:38+07:00

## Instructions for the next coding agent

Read `AGENTS.md`, the protected root `README.md`, applicable governance and
area READMEs, then this checkpoint. Verify Git state and reconcile changes made
after this snapshot. Continue from the next incomplete step without restarting
completed work, revalidate evidence when it may be stale, and keep updating this
same checkpoint after each coherent increment.

## Objective and scope

Implement the five owner-approved WebUI mockups as a working governed
application while preserving provider-neutral ingestion, RAG, workflows,
shared CLI/web services, and a reliable handoff here.

Constraints: do not change the protected root README/baseline, deploy, push,
change authentication, expose arbitrary shell commands/files, introduce a
vector database or new service, or modify unrelated user content. Reuse the
JSON index, runtime abstraction, and shared application services. Imported
documents are untrusted data.

## Repository snapshot

- Snapshot: 2026-09-13; branch `agent/python-cli-sdv-knowledge`; HEAD `59684ac`.
- Worktree is intentionally dirty with the Sprint 4–5 implementation and
  pre-existing staged/user-owned content. Preserve
  `knowledge/personal/lessons-learned/psychological-pattern-map.md` contents.
- Updating this checkpoint is explicitly authorized by the ingestion task.
- Root `README.md` remains unchanged.

## Completed and verified

- Sprint 1–5 bounded workflows and prior governance repair are implemented;
  75 tests and `python3 eng.py validate` passed before this increment.
- A separate `knowledge organize` command classifies an explicit Markdown file
  with the local reasoning model into configured existing destinations. It is
  not the ingestion path and must not choose paths for `add-knowledge`.
- Baseline command inventory confirmed: init, sync, validate, doctor, version;
  config views; LLM status/pull-plan/chat/embed; knowledge index/organize/search/
  ask; and four engineering workflows.
- Web coverage includes RAG query, four workflows, ingestion/retry/document
  viewing, and allowlisted EOS actions. It binds loopback, serves an explicit
  static allowlist, validates requests, limits size/concurrency, and exposes no
  arbitrary file route or shell command.
- Current query service reloads the JSON index per request, so successful atomic
  CLI index updates will be visible without web-process cache invalidation.
- Added governed `knowledge/inbox/`, shared ingestion in
  `engineering_os/ingestion.py`, and document-level indexing in
  `engineering_os/knowledge.py`. Markdown, `.markdown`, `.txt`, direct text,
  and stdin are supported; imported files are deduplicated by SHA-256 and
  collisions use a deterministic hash suffix.
- Index writes use an atomic replace plus thread/process writer locks. Updating
  one document preserves unrelated chunks, replaces stale chunks, and avoids
  re-embedding unchanged content. A failed embed preserves both the saved
  document and prior valid index.
- Added `add-knowledge` positional/`--file`/`--text`/`--stdin` forms, automatic
  indexing by default, `--no-index`, explicit conflict validation, retry output,
  Unicode/path handling, and truthful RAG readiness status.
- CLI help was rechecked and documents supported formats, the minimal
  positional form, and automatic indexing.
- Added synchronous bounded web ingestion through
  `POST /api/v1/knowledge/ingest`, retry through
  `POST /api/v1/knowledge/retry-index`, and safe viewing under
  `GET /api/v1/knowledge/document`. Browser file content is read on the user's
  device and sent as validated JSON; no server filesystem path is accepted.
- UI now supports file upload, pasted text, optional title, default auto-index,
  visible saved/indexed/partial states, retry, and an open-document link.
  Mutation requests reject cross-origin browser requests; document reads are
  constrained to the configured inbox.
- Added `engineering_os/actions.py`, a small allowlisted catalog and shared
  dispatcher for version, init/sync, validation, doctor, configuration, LLM
  status/pull-plan/chat/embed, and knowledge index/search/ask/organize. The web
  endpoint accepts typed values only; no shell command is constructed.
- Added the task-oriented “EOS commands” UI with role, retrieval, threshold,
  confirmation, and organizer controls. Long operations use the existing
  synchronous semaphore; the browser persists the last result and marks an
  in-flight action as completion-unknown after reload rather than replaying it.
- Added `docs/COMMAND_COVERAGE.md`. All `eng` commands have a web workflow;
  startup-only project/config path overrides remain server-owned. The host-level
  `scripts/eos-status` exception is explicit because exposing systemd/port
  inspection would widen the HTTP security boundary.
- Added `docs/KNOWLEDGE_INGESTION.md` as the canonical CLI/web user and recovery
  guide; synchronized architecture, operations, command coverage, area
  READMEs, roadmap, backlog, changelog, and CI/testing instructions.
- Added two ADRs for ingestion/index consistency and shared CLI/web application
  actions. Both remain `Proposed`, explicitly pending owner approval. Corrected
  ADR-0002 to show that ADR-0003 supersedes it and refreshed the ADR index.
- Converted four CLI dispatch tests to `unittest.TestCase`; they had previously
  been invisible to the repository's `unittest discover` CI command.
- Pre-WebUI ingestion/action baseline: 103 unittest tests passed together with
  Python compilation, `python3 eng.py validate`, `git diff --check`, and
  documented help checks.
- Live synthetic acceptance used an isolated `/tmp` project and real Ollama:
  CLI import and web upload each saved/indexed one document; CLI and web RAG
  retrieved both with valid inbox citations; repeat imports returned
  `unchanged`; the index contained exactly two documents/two chunks. The web
  server was stopped and the temporary project was deleted.
- Added governed knowledge library reads, bounded source excerpts, advanced RAG
  options, preview-bound knowledge organization, and revalidated preview tokens
  for full-index and project structure mutations.
- Replaced the linear browser form with functional Knowledge, Ask EOS,
  Engineering, Models, and Project workspaces plus shared Activity, responsive
  navigation, drawer/dialog focus handling, and plain-text copy/download.
- Added explicit `?demo=1` fixture mode. Edge headless executed the JavaScript
  and captured five 1536×1024 screens plus one 500×844 responsive drawer image
  under `docs/webui-screenshots/`; every fixture is visibly disconnected.
- Added `docs/WEBUI_GUIDE.md`, proposed ADR-2026-09-13-03, and the append-only
  `docs/WEBUI_IMPLEMENTATION_LOG.md`. Targeted application/web tests pass 46/46.
- Final regression passes 110/110 tests with loopback sockets enabled. Python
  compilation and `git diff --check` pass, and the protected root README has no
  working-tree diff.
- Project init/sync now refuses a confirmed preview when current governance or
  template errors block it; the browser surfaces that gate before confirmation.
- Governed knowledge reads reject parent traversal and symlinks, including
  symlinks whose resolved target would otherwise remain under `knowledge/`.
- Production hardening removed the `?demo=1` branch and all embedded sample
  documents, answers, model states, activities, and mutation previews from the
  shipped JavaScript. Every URL now loads current state from the real local API;
  unavailable services remain visibly unavailable instead of being replaced by
  demo results. Web tests assert that demo markers and switches are absent.
- Moved `setup-wsl-webui-testing.sh` into the governed `scripts/` area,
  normalized it to executable mode, and verified it with `bash -n`. The script
  was not executed. `python3 eng.py validate` now passes.
- Production-only regression passes all 82 non-socket tests, Python compilation,
  `git diff --check`, static no-demo assertions, and protected-root checks. The
  environment rejected the required approval for the remaining 28 loopback web
  tests before execution because the tool-approval quota was exhausted; the
  last pre-hardening full-suite baseline remains 110/110 passing.
- Runtime-readiness inspection found no visible Ollama or EngineeringOS web
  process. `eng.py llm status` resolved the real configured Ollama endpoint and
  models, but sandbox socket policy returned `Operation not permitted`; systemd
  inspection was similarly blocked. No service state was changed. Documented
  the optional governed WSL Playwright installer and its sudo/network effects.
- Final consistency review reconfirmed passing governance, Python compilation,
  working-tree whitespace checks, an unchanged protected root README, and zero
  demo-mode markers in the shipped static bundle. The configured pull plan is
  the four documented Ollama models; availability could not be queried through
  the sandbox.

## In progress

- WebUI implementation, production-data hardening, setup-script governance,
  repository validation, and all available deterministic checks are complete.
  The 28 loopback tests and live local production-data browser smoke await
  renewed execution approval and running local services.
- ADR-2026-09-13-03 remains `Proposed`. The mockups are explicitly approved
  visual direction; added architectural decisions still await owner acceptance.

## Failed, skipped, or blocked checks

- No current implementation blocker.
- Remote GitHub Actions and deployed-service behavior are not verified; deploy
  and service restart are outside authorization.
- The environment rejected the loopback-enabled regression request before it
  ran because the tool-approval quota was exhausted. This is an environment
  limitation, not a test failure; 82/82 non-socket tests pass.
- Microsoft Edge headless was available through the Windows installation and
  rendered executable JavaScript for all five deterministic desktop fixtures
  and one responsive viewport. A deployed live-data visual pass is still
  pending operator deployment.
- Standalone JavaScript syntax checking was attempted but skipped because
  `node` is not installed (`node --check` exited 127). Static assets and their
  behavior contracts are covered by web tests.
- `git diff --cached --check` reports three trailing-space lines in the stale
  checkpoint version staged before this increment. The current working-tree
  checkpoint passes `git diff --check`; staging was intentionally left
  untouched, so review and re-stage the current file before committing it.
- The setup script has not been executed because it installs OS and browser
  dependencies with `sudo` and network access; only its placement, mode, and
  Bash syntax were verified.
- The deployed web process still runs the previously deployed code until an
  operator deploys this working tree and restarts it.

## Remaining steps in dependency order

1. Rerun all 110 tests once loopback execution approval is available.
2. Smoke-test the page against the real local API/runtime without demo data.
3. Owner reviews the three proposed ADRs.
4. Reconcile and deliberately stage the current working files, replacing the
   stale staged checkpoint without altering unrelated user-owned knowledge,
   then commit.
5. Run remote GitHub Actions.
6. Deploy/restart the operator-owned web service, then visually inspect the
   five workspaces through the protected route.

Next concrete action: start Ollama, pull any missing models from
`python3 eng.py llm pull-plan`, start EOS with
`python3 -m engineering_os.web --port 8081`, then rerun all 110 tests and the
real-data browser smoke once loopback approval is available. No automatic push
or external deployment was performed.

## Useful commands and references

```bash
git status --short
python3 eng.py --help
python3 eng.py validate
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m engineering_os.web --port 8081
python3 eng.py add-knowledge --text "New knowledge" --title "My note"
```

- Knowledge ingestion: `docs/KNOWLEDGE_INGESTION.md`
- Coverage matrix: `docs/COMMAND_COVERAGE.md`
- Decision index: `docs/DECISIONS.md`
- WebUI ADR: `ADR/ADR-2026-09-13-03-governed-five-screen-webui.md`
- WebUI implementation log: `docs/WEBUI_IMPLEMENTATION_LOG.md`
- Backlog: `docs/PRODUCT_BACKLOG.md`
- Architecture: `docs/ARCHITECTURE.md`
- Operations: `docs/OPERATIONS.md`

The session-created server is stopped and its Windows Temp captures were
removed. The six governed screenshot artifacts remain under
`docs/webui-screenshots/` as intentional evidence.
