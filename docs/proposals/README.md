# docs/proposals

[Parent directory](../README.md) · [Structure Governance](../../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Proposals awaiting project-owner approval, with impact and patches when needed. Content in this area does not replace rules currently in force. After approval, apply the change to the primary source and record the approval decision.

## Existing Documents and Files

- [Approval preview](ROOT_README.proposed.md): proposed root README content; preview links are adjusted relative to this directory.
- [Exact root README diff](root-readme.patch): replaces the long introduction and exercises with the constitution, responsibility model, and link tree. Patch paths are relative to the repository root.

## Approval Decision and Application Status

The project owner approved the change on 2026-09-05 with the request: “good, implement the change.”
Status: **Approved / Applied**. The patch was applied to the root README, the protected hash was updated, and `rootNavigationPendingApproval` was set to `false`. The preview and patch are retained as history; do not apply this patch again.

The approved version preserves the Local AI and Solution Architect goals, moves changing details into docs/, identifies skills/agents and extension rules, and records the former exercises in [Architecture Context](../ARCHITECTURE_CONTEXT.md) as historical context.

The root README is authoritative; the preview is not the source for future updates. Do not apply a proposal merely because it exists in the repository. The README organization work did not change skill workflows or the learning roadmap; those remain in a separate earlier proposal.

## Extension Rules

Add files within the scope above and link them from this index. New subdirectories must be registered in the manifest, contain their own README.md, and be linked from the parent README. Follow the process and checks in the Structure Governance document.
