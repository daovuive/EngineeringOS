# ADR: Run Ollama on Windows and Store Ollama Models on the `D:` SSD

- **Date:** 2026-09-06
- **Status:** Accepted
- **Scope:** Local Ollama deployment and physical model storage

## Context

The machine has:

- Windows on a fast `C:` NVMe drive,
- EngineeringOS in WSL ext4 hosted on `C:`,
- a `D:` SATA SSD with approximately 2 TB capacity and substantial free space.

Ollama is already installed and running on Windows.

Local model binaries can consume very large amounts of storage. Keeping them inside WSL/ext4 would reduce space available for EngineeringOS and other Linux workloads.

## Decision

Ollama SHALL continue to run as a Windows-local provider.

Ollama's large model store SHALL be placed on the `D:` SSD rather than inside EngineeringOS or WSL ext4.

Recommended provider-owned storage location:

```text
D:\AI\Ollama\models
```

Ollama SHALL own this path through its own environment/configuration mechanism.

Conceptually:

```text
OLLAMA_MODELS=D:\AI\Ollama\models
```

This physical path SHALL NOT be part of EngineeringOS architecture or model configuration.

## Target Layout

```text
C: NVMe
├── Windows
├── Ollama application/service
└── WSL ext4
    └── EngineeringOS

D: SATA SSD
└── AI
    └── Ollama
        └── models
```

## Rationale

The `D:` drive provides much more capacity.

SATA SSD performance is acceptable for model storage because disk speed primarily affects cold loading; once model data is resident in RAM/VRAM, inference performance is dominated by compute and memory characteristics rather than the model's original disk location.

## Consequences

### Positive

- Preserves WSL/ext4 capacity.
- Makes large model collections practical.
- Keeps provider storage independent from EngineeringOS.
- Future disk migration affects Ollama configuration only.

### Trade-offs

- Cold model loads may be slower than on NVMe.
- The `D:` drive becomes an infrastructure dependency for the current Ollama installation.

## Implementation

1. Keep the Ollama application/service installed on Windows.
2. Create or use:

```text
D:\AI\Ollama\models
```

3. Configure Ollama's model storage using the provider-supported environment setting, for example:

```text
OLLAMA_MODELS=D:\AI\Ollama\models
```

4. Restart Ollama after changing its environment.
5. Verify `ollama list` or `/api/tags` sees the expected models.
6. Keep this path out of EngineeringOS configs and application code.

## Validation

On Windows:

```powershell
curl.exe http://127.0.0.1:11434/api/tags
```

and/or:

```powershell
ollama list
```

EngineeringOS validation should not depend on the physical `D:` model path.

## Future Migration

If models move to another disk, NAS, or host:

1. Update Ollama/provider infrastructure configuration.
2. Restart/revalidate Ollama.
3. Do not change EngineeringOS root architecture.
4. Do not change logical model bindings unless the provider/model identity itself changes.
