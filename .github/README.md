# .github

[Project charter](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

GitHub-specific repository automation. Default CI must remain deterministic and
must not require Ollama, model downloads, private documents, Cloudflare
credentials, or other live services.

The required pull-request path is defined in `workflows/ci.yml`: governed
structure validation, Python compilation, `unittest` discovery, and whitespace
checking. Live integration checks remain explicit operator workflows.

## Extension Rules

Register maintained subdirectories in the project manifest. Keep live service
checks explicit and separate from required pull-request gates.
