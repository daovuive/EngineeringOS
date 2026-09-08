# ADR: Keep EngineeringOS in WSL ext4 on the `C:` NVMe Drive

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** Development filesystem placement

## Context

EngineeringOS is developed and executed primarily through WSL/Linux tooling.

The machine provides:

- a fast `C:` NVMe drive hosting Windows and the WSL virtual disk,
- WSL ext4 storage with a practical capacity limit,
- a larger `D:` SATA SSD intended for high-capacity storage.

Linux development workloads perform best when source code, Python environments, Git operations, and active Linux runtime state remain inside the WSL ext4 filesystem rather than under `/mnt/c` or `/mnt/d`.

## Decision

EngineeringOS source and Linux-oriented project runtime SHALL remain in WSL ext4 on the `C:` NVMe drive.

The repository SHALL not be moved to the `D:` Windows filesystem merely to gain model-storage capacity.

Large provider-owned AI model binaries SHALL use separate external storage instead.

## Target Layout

```text
C: NVMe
└── WSL ext4
    └── ~/projects/EngineeringOS
        ├── source
        ├── configs
        ├── tests
        ├── knowledge
        └── project-owned runtime state
```

## Rationale

This keeps latency-sensitive Linux development activity on the faster native WSL filesystem while preserving the larger secondary disk for capacity-oriented model storage.

## Consequences

### Positive

- Better Git and Linux filesystem behavior.
- Fast project indexing and development workflows.
- Cleaner separation between project state and large AI assets.

### Trade-offs

- WSL ext4 capacity remains finite.
- Large generated datasets or caches may need explicit storage policies later.

## Implementation

1. Keep the repository under the Linux filesystem, for example:

```text
~/projects/EngineeringOS
```

2. Keep Python environments and Linux development tooling in WSL/ext4.
3. Keep EngineeringOS-owned indexes and active runtime state in ext4 unless a later ADR decides otherwise.
4. Store large reusable provider model binaries outside the repository.

## Validation

Confirm the repository path resolves inside the WSL Linux filesystem rather than `/mnt/c/...` or `/mnt/d/...`.

Confirm model binaries are not consuming EngineeringOS repository/runtime capacity.
