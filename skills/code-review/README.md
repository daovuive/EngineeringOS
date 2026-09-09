# skills/code-review

[Skills](../README.md) · [Structure Governance](../../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Canonical workflow contract for reviewing explicitly supplied source text or a
diff. Executable orchestration lives in `engineering_os.workflows`.

## Extension Rules

Keep reviewed source outside this package. Changes to the executable contract
must remain synchronized with the registry, CLI/web entry points, and tests.
