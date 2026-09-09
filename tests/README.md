# tests

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Tests for CLI behavior, governance, ingestion/index integrity, RAG, bounded
workflows, explicit actions, and the local web adapter. Test by module or
observable capability; temporary data belongs in
`tmp/`. Default tests mock model calls and require no Ollama, model weights,
private documents, Cloudflare credentials, or public network.

## Running the tests

Run the same deterministic suite as CI:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Target a subsystem while iterating, then run the full suite before handoff:

```bash
python3 -m unittest tests.test_ingestion tests.test_add_knowledge_cli
python3 -m unittest tests.test_actions tests.test_web
```

Live Ollama, deployed-service, and browser-visual smoke checks are separate
operator steps. They must use synthetic inputs and are not required CI gates.
The shipped WebUI has no demo-data mode: browser smoke tests connect to the
real local API. Historical captured evidence is documented in the
[WebUI Guide](../docs/WEBUI_GUIDE.md) and verifies rendering/layout at the time
of capture, not current runtime connectivity.

On WSL Ubuntu/Debian, the optional installer below prepares an isolated
Playwright workspace and can smoke-test a running real-data EOS page:

```bash
bash scripts/setup-wsl-webui-testing.sh http://127.0.0.1:8081
```

Review it before use: it invokes `sudo apt-get`, installs NVM/Node/Chromium from
the network, and writes tooling under `~/.local/share/eos-webui-testing/`. It
does not enable demo data and is not part of the default deterministic suite.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
