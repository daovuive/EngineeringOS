# ADR: Keep the Root README as a Stable Architecture Contract

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** Repository governance and architecture documentation

## Context

The root `README.md` is the stable entrypoint and architectural constitution of EngineeringOS.

Machine-specific details such as model storage paths, provider installation locations, hostnames, ports, disks, or WSL-specific values can change frequently. Embedding those details in the root README would force architectural documentation to change whenever infrastructure changes.

EngineeringOS is intended to remain portable across model providers, machines, disks, and runtime environments.

## Decision

The root `README.md` SHALL describe stable architectural responsibilities and boundaries only.

It SHALL NOT contain machine-specific physical model paths or other host-specific runtime details.

Routine changes such as moving a model, changing a disk, changing a provider endpoint, replacing a model, or changing a local runtime installation SHALL be handled through the appropriate configuration boundary and SHALL NOT require modification of the root README.

The protected root README baseline remains governed by explicit owner approval.

## Rationale

This keeps architecture separate from infrastructure and supports the EngineeringOS principles of:

- Configuration as Data.
- Stable architecture, replaceable infrastructure.
- One primary source per concept.
- Human control over architectural change.

## Consequences

### Positive

- The root README changes rarely.
- Machine migrations do not cause architecture-document churn.
- Local AI providers can change without redesigning the repository.
- Governance remains explicit and reviewable.

### Trade-offs

- Child READMEs and configuration files must clearly document variable runtime behavior.
- Contributors must know where machine-specific values belong.

## Implementation

1. Keep architectural principles and high-level ownership boundaries in the root `README.md`.
2. Put detailed AI configuration rules under the approved AI configuration area.
3. Put host-specific values in local/environment-specific configuration.
4. Do not place physical model paths in the root README.
5. Require explicit project-owner approval before changing the root README or rebasing its protected SHA-256 baseline.

## Validation

For any root-level documentation change:

```bash
python eng.py validate
```

Expected behavior:

- Unauthorized root README changes fail governance validation.
- Approved root README changes require an explicitly authorized baseline update.
- Infrastructure-only changes do not require a root README update.

## Change Rule

Change this decision only if the project intentionally changes the role of the root README itself.
