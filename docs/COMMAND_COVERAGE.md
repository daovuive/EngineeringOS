# EOS Command and Web Coverage

Last verified: 2026-09-13

This matrix inventories the supported command surface. Web actions are explicit
allowlisted application calls; there is no shell-command endpoint. The CLI and
web adapters call the same services under `engineering_os/`.

For user-facing ingestion commands, states, and recovery, use the canonical
[Knowledge Ingestion Guide](KNOWLEDGE_INGESTION.md). The shared action boundary
is recorded in a
[Proposed ADR](../ADR/ADR-2026-09-13-02-shared-cli-web-application-actions.md)
pending owner approval.

| Command or capability | Inputs and outputs | Shared application function | Web page/action | Execution | Status and evidence |
| --- | --- | --- | --- | --- | --- |
| `eng version` | Version text | package `__version__` | EOS commands → `project.version` | immediate | implemented; action/CLI tests |
| `eng init`, `eng sync` | Project/config overrides; creates only missing governed content | `ensure_structure` | Project → preview → confirmed initialize/synchronize; preview token is revalidated | immediate mutation | implemented; structure and action tests |
| `eng validate` | Project/config overrides; structured violations | `validate_structure` | Project → Run validation | immediate | implemented; governance and action tests |
| `eng doctor` | Fixed project/runtime configuration; diagnostic report | `run_doctor` | Project → Run diagnostics | potentially long | implemented; live host state remains environmental |
| `eng config [settings|runtime|structure|templates|skills]` | Section name; JSON configuration | configuration loaders | Project → read-only Configuration | immediate | implemented; action tests |
| `eng llm status` | Configured provider/models; available models | runtime definition and `list_models` | Models → Refresh status and role table | potentially long | implemented; mocked tests, local runtime previously verified |
| `eng llm pull-plan` | Configuration; printable pull commands | `build_pull_commands` | Models → View plan | immediate, no mutation | implemented; action catalog |
| `eng llm chat PROMPT [--role]` | Prompt and configured role; generated text | `LLMRuntime.generate` | Models → Chat with a model | potentially long | implemented; action tests |
| `eng llm embed TEXT` | Text; dimensions and vector preview | `LLMRuntime.embed` | Models → Generate embeddings | potentially long | implemented; action tests |
| `eng knowledge index` | Fixed knowledge/memory roots; chunk count and index path | `rebuild_index` | Knowledge → preview/confirm Rebuild index | long mutation | implemented synchronously; source snapshot is revalidated; atomic/writer-locked persistence tests |
| `eng knowledge search QUERY [--limit] [--include-memory]` | Query/options; scored sources and previews | `load_index`, `select_retrieval_chunks`, `search_index` | Ask EOS → Search only | potentially long | implemented; action/service tests |
| `eng knowledge ask QUERY` with retrieval thresholds, limit, role, and memory option | Question/options; grounded answer, citations, bounded excerpts | `query_knowledge` | Ask EOS → Ask with RAG and Retrieval settings | potentially long | implemented; query/web/action tests |
| `eng knowledge organize --file [--dry-run] [--move]` | Explicit Markdown; classified existing destination | organization preview/apply services | Knowledge drawer → Suggest folder → choose approved folder → confirm | potentially long mutation | implemented; content/destination binding and organizer safety tests |
| `eng add-knowledge PATH` / `--file` / `--text` / `--stdin`, title and index flags | One Markdown/text source; saved path, import/index status, chunk count | `ingest_path`, `ingest_text`, `update_document_index` | Add knowledge → device upload or pasted text, title, auto-index, retry/open | potentially long mutation | implemented; ingestion, CLI, web, concurrency and failure tests |
| `eng workflow code-review` | Files/text, optional retrieval/query; validated review | `run_workflow` | Engineering → Code Review | potentially long | implemented; workflow/web tests and prior live smoke |
| `eng workflow requirement-review` | Files/text, optional retrieval/query; validated review | `run_workflow` | Engineering → Requirement Review | potentially long | implemented; workflow/web tests and prior live smoke |
| `eng workflow adr-assistant` | Files/text, optional retrieval/query; unapproved ADR draft | `run_workflow` | Engineering → ADR Draft | potentially long | implemented; workflow/web tests and prior live smoke |
| `eng workflow solution-architect` | Files/text, optional retrieval/query; architecture proposal | `run_workflow` | Engineering → Solution Architecture | long | implemented; workflow/web tests and live acceptance |
| Global `--root`, `--structure-config`, `--template-config` | Select process-owned repository/config files | `ProjectPaths` | Fixed when the web process starts; not accepted from HTTP | startup-only | intentionally not a web user input; prevents arbitrary server-path access |
| `python -m engineering_os.web --root --port` | Starts the loopback adapter | `create_server` | Not applicable: this command hosts the web application | process lifecycle | implemented; deployment/restart remains operator-owned |
| `scripts/eos-status [--deep]` | Reads systemd, ports and deployed endpoints | repository diagnostic script | Partially represented by `project.doctor`; host/service detail is not exposed to HTTP | process/host-specific | explicit exception: exposing systemd/port inspection through the app would widen its security boundary |

## Long-running behavior

The current local stack uses bounded synchronous requests and the configured
runtime semaphore. The browser disables duplicate submission, labels long
actions, and stores the last action status/result locally. After reload, an
unfinished request is shown as interrupted or completion-unknown and is never
replayed automatically. A server-side queue is not introduced at the current
single-user scale; if measured proxy timeouts make synchronous operation
unusable, a persistent bounded job service is the next justified increment.

Pages and APIs retain the existing deployment protection. Mutation APIs also
require same-origin browser requests, and consequential repository mutations
require an explicit confirmation value.
