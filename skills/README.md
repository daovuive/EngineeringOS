# AI Skills

Skills are reusable AI capability workflows. They are intentionally separate
from agents:

- An agent owns orchestration and role-specific behavior.
- A skill owns one reusable capability.
- A prompt owns reusable wording or prompt fragments.
- A tool owns an integration or executable operation.

## Skill Package Contract

Each skill must have one canonical `SKILL.md` file. Optional supporting content
belongs inside the same skill folder:

```text
skills/<skill-id>/
├── SKILL.md
├── references/
├── templates/
└── scripts/
```

Use these rules to keep the library extensible and avoid duplication:

1. Give every skill a stable kebab-case `id`.
2. Keep workflow instructions in `SKILL.md`; do not copy them into agents.
3. Reference knowledge, memory and prompts by path or ID instead of copying content.
4. Keep domain-specific supporting files inside the skill package.
5. Record each skill once in `configs/skills.json`.
6. Make inputs, outputs, dependencies and quality checks explicit.
