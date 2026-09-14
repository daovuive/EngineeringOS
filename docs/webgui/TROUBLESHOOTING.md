# EngineeringOS WebGUI Troubleshooting

[WebGUI home](README.md) · [Operations](OPERATIONS.md) ·
[Architecture](ARCHITECTURE.md)

Start with `scripts/eos-status`. Use `--deep` only when the local health,
Ollama, and model checks pass, because it performs a real RAG request.

## Page does not open

- **Possible cause:** Web process is stopped, wrong port, port bind failed, or
  the browser is not on the same host/WSL network context.
- **Diagnose:** `curl -v http://127.0.0.1:8081/health`; then
  `ss -ltnp | grep ':8081\b'`. Check the foreground terminal or
  `systemctl status engineeringos-web --no-pager` on the deployed host.
- **Fix:** Start the documented foreground process, or restart the confirmed
  systemd unit. Use the actual `--port` in both URL and health checks.
- **Relevant files/logs:** `engineering_os/web.py`; foreground stderr/stdout;
  `journalctl -u engineeringos-web` when externally supervised.

## Port already in use

- **Possible cause:** another EOS instance or unrelated process owns 8081.
- **Diagnose:** `ss -ltnp | grep ':8081\b'`; do not kill a process until its
  owner and purpose are known.
- **Fix:** Stop the duplicate through its owner/service, or start EOS with an
  unused port such as `--port 8082` and update local/tunnel origin configuration
  deliberately.
- **Relevant files/logs:** `engineering_os/web.py` (`--port`, `DEFAULT_PORT`).

## Page opens but shows “Application unavailable”

- **Possible cause:** `/health` fetch failed, the page was opened from a file or
  different origin, or a proxy serves stale/static content without the API.
- **Diagnose:** open browser network tools and inspect `GET /health`; run curl
  against the exact page origin. The normal page must be served by EOS, not
  opened as `file://`.
- **Fix:** use `http://127.0.0.1:<port>/` or correct the tunnel origin. Restart
  the Python process after deploying source changes.
- **Relevant files/logs:** `app.js` `initialize()`; `web.py` `do_GET()`.

## Submit appears to do nothing

- **Possible cause:** empty/whitespace input, an in-flight request has disabled
  the button, JavaScript failed to load, or the expected shortcut was wrong.
- **Diagnose:** check the global error, Activity, browser console, and network
  panel. Ask EOS submits by button or `Ctrl+Enter`; plain Enter adds a newline.
- **Fix:** enter non-empty text, wait for/reconcile the current request, reload
  `/app.js`, and retry once. Do not repeatedly submit a mutating operation.
- **Relevant files/logs:** `app.js` `submitAsk()` and `bindEvents()`;
  `tests/test_web.py` input-clear contract.

## Ask input clears unexpectedly or does not clear

- **Current contract:** after non-empty input is accepted, `submitAsk()` copies
  the trimmed query and clears the textarea before the request. Empty input is
  not cleared. Both button and `Ctrl+Enter` call the same handler.
- **Diagnose:** inspect the loaded `/app.js` and browser cache/network response;
  verify the running service was restarted after deployment. The Models chat
  input is separate and currently does not clear.
- **Fix:** hard reload or restart the stale service. If changing behavior,
  preserve the local captured query and update `tests/test_web.py`.
- **Relevant files/logs:** `engineering_os/web_static/app.js` `submitAsk()` and
  `submitChat()`.

## Answer never appears / operation remains running

- **Possible cause:** local generation can be slow, Ollama reached its 300 s
  timeout, the two-operation semaphore is occupied, or browser connectivity was
  interrupted. No partial tokens are rendered.
- **Diagnose:** inspect Activity and browser network timing; run
  `scripts/eos-status`; check Ollama `/api/ps`; inspect service journal. A page
  reload turns a running Activity into **Completion unknown**.
- **Fix:** verify dependencies, allow one bounded request to complete, then
  retry manually. Reloading does not cancel or replay server work. Reconcile
  state before retrying index/project mutations.
- **Relevant files/logs:** `web.py` semaphore and handlers; `llm.py` timeout;
  `app.js` `runOperation()`.

## “Streaming stops” or no tokens appear progressively

- **Possible cause:** progressive browser streaming is not implemented; this is
  expected current behavior, not a broken SSE/WebSocket connection.
- **Diagnose:** the network request stays pending and then returns one JSON
  response. There is no EventSource, WebSocket, or AbortController in `app.js`.
- **Fix:** wait for the completed verified response or diagnose an actual
  timeout. Do not bypass grounding to imitate streaming. A streaming redesign
  is separate architecture work.
