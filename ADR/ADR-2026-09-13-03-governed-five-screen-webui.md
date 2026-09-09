# ADR: Extend the Existing WebUI into Five Governed Workspaces

- **Date:** 2026-09-13
- **Status:** Proposed
- **Scope:** Web information architecture, shared application integration, and
  governed browser operations

## Context

EngineeringOS already has a Python CLI, a loopback HTTP adapter, local runtime
abstraction, JSON knowledge index, grounded RAG, engineering workflows, and an
explicit web action catalog. The existing browser page exposes these features
as one long form and does not match the five owner-approved mockups for
Knowledge, Ask EOS, Engineering, Models, and Project.

The owner approved the mockups as the visual specification on 2026-09-13 and
requested a working implementation rather than a static preview. Visual
approval does not itself approve new architecture decisions.

## Decision drivers

- Make the full existing EOS capability set understandable and usable.
- Match the approved navigation, hierarchy, density, and interaction patterns.
- Keep CLI and web behavior on shared application services.
- Preserve local-first security, truthful state, and human confirmation.
- Avoid a second frontend framework, command registry, or deployment service.
- Remain extensible without coupling model/runtime logic to the browser.

## Alternatives considered

### Restyle the existing single-page form

Rejected. It cannot reproduce the five-workspace information architecture or
the mockups' contextual panels without remaining difficult to navigate.

### Introduce a frontend framework and build pipeline

Rejected for this increment. The dependency-free HTML/CSS/JavaScript stack can
provide the required shared shell and components without a second toolchain.

### Build separate business logic for each screen

Rejected. It would drift from CLI validation and violate the shared-service
boundary established by the existing action, ingestion, RAG, and workflow
services.

### Expose CLI or shell execution through HTTP

Rejected. Typed allowlisted application actions provide equivalent behavior
without command injection or arbitrary server-path access.

## Proposed decision

1. Extend the existing dependency-free WebUI into five client-side workspaces:
   Knowledge, Ask EOS, Engineering, Models, and Project, with one shared shell
   and Activity surface.
2. Use reusable CSS/DOM patterns for cards, tabs, controls, badges, drawers,
   dialogs, source references, progress, and result panels.
3. Keep operations in shared Python application services. Add only the bounded
   read/preview/revalidation capabilities missing from those services.
4. Build document and source inspection from governed project-relative paths;
   reject traversal, symlinks, unsupported content, and arbitrary server paths.
5. Bind consequential organization and structure mutations to server-validated
   previews. Revalidate the preview immediately before execution.
6. Keep model text and uploaded/retrieved content as untrusted plain text.
7. Retain synchronous bounded execution at current single-user scale. Browser
   Activity stores only bounded summaries, turns interrupted operations into
   completion-unknown, never replays mutations, and offers a relevant
   reconciliation action.
8. Ship only real application state in the browser bundle. Visual-test data may
   be supplied by external test harnesses, but no URL or runtime mode may
   replace API state with embedded demo results.

## Supported operations

- Governed knowledge listing, filtering, ingestion, retry, inspection,
  organization preview/apply, full-index preview/rebuild, search, and RAG.
- Four bounded engineering workflows with optional knowledge and downloadable
  or copyable plain-text results.
- Provider/model status, role mapping, chat, embedding preview, pull plan, and
  read-only runtime configuration.
- Version, validation, diagnostics, structure/sync previews and confirmed
  execution, and read-only configuration views.

Server lifecycle, configuration-path editing, host-level systemd/port/SSH/
Cloudflare diagnostics, deployment, production restart, and ADR approval remain
explicitly outside the website.

## Consequences

### Positive

- The visual hierarchy maps directly to user tasks instead of command names.
- CLI/web equivalence remains testable at the shared-service boundary.
- New browser reads and mutations remain constrained to governed resources.
- The current runtime and JSON index remain unchanged and replaceable.

### Trade-offs and limitations

- The no-build frontend requires disciplined shared DOM/CSS helpers.
- Long model/index operations remain synchronous and have indeterminate rather
  than fabricated percentage progress.
- Browser reload cannot prove whether an interrupted mutation completed; users
  must reconcile current state before retrying.
- Visual fidelity requires browser screenshots in addition to unit/API tests.

## Related decisions

- [Governed ingestion and atomic JSON index updates](ADR-2026-09-13-01-governed-ingestion-and-atomic-json-index-updates.md)
- [Shared explicit CLI/web application actions](ADR-2026-09-13-02-shared-cli-web-application-actions.md)

## Validation and completion criteria

- Deterministic tests cover all five workspaces, shared actions, guarded
  previews, path safety, activity recovery, and existing CLI behavior.
- Governance validation, Python compilation, full unit discovery, and
  whitespace checks pass.
- Five desktop screenshots and at least one narrow viewport are compared with
  the approved references using non-sensitive test state.
- Documentation, command coverage, backlog, implementation log, and resume
  checkpoint match the delivered behavior and disclose unverified live state.

Current evidence on 2026-09-13 includes 46 passing targeted application/web
tests, 110 passing full-suite tests, successful Python compilation and
working-tree whitespace checks, successful Edge headless rendering of
executable JavaScript, five 1536×1024 historical screenshots, and one 500×844
responsive screenshot. The subsequent production-hardening increment removed
the embedded demo-data path; all browser URLs now use the real local API.

## Approval

The five mockups are owner-approved visual direction through the implementation
request dated 2026-09-13. This architecture record remains **Proposed** pending
explicit owner acceptance of the additional WebUI integration and recovery
decisions described above.
