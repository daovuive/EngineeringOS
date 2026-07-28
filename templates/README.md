# Engineering OS

> Personal Engineering Knowledge Platform powered by Local AI.

---

# Vision

Engineering OS is a Personal Engineering Knowledge Platform and AI Operating System.

Its purpose is to preserve engineering knowledge, architecture decisions, reusable engineering assets, and lessons learned throughout an engineering career.

The platform continuously accumulates engineering knowledge to support the long-term growth of a Solution Architect.

---

# Mission

Engineering OS enables engineers to:

- Capture engineering knowledge
- Preserve architecture decisions
- Reuse engineering assets
- Learn from previous projects
- Accelerate engineering work using Local AI

---

# Design Principles

## Knowledge First

Knowledge is the most valuable engineering asset.

Everything should be searchable, reusable and continuously improved.

---

## Architecture First

Architecture decisions are more valuable than implementation details.

Architecture knowledge should outlive frameworks and technologies.

---

## Local AI First

Engineering OS is designed to work primarily with Local AI.

Benefits include:

- Privacy
- Offline capability
- Vendor independence
- Lower operating cost

---

## Human in Control

AI assists engineering work.

Engineers make the final decisions.

---

## Configuration as Data

Project structure, templates and runtime configuration are stored as configuration files.

Automation scripts and AI Agents read configuration instead of hard-coded logic.

---

## Single Source of Truth

Project structure is defined by:

```
configs/project-structure.json
```

Automation scripts and AI Agents should never hard-code repository structure.

---

# Repository Structure

```
EngineeringOS
│
├── ADR
├── agents
├── configs
├── docs
├── experiments
├── knowledge
├── logs
├── memory
├── prompts
├── runtime
├── scripts
├── templates
├── tests
└── tools
```

---

# Initialization

Initialize the repository:

```powershell
./eng.ps1 init
```

Validate the repository:

```powershell
./eng.ps1 validate
```

Synchronize missing resources:

```powershell
./eng.ps1 sync
```

Check local environment:

```powershell
./eng.ps1 doctor
```

---

# Configuration

The repository is configured using:

```
configs/project-structure.json
configs/templates.json
configs/settings.json
configs/ai-runtime.json
```

---

# License

See the LICENSE file for licensing information.