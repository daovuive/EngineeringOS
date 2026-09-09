# Product Backlog

Last verified: 2026-09-13

The implementation and test references below are evidence anchors. `Verified`
means local checks passed; it does not mean remote GitHub Actions ran.

| ID | Sprint | Outcome and scope | Dependencies | Status | Observable acceptance and evidence |
| --- | --- | --- | --- | --- | --- |
| EOS-S1-01 | 1 | Governed, navigable repository structure | Manifest, README hierarchy | implemented and verified | `python3 eng.py validate` passes; `configs/project-structure.json`, `engineering_os/structure.py`, `tests/test_structure_governance.py` |
| EOS-S1-02 | 1 | Initialize/synchronize missing governed content without overwriting sources | Templates and manifest | implemented and verified | `eng.py init`/`sync` contracts covered by `tests/test_structure.py` and governance tests |
| EOS-S1-03 | 1 | CLI for version, config, validation, runtime, knowledge, and workflows | Python 3.10+ | implemented and verified | `python3 eng.py --help`; dispatch tests in `tests/test_cli.py` |
| EOS-S1-04 | 1 | Diagnose local environment, runtime, and project drift | Runtime configuration | implemented and verified | `python3 eng.py doctor` reports each boundary; `engineering_os/doctor.py` |
| EOS-S2-01 | 2 | Replaceable local AI runtime with Ollama adapter and logical model roles | Running Ollama for live use | implemented and verified | Mocked adapter tests pass; live status listed every configured model; `engineering_os/llm.py` |
| EOS-S2-02 | 2 | Local single-prompt chat | EOS runtime | implemented and verified | `eng.py llm chat`; runtime generation covered by `tests/test_llm.py` |
| EOS-S2-03 | 2 | Browser access without arbitrary file or internal-context exposure | Loopback service; external access policy is host-owned | implemented and verified | Static, health, and safe API tests in `tests/test_web.py`; `engineering_os/web.py` |
| EOS-S2-04 | 2 | Operational health visibility | curl, systemd on deployed WSL host | implemented and verified | `scripts/eos-status` fast/deep contracts in `tests/test_eos_status.py`; provisioning remains outside repo |
| EOS-S3-01 | 3 | Build a local Markdown knowledge index | Ollama embedding model | implemented and verified | `eng.py knowledge index`; embedding contract and chunk tests |
| EOS-S3-02 | 3 | Semantic search with configured filtering | Compatible JSON index | implemented and verified | `eng.py knowledge search`; cosine retrieval in `engineering_os/knowledge.py` |
| EOS-S3-03 | 3 | Grounded answers with abstention and inline sources | Retrieval and generation models | implemented and verified | `eng.py knowledge ask`; confidence and grounding regressions in `tests/test_rag.py` |
| EOS-S3-04 | 3 | Storage adequate for current corpus scale | JSON index | implemented and verified | Versioned JSON load/save contract is tested and operational |
| EOS-S3-05 | 3 | Optional vector DB for scale/filtering demands | Measured limitation and approved storage decision | planned | Accept only after a benchmark shows the JSON index misses an explicit latency, scale, update, or filtering target |
| EOS-S3-06 | 3+ | Import Markdown/plain text and make it available to RAG automatically | Existing JSON index and embedding role | implemented and verified locally | `add-knowledge` supports file/text/stdin, automatic or skipped indexing, dedupe, collision handling, retry and truthful states; `tests/test_ingestion.py`, `tests/test_add_knowledge_cli.py` |
| EOS-S3-07 | 3+ | Incrementally and safely update one document in the JSON index | Compatible embedding contract | implemented and verified locally | Atomic persistence, writer coordination, stale-chunk replacement, unrelated-chunk preservation and failure recovery tests pass in `tests/test_ingestion.py` |
| EOS-S2-05 | 2+ | Use supported EOS commands through task-oriented protected web controls | Shared application services and action catalog | implemented and verified locally | Upload/paste/retry/open, explicit allowlisted actions, confirmations and workflow controls pass `tests/test_actions.py` and `tests/test_web.py`; coverage and host-level exception in `docs/COMMAND_COVERAGE.md` |
| EOS-S4-01 | 4 | Review explicit source files or diffs without execution or mutation | Reasoning model; optional index | implemented and verified | CLI and tested web Code Review paths; live CLI smoke passed. Running web process requires an operator restart to load the new route |
| EOS-S4-02 | 4 | Review requirements for quality, constraints, and traceability | Reasoning model; optional index | implemented and verified | CLI and tested web Requirement Review paths; live CLI smoke passed |
| EOS-S4-03 | 4 | Produce an explicitly unapproved ADR draft with options/trade-offs | Reasoning model; optional index | implemented and verified | CLI and tested web ADR Assistant paths; live CLI smoke passed; title/sections enforced by `engineering_os/workflows.py` |
| EOS-S5-01 | 5 | Produce a bounded architecture proposal with explicit uncertainty | Requirement/ADR guidance, reasoning model, optional index | implemented and verified | CLI/web paths and deterministic tests pass; schema-constrained live runs returned validated proposals with and without optional retrieval. Mermaid, stages, ADR options, and source excerpts are assembled deterministically; observed buffered latency was roughly 2.5–3 minutes |
| EOS-S5-02 | 5 | Run deterministic quality gates on GitHub | GitHub Actions | implemented but unverified | `.github/workflows/ci.yml` defines governance, compile, test, and diff gates; no remote run was observed |
| EOS-S5-03 | 5 | Evaluate usefulness across representative real cases | Owner-selected non-sensitive scenarios and review rubric | planned | Record false findings, missing risks, evidence quality, latency, and owner acceptance without copying private inputs into tests/logs |
| EOS-WEB-01 | WebUI | Implement the five owner-approved Knowledge, Ask EOS, Engineering, Models, and Project workspaces | Existing shared services; approved mockups; ADR-2026-09-13-03 | implemented and verified locally | Five functional real-data workspaces with no runtime demo mode, bound previews, prior 110-test baseline, current 82/82 non-socket regression, five historical 1536×1024 screenshots and a 500px responsive screenshot; `eng.py validate` passes |

## Current priorities

1. Rerun the 28 loopback web tests when execution approval is available; the
   production-only static assertions and all 82 non-socket tests pass.
2. Review and either accept or reject the three proposed ADRs for governed
   ingestion/index updates, shared CLI/web actions, and the five-screen WebUI;
   implementation status does not imply architectural approval.
3. Run the GitHub Actions workflow remotely and resolve only reproducible gate
   failures; deploy/restart the web service only through the operator-owned
   process.
4. Evaluate Solution Architect on owner-selected representative cases and
   measure end-to-end streaming and latency.
5. Add a vector store only if measurements establish a concrete need.
