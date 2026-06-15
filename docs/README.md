# Documentation & Workshop Guide

This folder contains everything an instructor needs to run the **Order Management
modernization workshop** with GitHub Copilot.

## Read in this order

1. **[01-architecture.md](01-architecture.md)** — the system, the data model, and the full
   catalogue of *planted problems* per tier.
2. **[02-prerequisites.md](02-prerequisites.md)** — tools to install before the session.
3. **[03-running-natively.md](03-running-natively.md)** — start all four apps natively and
   prove they work.
4. **[proctor-guide.md](proctor-guide.md)** — the instructor run sheet: timings, talking
   points, demo flow, and troubleshooting.

## The modernization labs (`modernization/`)

| # | Lab | Copilot capability showcased |
|---|-----|------------------------------|
| 00 | [Overview](modernization/00-overview.md) | The whole journey + how Copilot features map to each lab |
| 01 | [.NET version upgrade (8 → 9)](modernization/01-dotnet-upgrade.md) | GitHub Copilot app modernization – Upgrade |
| 02 | [Data‑model changes](modernization/02-data-model-changes.md) | Agent mode, multi-file edits |
| 03 | [UI changes](modernization/03-ui-changes.md) | WPF async/MVVM + React hardening |
| 04 | [Performance with dotnet-trace](modernization/04-performance-dotnet-trace.md) | Profiling + Copilot-guided fixes |
| 05 | [Agentic **local** delegation](modernization/05-agentic-local-delegation.md) | Copilot agent mode in the IDE |
| 06 | [Agentic **cloud** delegation](modernization/06-agentic-cloud-delegation.md) | Copilot coding agent on GitHub |
| 07 | [Skills & instructions](modernization/07-skills-and-instructions.md) | `.github` custom instructions, prompt files, skillsets |
| 08 | [Docker containerization](modernization/08-docker-containerization.md) | Containerize every tier |

## Copy‑paste prompts (`prompts/`)

- [Python API prompts](prompts/python-api-prompts.md)
- [.NET BFF prompts](prompts/dotnet-bff-prompts.md)
- [WPF desktop prompts](prompts/desktop-wpf-prompts.md)
- [React UI prompts](prompts/react-web-prompts.md)

> Teaching philosophy: **first modernize and improve** (labs 01–07), **then containerize**
> (lab 08). Each lab is self-contained and ends with a verification step.
