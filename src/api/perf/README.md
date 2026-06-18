# API performance testing with Locust

[Locust](https://locust.io/) load tests for the Order Management Python API
(`src/api`). The tests exercise every public endpoint with realistic, weighted traffic.

## Layout

| File | Purpose |
|------|---------|
| `locustfile.py` | The user behavior (tasks + weights) hitting the API endpoints. |
| `requirements.txt` | Test-only dependency (`locust`), separate from the app's `requirements.txt`. |

## Prerequisites

Install the test dependency into the existing virtual environment (run from `src/api`):

```powershell
.\.venv\Scripts\python.exe -m pip install -r perf\requirements.txt
```

## Run

**Terminal 1 — start the API** (from `src/api`):

```powershell
.\.venv\Scripts\python.exe app.py
```

**Terminal 2 — run Locust** (from `src/api`):

Headless (CI-friendly): 50 users, spawning 10/s, for 1 minute, writing CSV + HTML reports:

```powershell
.\.venv\Scripts\locust -f perf\locustfile.py --host http://localhost:5001 `
    --headless -u 50 -r 10 -t 1m --csv perf\results --html perf\report.html
```

Interactive web UI (then open http://localhost:8089 and set users/spawn rate there):

```powershell
.\.venv\Scripts\locust -f perf\locustfile.py --host http://localhost:5001
```

### Useful flags

| Flag | Meaning |
|------|---------|
| `-u, --users` | Peak number of concurrent simulated users. |
| `-r, --spawn-rate` | Users started per second until peak. |
| `-t, --run-time` | Test duration, e.g. `30s`, `5m`, `1h` (headless). |
| `--csv PREFIX` | Write `PREFIX_stats.csv`, `PREFIX_failures.csv`, etc. |
| `--html FILE` | Write a standalone HTML report. |
| `--host` | Base URL of the API under test. |

## What is tested

A read-heavy mix that mirrors typical API usage (weights in parentheses):

- **Reads:** `GET /orders` (10), `GET /orders/[id]` (6), `GET /products` (6),
  `GET /customers` (4), `GET /reports/revenue` (4), `GET /health` (2)
- **Writes:** `POST /login` (3), `POST /customers` (1), `POST /products` (1),
  `POST /orders` (1), `PUT /orders/[id]/status` (1)

Write tasks use `catch_response` so that expected business responses (e.g. `409` for a
duplicate email or out-of-stock product) are **not** counted as failures.

## Interpreting results

Locust reports per-endpoint **RPS**, **median / 95th / 99th percentile** latency, and
**failure rate**. Watch in particular:

- `GET /reports/revenue` — now backed by a single aggregate query (should stay fast).
- `GET /orders` — single JOIN with pagination; latency should be flat as load grows.
- Rising p95/p99 or failures as users increase indicate a saturation point.

## Notes

- The tests assume the **seeded** database (created automatically on first run). Seeded
  product `5` is intentionally out of stock; `POST /orders` tolerates the resulting `409`.
- `perf/results*.csv` and `perf/report.html` are test artifacts — they are git-ignored.
- Use a fresh `orders.db` for comparable baseline-vs-after runs; the test creates extra
  customers/products/orders over time.
