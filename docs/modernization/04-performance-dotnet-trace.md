# Lab 04 — Performance with `dotnet-trace`

**Goal:** profile the BFF with [`dotnet-trace`](https://learn.microsoft.com/dotnet/core/diagnostics/dotnet-trace),
find the hot path behind the slow `/api/dashboard` endpoint, and let Copilot fix it. Then
re-trace to prove the win.

**Time:** ~40 min · **Branch:** `git switch -c lab/04-perf`

---

## The problem

`GET /api/dashboard` is slow on purpose. In `src/web/OrderManagement.Web/Services/ReportService.cs`:
- `BuildDashboardHtml()` does a `Thread.Sleep(250)` and builds a string in a loop.
- `ComputeExpensiveChecksum()` uses **trial division up to n** (an O(n²) prime check) and is
  recomputed every request with **no caching**.
- `GetEnrichedOrders()` does an **O(orders × customers)** nested-loop join and calls the
  downstream API **synchronously** (`.Result`).

## Step 0 — Tooling

```powershell
dotnet tool install -g dotnet-trace   # once
dotnet-trace --version
```

## Step 1 — Run the app and generate load

Terminal 1 — Python API:
```powershell
cd src/api ; .\.venv\Scripts\python.exe app.py
```
Terminal 2 — BFF (note the process so we can attach):
```powershell
cd src/web/OrderManagement.Web ; dotnet run -c Release
```
Terminal 3 — find the PID and create steady load:
```powershell
dotnet-trace ps                       # note the OrderManagement.Web PID
# hammer the slow endpoint in a loop
1..20 | ForEach-Object { Invoke-WebRequest -UseBasicParsing http://localhost:5080/api/dashboard | Out-Null }
```

## Step 2 — Collect a trace

In a fourth terminal, attach to the BFF PID and collect while the load loop runs:
```powershell
dotnet-trace collect --process-id <PID> --format speedscope --output dashboard.nettrace
# let it run a few seconds while Step 1's loop hits /api/dashboard, then press Enter to stop
```
This writes `dashboard.nettrace` and `dashboard.speedscope.json`.

> Alternative (launch + trace a child process):
> ```powershell
> dotnet-trace collect --format speedscope -- dotnet run -c Release --project src/web/OrderManagement.Web
> ```

## Step 3 — Read the trace

Open the speedscope file at <https://www.speedscope.app/> (or use PerfView / Visual Studio's
trace viewer with the `.nettrace`). You should clearly see time dominated by:
- `ReportService.ComputeExpensiveChecksum` (CPU), and
- a blocked/sleeping segment from `Thread.Sleep` / the synchronous downstream call.

This is the teaching moment: **measure, don't guess.**

## Step 4 — Fix with Copilot

Open `ReportService.cs`, select the class, and use the *Performance* prompt in
[`prompts/dotnet-bff-prompts.md`](../prompts/dotnet-bff-prompts.md). Aim for:
- Replace trial division with a **sieve of Eratosthenes** or check up to `sqrt(n)`; better,
  **cache** the checksum (it only depends on a count).
- Remove the artificial `Thread.Sleep`.
- Replace the **O(n²)** join with a `Dictionary<int, CustomerDto>` lookup.
- Make the path **async** end-to-end and use `IHttpClientFactory` (ties back to lab 03/05):
  `PythonApiClient` methods become `async Task<string>` with `await`, registered with
  `builder.Services.AddHttpClient<PythonApiClient>()`.
- Use `StringBuilder` (or return JSON) instead of string concatenation.

## Step 5 — Re-trace and compare

Repeat Steps 1–3. Compare wall-clock per request:
```powershell
Measure-Command { Invoke-WebRequest -UseBasicParsing http://localhost:5080/api/dashboard } | Select-Object TotalMilliseconds
```
Expect a large drop (hundreds of ms → low tens). The flame graph no longer shows
`ComputeExpensiveChecksum` as the hot frame. Commit:
```powershell
git commit -am "lab 04: fix dashboard hot path (sieve+cache, async, dict join, no sleep)"
```

## Bonus — trace the Python slow report
The Python `/reports/revenue` endpoint is slow via `time.sleep(0.05)` per order. Use Python
profiling (`python -m cProfile -s tottime app.py` against a load script, or `py-spy`) to
show the same "measure then fix" loop on the other tier.

## Talking points
- `dotnet-trace` is **cross-platform** and needs no IDE — great for prod/CI.
- The workflow is: **trace → identify hotspot → ask Copilot for a targeted fix → re-trace**.
  Copilot proposes the algorithmic change; the trace proves it worked.
- Distinguish **CPU-bound** (the prime loop) from **blocking/wait** (sleep, sync-over-async)
  — different fixes.
