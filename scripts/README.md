# scripts

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Operational scripts that support EngineeringOS when genuinely needed. Reusable CLI logic belongs in engineering_os/. Add a script only when its inputs, outputs, execution, and checks are clear; do not create a second implementation of the same function.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
