# ASR-0001: LLM Model Selection for Local Ollama Runtime

## Status

Accepted as the current local model-selection decision.

## Purpose

This note records the model set selected for EngineeringOS when using Ollama as
the first supported local AI runtime. It is a model-selection decision note, not
a benchmark report.

EngineeringOS remains runtime/vendor independent at the architecture boundary:
core code should depend on the generic runtime API, not directly on Ollama HTTP
endpoints.

## Machine Configuration

The source note recorded the following personal machine configuration:

| Component | Recorded value |
| --- | --- |
| CPU | Intel Core i7-9750H, 6 cores / 12 threads |
| RAM | 64 GB |
| Dedicated GPU | NVIDIA Quadro T2000, 4 GB VRAM |
| Integrated GPU | Intel UHD Graphics 630 |

This repository does not currently contain independent machine-inventory
evidence for those values. Treat them as recorded context for the decision, not
as continuously verified project facts.

## Decision

Use a small Ollama model set optimized for local use on constrained GPU memory:

| Role | Model | Pull command |
| --- | --- | --- |
| RAG-oriented generation | `granite3.1-moe:3b` | `ollama pull granite3.1-moe:3b` |
| Chat | `phi3.5:3.8b-mini-instruct-q4_K_M` | `ollama pull phi3.5:3.8b-mini-instruct-q4_K_M` |
| Reasoning | `phi3.5:3.8b-mini-instruct-q4_K_M` | `ollama pull phi3.5:3.8b-mini-instruct-q4_K_M` |
| Coding | `qwen2.5-coder:3b-instruct-q4_K_M` | `ollama pull qwen2.5-coder:3b-instruct-q4_K_M` |
| Embedding | `nomic-embed-text` | `ollama pull nomic-embed-text` |

The matching model and runtime configuration is stored under `configs/ai/`.

## Assumptions

- Small models are preferred over larger 8B-14B models for this hardware class.
- Model memory use depends on Ollama version, quantization, context size,
  runtime residency, and CPU/GPU offloading behavior.
- Performance should be validated on the target machine before treating any
  model as suitable for production-like workflows.
- Embedding support is needed for future RAG, but this decision does not choose
  a vector database, chunking strategy, retrieval pipeline, or agent framework.

## Unverified Performance Claims

The original source text included exact or strong performance statements, such
as token-per-second estimates and claims that selected models run completely on
GPU. Those claims are not retained as project facts because this repository does
not include benchmark evidence for them.

For current EngineeringOS purposes, the defensible claim is narrower: the
selected models are intentionally small local-Ollama candidates expected to be
more practical on a 4 GB VRAM machine than larger model defaults.

## Usage

Check the configured model pull commands:

```bash
python eng.py llm pull-plan
```

Check runtime health:

```bash
python eng.py llm status
python eng.py doctor
```

Run a chat smoke test:

```bash
python eng.py llm chat "What is software architecture?"
```

Run an embedding smoke test:

```bash
python eng.py llm embed "EngineeringOS architecture review"
```
