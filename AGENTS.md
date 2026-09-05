# EngineeringOS AI entrypoint

Before creating, moving, deleting or editing project files:

1. Read [root README](README.md), then [structure governance](docs/STRUCTURE_GOVERNANCE.md).
2. Read [manifest](configs/project-structure.json) and the README.md chain from the
   intended top-level directory down to the destination. Follow the nearest
   README's placement rules; surface conflicts before changing architecture.
3. For reusable workflows, consult [skills](skills/README.md) and
   [skill registry](configs/skills.json). Read the matching SKILL.md rather than
   inventing or duplicating a workflow. Architect learning currently uses the
   [learning entrypoint](knowledge/architect/README.md); a new teaching skill is
   still a separate proposal.
4. Apply only the authorized task. Link new content from its containing README;
   register new maintained directories with a README and parent link.
5. Run `python eng.py validate` and checks appropriate to the change. Report
   remaining violations rather than changing the policy to make validation pass.

Root README.md is protected. Do not edit, replace, rename or delete it, or rebase
its SHA-256 baseline, without the user's explicit approval of the proposed root
change. Broad requests to clean up, synchronize or extend the project do not
grant that approval. Prepare a concrete proposal under docs/proposals/ first.

The root navigation migration was approved by the user and applied on 2026-09-05.
README.md is the active charter; archived proposals are not alternate policies.
Do not disable governance checks or widen exclusions as a workaround.
Keep one canonical workflow per skill and one source per piece
of knowledge. These instructions route to project documents; they do not replace
them or promise that every AI tool automatically reads this file.
