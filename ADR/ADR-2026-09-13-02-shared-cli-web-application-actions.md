# ADR: Share Explicit Application Actions Between CLI and Web Adapters

- **Date:** 2026-09-13
- **Status:** Proposed
- **Scope:** Application-service boundaries and web command coverage

## Context

EngineeringOS CLI capabilities expanded beyond the original web query screen.
Web equivalents were required without duplicating business logic, passing
arbitrary server paths, or exposing a remote shell. Some operations mutate
repository/runtime state or may run for several minutes.

## Alternatives considered

### Execute CLI subprocesses or arbitrary shell strings from HTTP

Rejected because it creates command-injection, quoting, filesystem, and
privilege risks and makes HTTP behavior depend on presentation output.

### Duplicate each command's logic in web handlers

Rejected because validation and behavior would drift between adapters.

### Introduce a general plugin framework

Rejected because the command surface is small and stable; a second command
registry/framework would add accidental complexity.

### Add Redis/Celery or a persistent server job queue now

Deferred. Current single-user operations work through the existing synchronous
runtime semaphore. The browser records the last result and marks an interrupted
request completion-unknown without replay. Add a persistent bounded job service
only after measured request/proxy failures justify it.

## Proposed decision

1. CLI and web adapters call shared application services for structure,
   configuration, runtime, ingestion, indexing, retrieval, RAG, and workflows.
2. Web-only command metadata uses one small allowlisted action catalog with
   stable IDs, descriptions, fields, duration, and mutation flags.
3. HTTP accepts typed values for known actions only and never builds a shell
   command.
4. Project root and configuration-path overrides remain process-owned and are
   not HTTP inputs.
5. Browser uploads send file bytes/text from the user's device, not a server
   path. Document reads stay inside governed knowledge; retries require an
   inbox document, while organization starts from the inbox and targets only
   configured governed destinations.
6. Mutation endpoints require same-origin requests; consequential actions
   require explicit confirmation.
7. Existing loopback binding, deployment access protection, request limits,
   runtime concurrency limits, sanitized failures, and plain-text model output
   remain in force.

## Consequences

### Positive

- CLI and web behavior reuse the same validation/persistence boundaries.
- The supported CLI surface has usable web equivalents without a shell API.
- Security-sensitive startup and host diagnostics remain outside request input.
- Future actions can be added explicitly without a plugin framework.

### Trade-offs

- The five workspaces expose bounded fields rather than every possible internal
  option; the action catalog remains the canonical executable allowlist.
- Long-running operations are synchronous and may remain completion-unknown
  after browser interruption.
- `scripts/eos-status --deep` remains an operator/host command; exposing
  systemd and ports would widen the web security boundary.

## Validation evidence

- Action and web tests cover catalog uniqueness, typed validation, confirmation,
  same-origin mutations, upload/retry/open, safe errors, and static controls.
- The command coverage matrix records every supported command and the explicit
  process-specific exception.
- A live temporary web process ingested and retrieved synthetic CLI/web content
  without an index-cache restart.

## Approval

This ADR documents implemented behavior but remains **Proposed** until the
project owner explicitly accepts it. Persistent job execution would require a
new or superseding decision once evidence defines its recovery contract.
