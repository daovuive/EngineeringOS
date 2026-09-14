# EngineeringOS WebGUI Operations

[WebGUI home](README.md) · [Troubleshooting](TROUBLESHOOTING.md) ·
[Project operations](../OPERATIONS.md)

This runbook separates repository-supported commands from deployment-specific
systemd and Cloudflare state. Run commands from the repository root unless a
different path is shown.

## Prerequisites

- Python 3.10 or newer. Ubuntu/WSL should use a virtual environment because the
  system Python may be externally managed.
- Runtime dependencies declared in `pyproject.toml`: `pypdf` and `fonttools`.
- A readable EngineeringOS repository and valid JSON configuration under
  `configs/`.
- Ollama reachable at the configured endpoint for RAG, model, embedding,
  workflow, ingestion-with-indexing, and index-rebuild operations. Static UI,
  `/health`, library metadata, and some project actions do not require Ollama.
- The configured role models installed in Ollama. Use the pull plan below to
  see the exact commands without downloading anything.

Prepare a local environment:

```bash
cd /home/daoph/projects/EngineeringOS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python eng.py validate
```

The repository defines only one Web runtime environment variable:

```bash
export ENGINEERINGOS_OLLAMA_ENDPOINT='http://<OLLAMA-HOST>:11434'
```

Omit it to use `http://localhost:11434`. Do not commit endpoint-specific
credentials or secrets; the current Ollama adapter has no credential setting.

## Start WebGUI

Foreground, using the repository and default port:

```bash
cd /home/daoph/projects/EngineeringOS
source .venv/bin/activate
python -m engineering_os.web --port 8081
```

Expected startup line:

```text
EngineeringOS local API listening on http://127.0.0.1:8081
```

Open `http://127.0.0.1:8081/`. From another working directory, fix the project
root explicitly:

```bash
python -m engineering_os.web \
  --root /home/daoph/projects/EngineeringOS \
  --port 8081
```

There is no `eng.py web` command, auto-reloader, build command, or repository
startup script. Restart the process after changing Python or static files.

### Deployed systemd service

`scripts/eos-status` defaults to service name `engineeringos-web`, and that
unit was observed on the previously inspected WSL host. The unit file and its
install procedure are not in this repository. On a host where the operator has
confirmed that exact unit, use:

```bash
systemctl status engineeringos-web --no-pager
sudo systemctl start engineeringos-web
```

Do not create or replace a unit from this document; first inspect the host's
actual `systemctl cat engineeringos-web` output.

## Stop WebGUI

For the foreground process, press `Ctrl+C` in its terminal. `main()` catches the
interrupt and closes the HTTP server.

For the confirmed deployed unit:

```bash
sudo systemctl stop engineeringos-web
```

## Restart WebGUI

Foreground: stop with `Ctrl+C`, then run the start command again.

Confirmed deployed unit:

```bash
sudo systemctl restart engineeringos-web
systemctl status engineeringos-web --no-pager
curl -fsS http://127.0.0.1:8081/health
```

Updating the working tree does not reload the running Python process.

## Verify Health

Process liveness:

```bash
curl -fsS http://127.0.0.1:8081/health
```

Expected body:

```json
{"status": "ok"}
```

`/health` proves that the Web process can answer HTTP. It does not validate the
index, Ollama, installed models, RAG generation, or Cloudflare.

Run the repository diagnostic:

```bash
scripts/eos-status
scripts/eos-status --deep
```

FAST mode checks systemd state, configured service names, local health, Ollama,
models, ports, the public endpoint, and recent warning counts. DEEP additionally
sends a real RAG query and can take up to 120 seconds. The script is read-only
and accepts deployment overrides documented in [project operations](../OPERATIONS.md).

Useful direct checks:

```bash
ss -ltnp | grep -E ':(8081|11434)\b'
curl -fsS http://localhost:11434/api/version
curl -fsS http://localhost:11434/api/tags
python eng.py llm status
python eng.py knowledge search 'EngineeringOS' --limit 1
```

The search command validates index compatibility and retrieval without answer
generation. A full API check is:

```bash
curl -fsS -X POST http://127.0.0.1:8081/api/v1/query \
  -H 'Content-Type: application/json' \
  --data '{"query":"What is EngineeringOS?","limit":3}'
```

## Logs

