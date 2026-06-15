# Lab 05 — Agentic **local** delegation (Copilot agent mode)

**Goal:** hand Copilot a *whole task* and let it work autonomously **on your machine** in
**agent mode** — planning, editing multiple files, running commands, and iterating until the
task is done and verified.

**Copilot capability:** Agent mode in VS Code / Visual Studio (local delegation).

**Time:** ~20 min · **Branch:** `git switch -c lab/05-local-agent`

---

## What "local delegation" means

In **agent mode**, you give a goal (not step-by-step edits). Copilot:
1. explores the repo, 2. proposes a plan, 3. makes multi-file edits, 4. runs tools
(build/test/CLI), 5. reads the output and fixes problems, looping until done — all in your
local working tree, with you watching and approving.

This is different from *Ask* (answers) and *Edit* (scoped single change).

## Step 1 — Enable agent mode
- **VS Code:** open the Copilot Chat view → set the mode selector to **Agent**. Ensure tools
  (terminal, edits) are allowed.
- **Visual Studio 2022:** Copilot Chat → **Agent**.

The repo's `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md`
are automatically in context (lab 07).

## Step 2 — Delegate a real, multi-file task

Pick a task that genuinely spans files. Good candidate: **eliminate the SQL injection and
plaintext passwords in the Python API.** Paste into agent mode:

> Secure the Python Flask API in `src/api`. Replace every SQL string built with f-strings or
> `+`/`%` with **parameterized queries**. Hash passwords with `werkzeug.security`
> (`generate_password_hash`/`check_password_hash`) on create and verify on login; migrate the
> seed data and stop returning the `password` column anywhere. Remove the hard-coded admin
> backdoor. Add input validation and correct HTTP status codes. Keep the API runnable; after
> your changes, delete `orders.db`, restart the app, and confirm `/health`, `/orders`, and a
> valid `/login` all work. Show me the diff and a summary of what you changed and why.

Other good local-delegation tasks:
- "Introduce `IHttpClientFactory` typed clients across the BFF and make all calls async."
- "Add a `pytest` suite covering the orders endpoints, then run it."

## Step 3 — Supervise
- Watch the **plan** and the **edits**. Approve terminal commands.
- When it runs the app / tests and something fails, let it read the error and retry.
- **Review the final diff** before accepting. Reject anything unclear and ask for changes.

## Step 4 — Verify
```powershell
Remove-Item src/api/orders.db -ErrorAction SilentlyContinue
cd src/api ; .\.venv\Scripts\python.exe app.py    # in another terminal
pwsh tools/smoke-test.ps1
```
Confirm: parameterized queries everywhere (`Select-String -Path src/api/*.py -Pattern "f\"SELECT|'%s'"` returns nothing), login still works, `/customers` has no `password`. Commit.

## Talking points
- **You stay in control:** local agent mode is interactive — approve tools, review diffs.
- It shines on **"touches many files + needs to run something to know if it worked"** tasks.
- Contrast with **Lab 06**: same style of task, but delegated to the **cloud** so you can
  walk away and review a PR later.
