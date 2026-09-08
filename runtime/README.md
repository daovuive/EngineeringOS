# runtime

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Generated EngineeringOS execution state: caches, indexes, sessions, and other
rebuildable local data. Adapter code is in engineering_os/llm.py; AI
configuration is in configs/ai/. Do not store sole-source documents or
provider-owned model binaries here.

The generated directories `cache/`, `index/`, and `vector-db/` are declared
exceptions in the manifest. Provider model storage is outside the EngineeringOS
repository and is not represented by a `runtime/models/` directory.

## Extension Rules

Add files within the scope above and link them from this index. New subdirectories must be registered in the manifest, contain their own README.md, and be linked from the parent README. Follow the process and checks in the Structure Governance document.
