# ADR: Use Local Hybrid RAG with Persisted BM25 and Bounded Reranking

- **Date:** 2026-09-13
- **Status:** Accepted
- **Scope:** Knowledge parsing, index representation, retrieval, reranking, and confidence

## Context

EngineeringOS previously used one Markdown heading per chunk and cosine-only
retrieval. That preserved simple grounded answers but underperformed on exact
technical identifiers, large sections, filenames, configuration keys, and
future metadata filtering. PDF was rejected and logs had no controlled path.

The existing Ollama roles, atomic JSON writer, citations, confidence abstention,
and post-generation claim verifier are working boundaries that must remain.
The current local corpus does not justify a remote search service or large ML
reranker dependency.

## Alternatives considered

### Keep dense-only cosine retrieval

Rejected because semantic similarity alone is unreliable for exact IDs and
configuration symbols, and it leaves metadata filtering and true reranking
outside the retrieval pipeline.

### Add a vector database or external search server

Deferred. It adds operations, migration, and another persistence boundary
without evidence that the current corpus exceeds atomic JSON performance.

### Add a local cross-encoder

Deferred. It may improve ranking but adds a large model/dependency and latency.
The reranker interface permits this later if measured evaluation justifies it.

### Rebuild lexical state on every query

Rejected because unchanged BM25 corpus statistics are deterministic index state
and need not be recomputed for each request.

## Decision

1. Use deterministic approximate-token chunks with overlap, heading hierarchy,
   stable IDs, and optional rich metadata.
2. Store embeddings, chunk metadata, and BM25 corpus statistics together in
   schema `2.0`, preserving schema `1.1` reads and atomic replacement.
3. Generate dense and BM25 candidate rankings, fuse them with configurable
   weighted Reciprocal Rank Fusion, then apply optional metadata filters.
4. Rerank only a bounded shortlist through a replaceable interface. Use the
   deterministic local implementation by default and allow it to be disabled.
5. Apply the existing confidence threshold to final evidence quality after
   reranking; retain a separate dense candidate threshold.
6. Preserve Markdown citations and add PDF page citations. Keep claim grounding
   after generation as a distinct safety stage.
7. Parse text PDFs locally with `pypdf`; do not perform OCR by default.
8. Index logs only on explicit rebuild, only from configured project-relative
   allowlists, and only after size, age, binary, symlink, and secret checks.

## Consequences

### Positive

- Exact identifiers and semantic concepts can both retrieve useful evidence.
- Ranking stages and abstention decisions are observable in opt-in debug mode.
- PDF evidence remains traceable to pages; changing logs are never parsed on a
  query request.
- Existing Ollama, citations, atomic persistence, and grounding remain intact.

### Trade-offs

- The JSON index is larger because it stores dense vectors and BM25 statistics.
- Deterministic reranking is lexical/score based and is not a cross-encoder.
- PDF extraction supports embedded text, not OCR or layout reconstruction.
- Allowlisted logs may still contain novel secret forms not matched by the
  conservative detector and therefore require operator review.

## Validation evidence

- Unit tests cover token bounds/overlap/IDs, schema compatibility, BM25 exact
  identifiers, RRF/filter determinism, reranker ordering/disable mode,
  confidence pass/abstain, generated text PDFs/page citations, and every log
  safety rule.
- CLI/action/web tests cover the shared retrieval path, optional diagnostics,
  metadata filters, PDF upload, and backward-compatible defaults.
- Final full-suite, compilation, governance, and diff evidence is recorded in
  `prompts/Resume_EngineeringOS_Development.md`.

## Approval

Accepted explicitly by the project owner on 2026-09-13 after implementation and
validation. A vector store, cross-encoder, OCR pipeline, or broader log policy
requires a new or superseding decision when evidence justifies it.
