# 02 — Prerequisites

Install these **before** the workshop. Everything runs on a single Windows machine.

## Required

| Tool | Version | Check | Notes |
|------|---------|-------|-------|
| .NET SDK | **9.x** | `dotnet --version` | Builds & runs the `net8.0` projects and powers the 8→9 upgrade lab. |
| .NET runtimes | **8.x and 9.x** | `dotnet --list-runtimes` | Need `Microsoft.NETCore.App`, `Microsoft.AspNetCore.App`, **and** `Microsoft.WindowsDesktop.App` for both 8 and 9. |
| Python | **3.11+** | `python --version` | For the Flask API. |
| Node.js | **20+** (22/24 fine) | `node --version` | For the React UI / Vite. |
| Git | any recent | `git --version` | |

> WPF is **Windows-only**. The desktop tier will not build/run on macOS or Linux.

## For specific labs

| Lab | Extra tooling |
|-----|---------------|
| 01 — .NET upgrade | **Visual Studio 2022 17.10+** or **VS Code** with the *GitHub Copilot app modernization – Upgrade for .NET* extension, or the CLI **`dotnet tool install -g upgrade-assistant`**. |
| 04 — Performance | **`dotnet-trace`**: `dotnet tool install -g dotnet-trace`. Optional: [Speedscope](https://www.speedscope.app/) or PerfView/Visual Studio to view traces. |
| 05/06 — Agentic | **GitHub Copilot** subscription with **agent mode** enabled in the IDE; for the cloud lab, a GitHub repo with the **Copilot coding agent** available. |
| 08 — Docker | **Docker Desktop** (Linux containers). |

## Verify your machine (copy‑paste)

```powershell
dotnet --version
dotnet --list-runtimes
python --version
node --version ; npm --version
```

You should see .NET **8.x and 9.x** runtimes for `NETCore`, `AspNetCore` **and**
`WindowsDesktop`. If a runtime is missing, install it from
<https://dotnet.microsoft.com/download>.

## GitHub Copilot setup

- Sign in to Copilot in your IDE (VS Code or Visual Studio).
- Enable **Agent mode** (VS Code: the Chat view mode selector → *Agent*).
- This repo ships **custom instructions** in `.github/` that Copilot picks up automatically
  (see lab 07).

Next: **[03-running-natively.md](03-running-natively.md)**.
