# configs

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Configuration as data: the structure manifest, schemas, runtime settings, template registry, and skill registry. The manifest records managed directories; this README explains their meaning. Changes must stay consistent with the schema and related indexes.

## Configuration Notes

`settings.json` owns knowledge indexing/retrieval policy. The
`knowledge.autoIndex` value controls the ingestion default;
`knowledge.ingestion` owns the fixed inbox and maximum input size; and
`knowledge.organizer.destinations` is the only destination allowlist available
to model-assisted organization. The
`knowledge.retrieval` values define candidate filtering, the evidence
confidence gate, and the existing over-fetch factor; they are kept separate
from provider/model configuration under `configs/ai/`. The
`knowledge.grounding` values define the conservative lexical claim-support
contract applied after generation; unsupported and partial claims are not
returned as EngineeringOS facts.

User behavior and recovery are documented in the canonical
[Knowledge Ingestion Guide](../docs/KNOWLEDGE_INGESTION.md). Machine-specific
provider endpoints and model assignments remain under `configs/ai/`; do not
place them in ingestion policy.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
