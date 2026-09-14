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
| EOS-S3-01 | 3 | Build a local Markdown/PDF index with optional safe logs | Ollama embedding model; pypdf | implemented and verified | token-aware/page-aware chunks, schema 2.0 lexical state, and log controls tested |
| EOS-S3-02 | 3 | Hybrid dense/BM25 retrieval, filtering, and reranking | Compatible JSON index | implemented and verified | `eng.py knowledge search`; identifier/RRF/filter/rerank/debug tests |
| EOS-S3-03 | 3 | Grounded answers with abstention and inline sources | Retrieval and generation models | implemented and verified | `eng.py knowledge ask`; confidence and grounding regressions in `tests/test_rag.py` |
| EOS-S3-04 | 3 | Storage adequate for current corpus scale | JSON index | implemented and verified | Current 1,732 chunks load below 0.7 s and live retrieval p95 is below 0.64 s; capacity benchmark and thresholds are in `docs/POST_RELEASE_ENGINEERING_REPORT.md` |
| EOS-S3-05 | 3 | Optional vector DB for scale/filtering demands | Measured limitation and approved storage decision | conditional; not justified | `KEEP_JSON_INDEX`; representative 25k chunks cross the prospective 2 s retrieval/5 s load targets, so re-evaluate before that scale rather than migrate now |
| EOS-S3-06 | 3+ | Import Markdown/plain text/text PDF and make it available to RAG automatically | Existing JSON index, embedding role, pypdf | implemented and verified locally | file/text/stdin/PDF, page citations, automatic/skipped indexing, dedupe, retry and truthful states; ingestion/PDF/web tests |
| EOS-S3-07 | 3+ | Incrementally and safely update one document in the JSON index | Compatible embedding contract | implemented and verified locally | Atomic persistence, writer coordination, stale-chunk replacement, unrelated-chunk preservation and failure recovery tests pass in `tests/test_ingestion.py` |
| EOS-S2-05 | 2+ | Use supported EOS commands through task-oriented protected web controls | Shared application services and action catalog | implemented and verified locally | Upload/paste/retry/open, explicit allowlisted actions, confirmations and workflow controls pass `tests/test_actions.py` and `tests/test_web.py`; coverage and host-level exception in `docs/COMMAND_COVERAGE.md` |
| EOS-S4-01 | 4 | Review explicit source files or diffs without execution or mutation | Reasoning model; optional index | implemented and verified | CLI and tested web Code Review paths; live CLI smoke passed. Running web process requires an operator restart to load the new route |
| EOS-S4-02 | 4 | Review requirements for quality, constraints, and traceability | Reasoning model; optional index | implemented and verified | CLI and tested web Requirement Review paths; live CLI smoke passed |
| EOS-S4-03 | 4 | Produce an explicitly unapproved ADR draft with options/trade-offs | Reasoning model; optional index | implemented and verified | CLI and tested web ADR Assistant paths; live CLI smoke passed; title/sections enforced by `engineering_os/workflows.py` |
| EOS-S5-01 | 5 | Produce a bounded architecture proposal with explicit uncertainty | Requirement/ADR guidance, reasoning model, optional index | implemented and verified | CLI/web paths and deterministic tests pass; schema-constrained live runs returned validated proposals with and without optional retrieval. Mermaid, stages, ADR options, and source excerpts are assembled deterministically; observed buffered latency was roughly 2.5–3 minutes |
| EOS-S5-02 | 5 | Run deterministic quality gates on GitHub | GitHub Actions | implemented; remote fix pending | Release run `34766061187` was verified failed: missing dependency install and executable mode. Both fixes pass the exact sequence in a clean local environment; commit/push and green remote rerun remain external work |
| EOS-S5-03 | 5 | Evaluate usefulness across representative real cases | Non-sensitive local dataset and review metrics | implemented with documented weak cases | 12-category Hybrid RAG dataset and live/retrieval reports measure source hit, confidence, abstention, citations, unsupported claims and latency; 6/12 meet all expectations and weak cases remain explicit |
| EOS-WEB-01 | WebUI | Implement the five owner-approved Knowledge, Ask EOS, Engineering, Models, and Project workspaces | Existing shared services; approved mockups; ADR-2026-09-13-03 | implemented and verified locally | Real-data workspaces with no demo mode, PDF upload/library, Hybrid RAG filters/debug, bound previews, and loopback web regression tests |
| EOS-RAG-01 | RAG | Upgrade dense-only retrieval to local Hybrid RAG without weakening grounding | schema 2.0, pypdf, ADR-2026-09-13-04 | implemented and verified locally | chunking, metadata, BM25, RRF, reranking, confidence, PDF/log safety, CLI/action/web tests |

## Current priorities

1. Commit/push the locally verified CI fixes and confirm the next remote run is
   green; deployment/restart stays operator-owned.
2. Improve ambiguity/insufficient-evidence behavior, exact filenames, canonical
   source preference, and terminology variation against the retained dataset.
3. Define a verified streaming-event contract before exposing incremental text;
   keep JSON and re-run its capacity benchmark as the corpus approaches 10k.
