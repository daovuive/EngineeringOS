# ADR: Establish `configs/ai/` as the EngineeringOS AI Configuration Boundary

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** AI configuration architecture

## Context

EngineeringOS needs to select models and providers without coupling application logic or architecture documentation to a specific machine, disk, runtime, or provider.

A clear AI configuration boundary is needed so future changes remain localized.

## Decision

AI-specific configuration SHALL be organized under:

```text
configs/ai/
```

This area owns logical AI configuration such as:

```text
configs/ai/
├── README.md
├── models.json
├── providers.json
└── runtime.json
```

Exact filenames and schemas remain governed by the local README and project configuration rules.

Machine-specific values MAY be supplied through a local environment file or environment variables when required, but they SHALL NOT become stable architecture documentation.

## Responsibility Split

### `models.json`

Defines logical model roles and provider model identifiers.

Examples:

```text
primary_llm
embedding_model
ranking_model
coding_model
```

### `providers.json`

Defines provider identities, types, endpoints, and provider capabilities.

### `runtime.json`

Defines EngineeringOS-owned AI runtime behavior and bindings.

### Local/environment configuration

Defines machine-specific values when required.

## Decision Rule

Logical model identity SHALL be separate from physical model storage.

For example:

```text
primary_llm
    -> provider: ollama-local
    -> model: <provider-model-id>
```

The configuration SHALL NOT require EngineeringOS to know the provider's physical model directory.

## Rationale

This supports:

- replaceable providers,
- replaceable models,
- portable storage,
- configuration-driven behavior,
- minimal application-code changes.

## Consequences

### Positive

- Provider and model changes are localized.
- Application code depends on contracts rather than disk paths.
- Machine-specific details can remain local.
- Future providers can be added without changing the knowledge architecture.

### Trade-offs

- Schemas and ownership rules for `configs/ai/` must remain clear.
- Duplicate configuration mechanisms must be avoided.

## Implementation

1. Maintain a local README for the AI configuration area.
2. Store logical model bindings in the model configuration.
3. Store provider definitions in the provider configuration.
4. Store EngineeringOS AI runtime behavior in runtime configuration.
5. Keep host-specific values outside stable architectural documents.
6. Ensure application code resolves provider/model information through this configuration boundary.

## Validation

Verify that changing:

- the primary LLM,
- the Ollama endpoint,
- a provider model identifier,

does not require changes to unrelated knowledge or architecture files.

Run the checks required by `AGENTS.md` for the affected scope.
