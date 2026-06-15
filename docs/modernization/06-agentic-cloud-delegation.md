# Lab 06 — Agentic **cloud** delegation (Copilot coding agent)

**Goal:** delegate a task to the **GitHub Copilot coding agent**, which works **in the
cloud** on its own branch and opens a **pull request** you review — no local machine time.

**Copilot capability:** Copilot coding agent (assign an issue / "delegate" to Copilot on
GitHub).

**Time:** ~20 min (plus async wait) · runs on **GitHub**, not your laptop.

---

## What "cloud delegation" means

You describe a task as a **GitHub Issue** (or from VS Code's "delegate to coding agent") and
assign it to **Copilot**. Copilot spins up a cloud environment, clones the repo, makes the
changes on a branch, runs builds/tests, and opens a **draft PR**. You review, comment
(Copilot iterates on review feedback), and merge. Great for parallelizing well-scoped work.

> Prerequisite: the Copilot coding agent must be enabled for the repository/organization, and
> the repo must be on GitHub.

## Step 1 — Write a crisp issue

A good cloud task is **self-contained, well-scoped, and verifiable**. Example issue:

**Title:** Harden the .NET BFF HTTP layer (async + IHttpClientFactory)

**Body:**
> In `src/web/OrderManagement.Web`, replace the `new HttpClient()`-per-call pattern in
> `Services/PythonApiClient.cs` with a typed client registered via
> `builder.Services.AddHttpClient<PythonApiClient>()`. Make every method `async Task<...>`
> and `await` the calls — remove all `.Result`. Update `Program.cs` minimal-API handlers and
> `ReportService` to be async accordingly. Keep the downstream base URL configurable via
> `PythonApi:BaseUrl`. Set a sensible `HttpClient.Timeout`. The solution must build
> (`dotnet build OrderManagement.sln`) and `GET /api/products` and `/api/orders` must still
> work. Add a short note to `docs/` if behavior changes.

Acceptance criteria (bullet list) helps the agent know when it's done.

## Step 2 — Assign to Copilot
- On GitHub: open the issue → **Assignees** → select **Copilot**. (Or from VS Code, use
  *Delegate to coding agent*.)
- Copilot reacts (👀), creates a branch, and starts working. You can close the laptop.

## Step 3 — Review the PR
- Copilot opens a **draft PR** linked to the issue, with a summary of changes and the
  build/test results it ran.
- Review the diff like any colleague's PR. Leave **review comments**; Copilot will push
  follow-up commits addressing them.
- When satisfied, approve and **merge**.

## Step 4 — Pull and verify locally
```powershell
git fetch origin
git switch <copilot-branch>      # or pull main after merge
dotnet build OrderManagement.sln
pwsh tools/smoke-test.ps1
```

## Local vs. cloud — when to use which

| | **Local** (Lab 05) | **Cloud** (this lab) |
|--|--|--|
| Where it runs | your machine | GitHub-hosted env |
| Interaction | live, step-by-step approval | async, review a PR |
| Best for | exploratory work, things needing your local services | well-scoped, parallelizable tasks |
| You can… | watch & redirect mid-task | fire-and-forget, batch several issues |

## Talking points
- Same kind of task as Lab 05, **different delegation model**. Show both so attendees pick
  the right tool.
- A clear issue with **acceptance criteria** is the single biggest factor in a good cloud
  result — the prompt-writing skill transfers directly.
- You can hand off **several issues at once** and review the PRs as they land.
