# 03 — Running everything natively

Goal: prove all four tiers run on your machine **before** any modernization. Use four
terminals (or the helper script at the end).

> All commands are run from the repository root unless noted.

## 1. Python API (port 5001)

```powershell
cd src/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Expected: `Running on http://0.0.0.0:5001`. The SQLite DB `orders.db` is created and seeded
on first run.

Verify:
```powershell
curl http://localhost:5001/health
curl http://localhost:5001/orders
```

## 2. .NET BFF (port 5080)

```powershell
cd src/web/OrderManagement.Web
dotnet run
```

Expected: `Now listening on: http://localhost:5080`. Open <http://localhost:5080/swagger>.

Verify:
```powershell
curl http://localhost:5080/api/products
curl http://localhost:5080/api/orders
curl http://localhost:5080/api/dashboard   # slow on purpose (~0.7s+)
```

## 3. React UI (port 5173)

```powershell
cd src/web/OrderManagement.Web/ClientApp
npm install
npm run dev
```

Open <http://localhost:5173>. The page lists orders/products (from the BFF), has a login
box (`alice@example.com` / `password123`, or password `admin`), and a **Load Dashboard**
button.

> Production mode: `npm run build` emits the SPA into the BFF's `wwwroot`, after which the
> BFF serves the UI at <http://localhost:5080>.

## 4. WPF desktop

With the Python API running:
```powershell
dotnet run --project src/desktop/OrderManagement.Desktop
```

The window loads orders on startup. Try:
- **Login** (note: it freezes briefly — planted blocking call).
- **Refresh Orders**, select a row, set a status, **Update Status**.
- **Load Revenue Report** — the window goes unresponsive while the slow report runs
  (planted UI-thread block). This is intentional and is fixed in lab 03/04.
- **Export CSV** — writes `C:\temp\orders_export.csv` (planted code-behind logic).

## One-shot helper scripts

Start the API + BFF together (each in its own window):
```powershell
pwsh tools/run-all.ps1            # API + BFF
pwsh tools/run-all.ps1 -WithWeb   # API + BFF + React dev server
```

Smoke-test the running services:
```powershell
pwsh tools/smoke-test.ps1
```

Run the WPF app separately with `dotnet run --project src/desktop/OrderManagement.Desktop`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| BFF returns 500 on `/api/*` | The Python API isn't running, or not on 5001. Start it first. |
| `orders.db is locked` | Stop extra API instances; the global SQLite connection is a planted bug. |
| WPF hangs on launch | The API is down/slow — the view-model constructor blocks (planted). Start the API. |
| Port already in use | Another instance is running. Close it or change the port. |
| React shows empty tables | BFF not running, or CORS/console errors — open dev tools. |

Once everything runs, go to the labs: **[modernization/00-overview.md](modernization/00-overview.md)**.
