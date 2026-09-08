# skills

[Parent directory](../README.md) · [Structure Governance](../docs/STRUCTURE_GOVERNANCE.md)

## Purpose and Scope

Primary source for reusable AI workflows. Each skills/<skill-id>/SKILL.md has a stable kebab-case ID and an entry in configs/skills.json. Agents coordinate, skills describe the method, and knowledge/career provide data. Create references/templates/scripts only when needed.

## Subdirectories

- [analyze-job-description](analyze-job-description/README.md): Job-description analysis package.
- [career-direction-review](career-direction-review/README.md): Career-direction review package.

## Extension Rules

Each SKILL.md must state inputs, outputs, workflow, dependencies, and quality checks.
IDs must be stable and use kebab-case. Supporting references, templates, or scripts
belong to a package only when needed for its workflow; do not copy career/knowledge sources.

Add files within the scope above and link them from this index. New subdirectories must be registered in the manifest, contain their own README.md, and be linked from the parent README. Follow the process and checks in the Structure Governance document.
