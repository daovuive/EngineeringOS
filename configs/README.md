# configs

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Configuration as data: the structure manifest, schemas, runtime settings, template registry, and skill registry. The manifest records managed directories; this README explains their meaning. Changes must stay consistent with the schema and related indexes.

## Subdirectories

- [ai](ai/README.md): Canonical AI provider, logical model, and runtime configuration.

## Existing Documents and Files

- [project-structure.json](project-structure.json).
- [project-structure.schema.json](project-structure.schema.json).
- [settings.json](settings.json).
- [skills.json](skills.json).
- [templates.json](templates.json).

`settings.json` owns knowledge indexing/retrieval policy. The
`knowledge.retrieval` values define candidate filtering, the evidence
confidence gate, and the existing over-fetch factor; they are kept separate
from provider/model configuration under `configs/ai/`. The
`knowledge.grounding` values define the conservative lexical claim-support
contract applied after generation; unsupported and partial claims are not
returned as EngineeringOS facts.

## Extension Rules

Add files within the scope above and link them from this index. New subdirectories must be registered in the manifest, contain their own README.md, and be linked from the parent README. Follow the process and checks in the Structure Governance document.