The WebGUI currently has no repository-implemented file logger. Although
`configs/settings.json` contains a `logging` section, `engineering_os.web` does
not consume it. `LocalQueryHandler.log_message()` suppresses Python's default
HTTP access log so question text is not written automatically.

Foreground startup/errors go to the terminal. On the confirmed systemd host,
inspect supervisor output and warnings:

```bash
journalctl -u engineeringos-web -n 200 --no-pager
journalctl -u engineeringos-web --since '1 hour ago' -p warning --no-pager
journalctl -u cloudflared -n 200 --no-pager
```

Do not enable request-body logging in production. If deeper diagnosis is
required, reproduce with synthetic inputs in a foreground process. The
browser's Activity view stores only the last eight bounded summaries and is not
an authoritative audit log.

## Verify Dependencies

```bash
source .venv/bin/activate
python -m pip check
python eng.py validate
python eng.py doctor
python eng.py llm status
python eng.py llm pull-plan
```

`llm pull-plan` prints Ollama pull commands but does not run them. To inspect
the index through the same Web action used by Project health:

```bash
curl -fsS -X POST http://127.0.0.1:8081/api/v1/actions/knowledge.index-status \
  -H 'Content-Type: application/json' \
  --data '{"values":{}}'
```

If the index is missing or incompatible, rebuild it only after confirming
Ollama and the embedding model:

```bash
python eng.py knowledge index
```

The CLI rebuild uses the same shared index implementation. It replaces the
previous compatible JSON file only after all documents and embeddings succeed.

## Remote Access

Repository evidence shows this deployment shape:

```mermaid
flowchart LR
    Browser[Remote browser] -->|HTTPS| Access[Cloudflare Access]
    Access --> Tunnel[Cloudflare Tunnel]
    Tunnel -->|local origin| EOS[127.0.0.1:8081]
```

The status script defaults to `https://eos.dao-labs.org` and service
`cloudflared`; post-release checks observed an unauthenticated 302 from
Cloudflare Access. The tunnel identifier, ingress file, DNS route, credentials,
Access application, and service unit are not in this repository. Therefore:

- audit them with the deployment owner before changing remote access;
- keep EOS bound to loopback and do not expose Ollama directly;
- do not copy tokens, credentials, or tunnel files into documentation;
- treat HTTP 302/401/403 from an unauthenticated health request as potentially
  Access-protected, then test through an authenticated browser.

Read-only host checks:

```bash
systemctl status cloudflared --no-pager
systemctl cat cloudflared
curl -I https://eos.dao-labs.org/health
```

## Shutdown and Recovery

### WSL or Windows restart

1. Confirm WSL/systemd is running: `systemctl is-system-running`.
2. Check `engineeringos-web` and `cloudflared` only if those units are installed.
3. Check Ollama using `/api/version` and the configured endpoint.
4. Run `scripts/eos-status`; use `--deep` only after FAST checks pass.
5. If units are not installed, start Ollama using its host-specific procedure
   and start EOS with the foreground command above.

### Web service crash

1. Read the foreground output or `journalctl -u engineeringos-web`.
2. Check for a port collision and validate project/config files.
3. Restart the process, verify `/health`, then run one synthetic operation.

### Ollama restart or failure

1. Verify the configured endpoint and `ENGINEERINGOS_OLLAMA_ENDPOINT`.
2. Check `/api/version`, `/api/tags`, and `python eng.py llm status`.
3. Restart Ollama using its installation's procedure; none is owned here.
4. Retry the user operation manually. The WebGUI does not queue or replay it.

### Ingestion or index failure

If upload returns “saved, indexing failed,” the document remains in
`knowledge/inbox/`. Fix Ollama/model/index compatibility and click **Retry
indexing**, or run the retry command printed by `eng.py add-knowledge`. A full
rebuild is available in Knowledge through preview/confirmation or by running
`python eng.py knowledge index`. Never delete the previous index as a first
recovery step; atomic updates preserve the last valid file.

### Interrupted browser operation

After reload, a formerly running Activity item becomes **Completion unknown**.
Use **Check current state** when offered, inspect library/index/project state,
and only then retry. The browser intentionally does not replay mutations.

## Optional Browser Smoke Test

The repository's optional WSL installer uses network and sudo access to prepare
Playwright under the user's home directory. Review it before running:

```bash
bash scripts/setup-wsl-webui-testing.sh http://127.0.0.1:8081
```

It tests the real page, not demo data, and is not a CI gate.
