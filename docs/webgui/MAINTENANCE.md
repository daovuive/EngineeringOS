# EngineeringOS WebGUI Maintenance

[WebGUI home](README.md) · [Architecture](ARCHITECTURE.md) ·
[Tests](../../tests/README.md)

## Source Ownership Map

| Intent | Primary source | Also inspect |
| --- | --- | --- |
| Change page structure, labels, controls, or accessibility | `engineering_os/web_static/index.html` | `app.js`, `style.css`, `tests/test_web.py` |
| Change input, Submit, keyboard, Activity, or dialog behavior | `engineering_os/web_static/app.js` | matching element IDs in `index.html`, `tests/test_web.py` |
| Change layout, colors, or responsive breakpoints | `engineering_os/web_static/style.css` | `index.html`, browser smoke evidence |
| Add or change a static/API route | `engineering_os/web.py` | frontend caller, shared service, `tests/test_web.py` |
| Add a reusable Web action | `engineering_os/actions.py` | CLI/core implementation, frontend, `tests/test_actions.py`, `test_web.py` |
| Change question request/response fields | `web.py` and `app.js` | `query.py`, `rag.py`, `tests/test_web.py`, `test_query.py` |
| Change Hybrid retrieval or confidence behavior | `query.py`, `retrieval.py`, `reranking.py` | `configs/settings.json`, RAG/retrieval tests |
| Change answer grounding/citation behavior | `rag.py` | `query.py`, `web.py`, RAG/query/web tests |
| Change model transport, role mapping, or timeout | `llm.py`, `configs/ai/*.json` | actions/query/workflows and LLM tests |
| Change upload, deduplication, retry, or atomic update | `ingestion.py`, `knowledge.py` | `library.py`, `web.py`, ingestion/knowledge/web tests |
| Change library list or source opening policy | `library.py` | `web.py`, `app.js`, library/web tests |
| Change Engineering workflows | `workflows.py` | `web.py`, `app.js`, workflow/web tests |
| Change startup arguments or bind behavior | `web.py` | operations/security docs, web tests, deployment configuration |
| Add actual browser streaming | currently spans `llm.py`, `rag.py`, `web.py`, and `app.js` | requires protocol/security/grounding design and an ADR review |
| Change systemd or Cloudflare behavior | external deployment state; not currently owned in repo | `scripts/eos-status`, operations docs, deployment owner |

The static README at `engineering_os/web_static/README.md` defines local asset
rules. The WebUI guide is user-facing; this directory is the maintainer source.

## How to Make a Safe Change

1. Read the nearest source and its tests. For a cross-module change, trace from
   the browser event to `LocalQueryHandler`, then to the shared service.
2. Preserve the single implementation of business behavior. The Web adapter
   should validate/serialize; core logic belongs in shared modules used by CLI.
3. Keep static paths, actions, fields, model roles, metadata filters, and file
   access allowlisted. Never turn a browser value into a shell command or an
   arbitrary filesystem path.
4. Preserve pre-validation and preview/confirmation for mutations. Capture
   user input in a local variable before clearing or awaiting a request.
5. Add the smallest targeted tests, then run the relevant module tests.
6. Start the real local WebGUI, use synthetic data, and verify success,
   validation failure, unavailable dependency, keyboard, and responsive states.
7. Run the deterministic project gates below. Structural changes require
   `python eng.py validate`.
8. Update this documentation, the user guide if behavior changed, and the
   existing resume checkpoint. Do not modify the protected root README without
   explicit approval.

Recommended gates:

```bash
python3 -m unittest tests.test_web tests.test_actions
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall -q engineering_os tests
python3 eng.py validate
git diff --check
```

`tests/test_web.py` starts a loopback server. In a restricted sandbox it may
need explicit loopback permission; a denied bind is not an application test
failure. The repository currently has static source assertions for browser
behavior but no installed DOM unit-test runner.

## Change Impact Matrix

