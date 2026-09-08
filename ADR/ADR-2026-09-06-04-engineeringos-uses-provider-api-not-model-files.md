# ADR: Access Local Models Through Provider APIs, Not Provider Model Files

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** Runtime/provider integration

## Context

Ollama manages its own model files and exposes an inference API.

Allowing EngineeringOS to read Ollama's internal model directory directly would couple the project to:

- Ollama's storage layout,
- a particular operating system,
- a particular disk,
- provider implementation details.

## Decision

EngineeringOS SHALL interact with Ollama through its provider/API abstraction.

EngineeringOS SHALL NOT directly read, mount, index, or otherwise depend on Ollama's physical model store.

EngineeringOS needs to know only provider-level information such as:

```text
provider
endpoint
provider model identifier
```

It SHALL NOT need to know:

```text
D:\AI\Ollama\models
```

or any equivalent provider-owned model path.

## Target Flow

```text
EngineeringOS configuration
        |
        v
logical model
        |
        v
provider abstraction
        |
        v
Ollama API
        |
        v
Ollama-managed model storage
```

## Rationale

This creates a clean replaceable-provider boundary.

It allows:

- Ollama to move between hosts,
- model storage to move between disks,
- a provider to change its internal storage layout,
- Ollama to be replaced by another provider,

without redesigning EngineeringOS knowledge or application architecture.

## Consequences

### Positive

- Strong separation of concerns.
- Better provider portability.
- No dependency on provider-internal file structures.
- Easier testing of provider integration.

### Trade-offs

- EngineeringOS depends on provider availability and API compatibility.
- Network/provider failures become explicit runtime failure modes.

## Implementation

1. Resolve the logical model through `configs/ai/`.
2. Resolve the configured provider.
3. Call the provider endpoint through the EngineeringOS runtime abstraction.
4. Treat provider storage as opaque.
5. Do not hard-code provider model paths in application code.
6. Add smoke/integration tests at the provider boundary.

## Validation

A valid smoke test should verify:

```text
config resolution
    -> provider resolution
    -> provider endpoint reachable
    -> configured model exists
    -> inference succeeds
```

The same test should confirm that no physical Ollama model path is required by EngineeringOS.
