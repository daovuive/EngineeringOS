# tests

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Tests for CLI behavior and EngineeringOS modules. Test by module or observable capability; temporary data belongs in tmp/. Do not call real models or services when checking document structure.

## Existing Documents and Files

- [test_cli.py](test_cli.py).
- [test_llm.py](test_llm.py).
- [test_rag.py](test_rag.py).
- [test_structure.py](test_structure.py).
- [test_structure_governance.py](test_structure_governance.py).

## Extension Rules

Add files within the scope above and link them from this index. New subdirectories must be registered in the manifest, contain their own README.md, and be linked from the parent README. Follow the process and checks in the Structure Governance document.
