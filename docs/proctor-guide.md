# Proctor / Instructor Guide

This is the run sheet for delivering the **Order Management modernization workshop**. It
assumes a single Windows machine per attendee (or a shared demo machine driven by the
instructor).

## Learning outcomes

By the end, attendees can use GitHub Copilot to:
1. Upgrade a .NET app to a newer target framework.
2. Make a cross-cutting **data-model** change safely.
3. Fix **UI** problems (WPF async/MVVM, React hardening).
4. **Profile** with `dotnet-trace` and fix the hot path.
5. Delegate work to Copilot **locally** (agent mode) and in the **cloud** (coding agent).
6. Steer Copilot with **custom instructions / skills**.
7. **Containerize** every tier with Docker.

## Suggested timing (half day, ~4h)

| Time | Segment |
|------|---------|
| 0:00–0:20 | Intro + architecture walkthrough (`docs/01-architecture.md`) |
| 0:20–0:45 | Everyone runs all four tiers natively (`docs/03-running-natively.md`) |
| 0:45–1:15 | Lab 01 — .NET 8 → 9 upgrade |
| 1:15–1:45 | Lab 02 — data-model change (`double`→`decimal`, constraints) |
| 1:45–2:00 | Break |
| 2:00–2:30 | Lab 03 — UI changes (WPF async + React) |
| 2:30–3:10 | Lab 04 — `dotnet-trace` performance |
| 3:10–3:30 | Lab 05 — agentic **local** delegation |
| 3:30–3:50 | Lab 06 — agentic **cloud** delegation + Lab 07 (instructions/skills) |
| 3:50–4:20 | Lab 08 — Docker (optional / overflow) |
| 4:20–4:30 | Wrap-up, Q&A |

> Short on time? Run labs 01, 04 and 06 — they give the strongest "wow" per minute.

## Before the session (instructor checklist)

- [ ] Walk `docs/02-prerequisites.md`; confirm `.NET 8 + 9` runtimes and the
      `dotnet-trace` global tool are installed.
- [ ] Clone the repo and run `pwsh tools/run-all.ps1 -WithWeb` once; confirm
      `pwsh tools/smoke-test.ps1` is all green.
- [ ] Build the solution once (`dotnet build OrderManagement.sln`) so NuGet is warm.
- [ ] `npm install` in `ClientApp` once so the first lab isn't waiting on downloads.
- [ ] Sign in to Copilot; enable **Agent mode**; confirm the repo's `.github` instructions
      are detected.
- [ ] For Lab 06, have a GitHub repo where the **Copilot coding agent** is enabled.

## Demo flow & talking points

### Set the scene (the "before")
Open the React UI and the WPF app side by side. Click **Load Dashboard** (web) and **Load
Revenue Report** (desktop) — both stall. Say: *"This is a real-feeling legacy app. It
works, but it's slow, insecure and hard to change. We'll let Copilot do the heavy lifting."*

Then run, in a terminal, a search for the planted issues:
```powershell
# Show how many planted problems exist
Select-String -Path (Get-ChildItem -Recurse -Include *.py,*.cs,*.tsx) -Pattern "BAD:" | Measure-Object
```

### Reinforce the pattern each lab
For every lab: **(1)** show the problem, **(2)** give Copilot the prompt from
`docs/prompts/…`, **(3)** review the diff *out loud* (this is the teaching moment — Copilot
is a pair, not an oracle), **(4)** run the verification step, **(5)** commit.

### Key "aha" moments to land
- **Lab 01:** Copilot/the upgrade tooling edits the `.csproj` TFM and fixes APIs, then
  *builds to verify*. Emphasize the build-fix-rebuild loop.
- **Lab 04:** The `dotnet-trace` flame/te shows `ComputeExpensiveChecksum` and
  `Thread.Sleep` dominating. Copilot replaces trial-division with a sieve and removes the
  sleep; re-trace shows the win.
- **Lab 05 vs 06:** Same kind of task, two delegation models — *local* (you watch it edit
  files live) vs *cloud* (it opens a PR you review). Contrast control vs. parallelism.
- **Lab 07:** Toggle the `.github/instructions/*.instructions.md` and show how Copilot's
  suggestions change (e.g. it now insists on `decimal` and `IHttpClientFactory`).

## Common pitfalls (and answers)

| Pitfall | Answer |
|---------|--------|
| "Copilot changed too much." | Use smaller, scoped prompts; accept hunks selectively; keep the app runnable between steps. |
| Upgrade lab can't find .NET 9 | `dotnet --list-sdks`; install the SDK; reload the IDE. |
| `dotnet-trace` shows nothing useful | Make sure you hit `/api/dashboard` *while* tracing; trace the running PID, not a new process. |
| WPF won't run in a VM/over RDP without GPU | WPF needs a desktop session; software rendering usually works, but avoid headless agents. |
| Compose `web` can't reach `api` | Confirm `PythonApi__BaseUrl=http://api:5001` is set (lab 08). |
| Merge conflicts after cloud PR | Pull the PR branch locally; let Copilot resolve, or reset the lab. |

## Reset between cohorts

```powershell
git restore .
git clean -fdx        # removes bin/obj/.venv/node_modules/orders.db/wwwroot build output
```

Re-run the "Before the session" checklist.

## Grading / "done" criteria per lab
Each lab file ends with a **Verify** section. A lab is "done" when its verification passes
*and* the app still runs (`tools/smoke-test.ps1` green, WPF launches, React loads).
