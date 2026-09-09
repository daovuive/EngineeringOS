# .github/workflows

[GitHub automation](../README.md) · [Structure Governance](../../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

GitHub Actions definitions for repository governance and deterministic tests.

`ci.yml` runs `python3 eng.py validate`, compiles `engineering_os` and `tests`,
discovers every `test_*.py` test through `unittest`, and runs
`git diff --check`. A local pass is evidence for the implementation but does
not imply that the remote GitHub workflow has run.

## Extension Rules

Do not add credentials, private knowledge, model downloads, or live Ollama and
Cloudflare dependencies to the default CI path.