- **Relevant files/logs:** `llm.py` `_request()`/`request_json_lines()`;
  `web.py` `_send_json()`; [streaming architecture](ARCHITECTURE.md#4-streaming-flow).

## Ollama unavailable

- **Possible cause:** Ollama is stopped, endpoint override is wrong, WSL cannot
  reach the host, or a firewall/network rule changed.
- **Diagnose:** `python eng.py llm status`,
  `curl -v http://localhost:11434/api/version`, and inspect
  `ENGINEERINGOS_OLLAMA_ENDPOINT` plus `configs/ai/providers.json`.
- **Fix:** start/restart Ollama using its installed host procedure or correct
  the endpoint environment. Restart EOS if its process environment changed.
- **Relevant files/logs:** `configs/ai/providers.json`, `llm.py`; Ollama's own
  external logs.

## Configured model unavailable

- **Possible cause:** a role maps to a model not installed under the exact
  configured name.
- **Diagnose:** `python eng.py llm status` and `python eng.py llm pull-plan`;
  compare `/api/tags` with `configs/ai/models.json`.
- **Fix:** run the reviewed `ollama pull ...` command from the pull plan or
  deliberately change the role mapping and rebuild the index if the embedding
  contract changes.
- **Relevant files/logs:** `configs/ai/models.json`, Models workspace, `llm.py`.

## RAG unavailable or returns 500

- **Possible cause:** missing/incompatible index, unavailable embedding/RAG
  model, malformed persisted index, or runtime failure.
- **Diagnose:** Project → Knowledge status; `python eng.py knowledge search
  'EngineeringOS' --limit 1`; inspect the action endpoint for
  `knowledge.index-status`; check Ollama.
- **Fix:** restore runtime/model availability, then run
  `python eng.py knowledge index`. Do not edit JSON vectors manually.
- **Relevant files/logs:** `runtime/index/knowledge.json`, `knowledge.py`,
  `query.py`, `web.py`.

## EOS says “Insufficient evidence”

- **Possible cause:** no eligible chunks, filters exclude evidence, or the top
  reranked score is below the confidence threshold. This is an intentional
  abstention and returns HTTP 200.
- **Diagnose:** remove unintended filters, inspect source metadata, try Search
  only, and enable Debug retrieval for synthetic/non-sensitive questions.
- **Fix:** add/index authoritative knowledge, correct metadata/filter choices,
  or ask a more specific question. Do not lower thresholds just to force an
  answer.
- **Relevant files/logs:** `query.py`, `rag.py`, retrieval settings in
  `configs/settings.json`.

## Uploaded document is saved but not searchable

- **Possible cause:** auto-index was disabled or indexing failed after the
  source was safely saved. HTTP 207 represents this partial state.
- **Diagnose:** inspect the ingestion status and Knowledge row (`Saved only`),
  verify Ollama/embedding model, and inspect Project index status.
- **Fix:** use **Retry indexing** for the saved inbox document or rebuild the
  complete index. If organization moved/copied the file, rebuild to refresh
  citation paths.
- **Relevant files/logs:** `ingestion.py`, `knowledge.py`, `library.py`;
  [knowledge guide](../KNOWLEDGE_INGESTION.md).

## PDF upload fails

- **Possible cause:** malformed/encrypted/scanned PDF, disabled PDF policy,
  over-2-MiB file, missing dependency, or text extraction/font issue.
- **Diagnose:** verify the file header/size and `.venv`; run `python -m pip
  check`. OCR is explicitly disabled, and encrypted PDFs are unsupported.
- **Fix:** install project dependencies, provide a non-encrypted text PDF under
  the limit, or perform external reviewed OCR and import the resulting UTF-8
  text. Do not enable silent OCR by changing Web code.
- **Relevant files/logs:** `pdf.py`, `ingestion.py`, `pyproject.toml`,
  `configs/settings.json`.

## Source link fails or returns 400

- **Possible cause:** citation refers to memory/log rather than openable
  knowledge, file moved after indexing, path is outside knowledge, symlink or
  unsupported type, or the document exceeds the inspection limit.
- **Diagnose:** inspect `source_details`, the current library row, and the raw
  request. Only knowledge-source Markdown/PDF entries receive open URLs.
- **Fix:** rebuild after moving/organizing files; open non-knowledge evidence
  through its governed owner; do not widen the endpoint to arbitrary paths.
- **Relevant files/logs:** `library.py` path checks; `web.py`
  `_serialize_response()` and `_handle_open_document()`.

## 404 response

- **Possible cause:** route/method is not in the explicit allowlist, wrong
  workflow ID, stale frontend calling a removed route, or guessed static path.
- **Diagnose:** compare the request with the route table in
  [Architecture](ARCHITECTURE.md#http-surface) and `workflow_ids()`.
- **Fix:** call the supported path/method or deploy frontend/backend together.
  Do not expect `/web_static/...` or arbitrary files to be served.
- **Relevant files/logs:** `web.py` `do_GET()`/`do_POST()`; `tests/test_web.py`.

## 500 or 422 response

- **Possible cause:** 500 is a sanitized unexpected/query/internal failure;
  422 means a valid action/workflow request could not complete.
- **Diagnose:** preserve the response code/body, correlate with Activity and
  terminal/journal, then check runtime, index, and input constraints. Backend
  exception details are intentionally hidden from the browser.
- **Fix:** repair the dependency/config/input cause and retry. Reproduce with
  synthetic input in foreground if the journal has insufficient detail.
- **Relevant files/logs:** handler-specific exception blocks in `web.py`;
  external systemd journal.

## Cloudflare returns 502 or origin unavailable

- **Possible cause:** EOS is stopped, tunnel is stopped, ingress points to the
  wrong port, or WSL/network state changed. A 502 is produced upstream; EOS
  itself has no 502 response path.
- **Diagnose:** check local `/health` first, then `systemctl status cloudflared`,
  its journal, and the host's actual tunnel ingress. Compare the configured
  origin port with the EOS listener.
- **Fix:** restore the local WebGUI before restarting the tunnel. Correct
  deployment ingress only with the owner; its source is not in this repository.
- **Relevant files/logs:** `scripts/eos-status`, `journalctl -u cloudflared`,
  external tunnel configuration.

## Public URL redirects or returns 401/403

- **Possible cause:** Cloudflare Access is protecting the application. The
  unauthenticated post-release check observed HTTP 302.
- **Diagnose:** use `curl -I https://eos.dao-labs.org/health` and an authorized
  browser. Distinguish Access login/denial from origin failure.
- **Fix:** authenticate through the approved Access policy or ask its owner for
  access. Do not put Access tokens in commands committed to the repository.
- **Relevant files/logs:** external Cloudflare Access audit; `scripts/eos-status`.
