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
`knowledge.chunking` defines approximate token bounds and overlap.
`knowledge.retrieval` defines dense/BM25 enablement, candidate eligibility,
RRF weights, and final confidence; `knowledge.rerank` bounds and weights the
replaceable local reranker. `knowledge.pdf` keeps OCR explicitly disabled, and
`knowledge.logs` owns the disabled-by-default allowlist, size, and retention
policy. These remain separate from provider/model configuration under
`configs/ai/`. The
`knowledge.grounding` values define the conservative lexical claim-support
contract applied after generation; unsupported and partial claims are not
returned as EngineeringOS facts.

User behavior and recovery are documented in the canonical
[Knowledge Ingestion and Hybrid RAG Guide](../docs/KNOWLEDGE_INGESTION.md). Machine-specific
provider endpoints and model assignments remain under `configs/ai/`; do not
place them in ingestion policy.

`configs/ai/runtime.json` owns generation sampling and output bounds. The
current 512-token ceiling is a measured production latency safeguard; increase
it only with before/after latency and grounding evidence. The `stream` option
controls Ollama transport behavior, not browser-visible streaming: the current
public API returns a verified complete JSON response.

## Extension Rules

Add files within the scope above. This README is a local guide, not a complete
file index; adding a file does not require editing it. New subdirectories must
be registered in the manifest, contain their own README.md. Folder and file navigation is discovered
through the manifest; no parent README needs a new link for routine additions. Follow the process and checks in the Structure Governance document.