| Change | Likely affected components | Minimum validation |
| --- | --- | --- |
| Ask input or keyboard handling | `app.js`, `index.html` | static contract in `test_web`; manual click and Ctrl+Enter |
| Message/source rendering | `app.js`, response serializer | safe text rendering and web response tests; browser smoke |
| API schema or status code | `web.py`, `app.js`, shared caller | focused web tests for valid/invalid/large/cross-origin cases |
| New action | `ACTION_CATALOG`, `execute_action`, UI | action and web tests; confirmation tests if mutating |
| RAG retrieval policy | settings, query/retrieval/reranker | retrieval, query, RAG, action, and web regression |
| Citation/source policy | RAG, library, serializer, UI | RAG/library/web tests including traversal and weak evidence |
| Ingestion | web adapter, ingestion/index/library, UI | ingestion/library/web tests including HTTP 207 recovery |
| Workflow | workflows, web adapter, UI | workflow/action/web tests; confirm input stays unexecuted |
| Model/runtime config | config loaders and LLM adapter | LLM tests, `llm status`, synthetic live operation |
| Concurrency or timeout | provider config, semaphore, Ollama client | web concurrency and LLM timeout tests; load smoke |
| Static asset or responsive layout | all `web_static` files | web static tests plus desktop/mobile browser smoke |
| Streaming protocol | Ollama client, RAG verification, HTTP, UI | new unit/integration/browser tests and architecture decision |
| Bind/proxy/authentication | server and external deployment | security review, route/origin tests, local and protected remote smoke |

## Extension Points

These are supported by explicit registries or interfaces rather than filename
convention alone:

- `ACTION_CATALOG` plus `execute_action()` is the typed action boundary. New
  actions must declare accepted fields and implement server-side validation.
- `WORKFLOWS` and `WorkflowDefinition` register bounded engineering workflows;
  `/api/v1/workflows/<id>` rejects IDs not in this registry.
- Logical model roles in `configs/ai/models.json` let callers select purpose
  without hardcoding a model name. Only provider types implemented by
  `create_runtime()` are usable; currently that is Ollama.
- Retrieval/rerank/grounding dataclasses load centrally from settings, keeping
  CLI, Web query, and action behavior consistent.
- `STATIC_ASSETS` is intentionally explicit. Adding an asset requires adding a
  mapping; it is not a general static-directory mechanism.
- Library and ingestion services are reusable by CLI/Web while keeping path,
  size, duplicate, PDF, and atomic-index policies in one place.

## Confirmed Technical Debt

- End-to-end streaming is absent. Ollama NDJSON is read fully into memory,
  `request_json_lines()` returns a list, RAG verifies only after completion,
  and Web sends one JSON body.
- Browser requests have no timeout or cancellation. A stalled request remains
  pending until the runtime/network settles or the page reloads.
- `app.js` is a single 893-line global script with one mutable state object and
  direct DOM access. Screen boundaries are conventions, not modules.
- `index.html` is densely authored and all five workspaces are shipped as one
  page; there is no template/component system or asset pipeline.
- Browser behavior is mainly protected by static string/order assertions in
  `tests/test_web.py`; no repository-installed DOM/browser test suite runs in
  default CI.
- The Models screen labels single-turn exchanges as a conversation, but each
  `llm.chat` call sends only the current prompt. History is visual only. Its
  message input also remains populated after submission, unlike Ask EOS.
- PDF document bytes are fetched and converted with `response.text()` for the
  dialog, so the inline dialog is not a PDF renderer. The raw governed link is
  the usable browser-native PDF view.
- The configured Web logging section is not wired to the Web server, while the
  default access log is suppressed. Operational detail depends on terminal or
  external supervisor capture.
- The repository does not own the deployed systemd unit, Cloudflare tunnel,
  reverse proxy, or Access configuration. A new host cannot reproduce remote
  deployment from repository content alone.
- Activity is bounded browser-local status, not durable job tracking. Reload
  cannot determine whether a generic long operation completed; only selected
  operations offer state reconciliation.

## Possible Future Improvements

These are not current behavior or approved work:

- Introduce a verified event protocol that keeps claim verification and
  citations authoritative while improving perceived latency.
- Add request cancellation and an explicit browser/server timeout contract.
- Split frontend behavior by workspace and add a dependency-light DOM test
  harness before increasing UI complexity.
- Add a governed, secret-free deployment template and operator checklist if
  repeatable systemd/Cloudflare provisioning becomes a project requirement.
- Add structured, privacy-aware operational events without logging question or
  document bodies.
- Improve browser-native PDF preview and make single-turn model chat semantics
  clearer.

Any of these may change security or architecture boundaries and requires the
normal ADR review; this list is not authorization.
