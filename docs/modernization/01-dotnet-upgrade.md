# Lab 01 — .NET version upgrade (8 → 9)

**Goal:** upgrade the two .NET projects (WPF desktop + ASP.NET Core BFF) from `net8.0` to
`net9.0` using **GitHub Copilot app modernization for .NET**, and verify they still build
and run.

**Copilot capability:** GitHub Copilot app modernization – *Upgrade for .NET*
(<https://learn.microsoft.com/dotnet/core/porting/github-copilot-app-modernization/>).

**Time:** ~30 min · **Branch:** `git switch -c lab/01-dotnet-upgrade`

---

## Background

The upgrade tooling can analyze a solution, propose a plan, edit project files and code,
and **build to verify** — fixing what it broke in a loop. It is available as:
- The **GitHub Copilot app modernization – Upgrade** extension for **Visual Studio 2022**
  and **VS Code**, and
- the **.NET Upgrade Assistant** CLI (`upgrade-assistant`) which integrates with Copilot.

We have:
- `src/desktop/OrderManagement.Desktop/OrderManagement.Desktop.csproj` → `net8.0-windows`
- `src/web/OrderManagement.Web/OrderManagement.Web.csproj` → `net8.0`

## Step 1 — Baseline

```powershell
dotnet build OrderManagement.sln
```
Confirm a clean build on `net8.0`. Commit so you have a known-good starting point.

## Step 2 — Kick off the upgrade

### Option A — Visual Studio / VS Code (recommended for the demo)
1. Install the **GitHub Copilot app modernization – Upgrade for .NET** extension.
2. Right-click the **solution** (VS) or open the **Copilot Chat → Agent** view (VS Code)
   and choose **Upgrade** / `@upgrade`.
3. Select target **.NET 9**. Let it produce an **upgrade plan** (it lists each project and
   the changes it will make).
4. Review the plan, then **Apply**. Watch it edit the `TargetFramework`, bump package
   versions, and adjust any APIs.

### Option B — CLI
```powershell
dotnet tool install -g upgrade-assistant
upgrade-assistant upgrade OrderManagement.sln
```
Follow the interactive steps; choose **.NET 9** as the target.

### Option C — Copilot Agent prompt (no extension)
In **Agent mode**, paste the prompt from
[`docs/prompts/dotnet-bff-prompts.md`](../prompts/dotnet-bff-prompts.md#lab-01--upgrade-to-net-9)
(and the WPF equivalent). Copilot edits both `.csproj` files and rebuilds.

## Step 3 — What should change

- `net8.0` → `net9.0` (and `net8.0-windows` → `net9.0-windows`).
- `Microsoft.AspNetCore.OpenApi` `8.0.x` → `9.0.x`.
- `CommunityToolkit.Mvvm` stays compatible (already `8.3.2`); no change required.
- Any obsolete API usage flagged and fixed (this sample is small, so expect few).

Example diff (BFF):
```xml
<!-- before -->
<TargetFramework>net8.0</TargetFramework>
<PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.28" />
<!-- after -->
<TargetFramework>net9.0</TargetFramework>
<PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="9.0.0" />
```

## Step 4 — Verify

```powershell
dotnet build OrderManagement.sln
# run the apps
dotnet run --project src/web/OrderManagement.Web      # then hit /swagger
dotnet run --project src/desktop/OrderManagement.Desktop
pwsh tools/smoke-test.ps1   # with the Python API + BFF running
```

All green and both apps run → upgrade complete. Commit:
```powershell
git commit -am "lab 01: upgrade WPF + BFF to net9.0"
```

## Talking points
- The value isn't the one-line TFM change — it's the **build → fix → rebuild loop** the
  tooling runs *for you*, and the **plan** you can review before anything changes.
- Point out that the `net8.0` runtime is still installed, so you can compare side by side.
- Note: the React + Python tiers are unaffected by a .NET upgrade — modernization is
  per-tier.

## If you want to stay on .NET 8
Skip this lab; everything else works on `net8.0`. The later labs do not depend on 9.
