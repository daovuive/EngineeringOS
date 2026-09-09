# engineering_os

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

EngineeringOS Python implementation: CLI, configuration, structure creation/validation, runtime abstraction, and Markdown search. The root eng.py is only an entry point. The runtime API goes through LLMRuntime/create_runtime; learning workflows and model data do not belong in the code module.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
