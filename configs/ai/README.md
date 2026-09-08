# configs/ai

[Parent directory](../README.md) · [Structure Governance](../../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Canonical configuration boundary for EngineeringOS AI providers, logical model
roles, and runtime behavior.

This directory defines how EngineeringOS reaches a provider and which logical
role uses which provider model identifier. It must not contain provider-owned
model binaries or physical model-storage paths.

## Existing Documents and Files

- [models.json](models.json): Logical roles and their provider model identifiers.
- [providers.json](providers.json): Provider types, endpoints, and connection settings.
- [runtime.json](runtime.json): Default provider and provider-neutral runtime options.

The default provider is Ollama exposed by the Windows installation at
`http://localhost:11434`. If WSL cannot reach that forwarded endpoint, set
`ENGINEERINGOS_OLLAMA_ENDPOINT` to the reachable Ollama API endpoint. The
provider's model directory remains outside EngineeringOS and is not configured
in this repository.

Ollama must be running on Windows and its API must be reachable from WSL. If
required, configure the Windows-side `OLLAMA_HOST` environment setting outside
this repository. EngineeringOS communicates with Ollama through HTTP only.

## Ownership Rules

- EngineeringOS owns logical roles, provider bindings, endpoint configuration,
  and runtime behavior.
- Ollama owns model installation, model lifecycle, and physical model storage.
- Machine-specific endpoint overrides belong in the environment, not in stable
  architecture documentation.

## Extension Rules

Add provider-neutral configuration here and keep one canonical source for each
responsibility. Add a provider adapter in `engineering_os/llm.py` only when the
provider implements the generic runtime contract. Do not add model binaries or
physical Windows/Linux storage paths.
