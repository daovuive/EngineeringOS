# engineering_os

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

EngineeringOS Python implementation: CLI, configuration, structure creation/validation, runtime abstraction, and Markdown search. The root eng.py is only an entry point. The runtime API goes through LLMRuntime/create_runtime; learning workflows and model data do not belong in the code module.

## Existing Documents and Files

- [__init__.py](__init__.py).
- [cli.py](cli.py).
- [config.py](config.py).
- [doctor.py](doctor.py).
- [knowledge.py](knowledge.py).
- [rag.py](rag.py).
- [llm.py](llm.py).
- [structure.py](structure.py).
- [templates.py](templates.py).

## Extension Rules

Add files within the scope above and link them from this index. New subdirectories must be registered in the manifest, contain their own README.md, and be linked from the parent README. Follow the process and checks in the Structure Governance document.
