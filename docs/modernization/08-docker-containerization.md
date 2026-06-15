# Lab 08 — Docker containerization

**Goal:** containerize the demo **after** modernizing it. Build images for the Python API
and the .NET BFF (which also serves the React UI), and run the whole stack with
`docker compose`.

**Copilot capability:** generating/refining Dockerfiles and compose with Copilot;
"containerize this app" prompts.

**Time:** ~30 min · **Prerequisite:** Docker Desktop (Linux containers).

> Do this **last**. Containerizing a modernized app is clean; containerizing the broken
> "before" just packages the bugs.

---

## What's containerizable

| Tier | Containerized? | Why |
|------|----------------|-----|
| Python API | ✅ | standard Linux web service |
| .NET BFF + React UI | ✅ | multi-stage build (Node builds the SPA, .NET serves it) |
| WPF desktop | ❌ | a **Windows GUI** app; there is no meaningful Linux container, and Windows containers can't render an interactive desktop. Ship it as an MSIX/installer instead. |

This repo ships ready-made artifacts (review them with the class):
- `src/api/Dockerfile` + `.dockerignore`
- `src/web/OrderManagement.Web/Dockerfile` (multi-stage) + `.dockerignore`
- `docker-compose.yml` (root)

## Key enabler: configurable downstream URL

Natively the BFF calls `http://localhost:5001`. In containers each service has its own
network identity, so the URL must be configurable. The BFF already reads
`PythonApi:BaseUrl` from configuration (with a localhost fallback), and the compose file
overrides it:
```yaml
environment:
  - PythonApi__BaseUrl=http://api:5001   # "api" is the compose service name
```
> If you skipped the earlier labs, this is the one code change Docker requires. Ask Copilot:
> *"make the Python API base URL in `PythonApiClient` read from configuration key
> `PythonApi:BaseUrl` with a localhost fallback."*

## Step 1 — Build & run individually (understand each image)

Python API:
```powershell
docker build -t ordermgmt-api ./src/api
docker run --rm -p 5001:5001 ordermgmt-api
# verify: curl http://localhost:5001/health
```

.NET BFF + React (multi-stage):
```powershell
docker build -t ordermgmt-web ./src/web/OrderManagement.Web
docker run --rm -p 5080:5080 -e PythonApi__BaseUrl=http://host.docker.internal:5001 ordermgmt-web
# verify: open http://localhost:5080  (SPA) and http://localhost:5080/api/products
```

## Step 2 — Run the whole stack with Compose

```powershell
docker compose up --build
```
- Web UI + BFF: <http://localhost:5080>
- Python API: <http://localhost:5001>

`docker compose down` to stop.

## Step 3 — Verify

```powershell
pwsh tools/smoke-test.ps1   # hits 5001 + 5080 against the containers
```
All green → the stack runs in Docker.

## Step 4 — Harden (let Copilot help)

Use Copilot to improve the images, e.g.:
- **Python:** run a production WSGI server (`waitress`/`gunicorn`) instead of the Flask dev
  server; drop `debug=True`; run as a **non-root** user; pin the base image digest.
- **.NET:** use the **chiseled**/`-noble-chiseled` runtime image, run as non-root, add a
  `HEALTHCHECK`, and enable `PublishTrimmed`/ReadyToRun if appropriate.
- **General:** add `.dockerignore` hygiene (done), multi-stage caching, and a compose
  `healthcheck` + `depends_on: condition: service_healthy`.

Sample prompt:
> Harden `src/api/Dockerfile` for production: install and run `waitress` serving `app:app`
> on 0.0.0.0:5001, remove Flask debug mode, create and switch to a non-root user, and add a
> HEALTHCHECK hitting `/health`. Keep the image small.

## Step 5 — Persist data (optional)
Mount a volume so the SQLite DB survives restarts:
```yaml
  api:
    volumes:
      - api-data:/app
volumes:
  api-data:
```
(Or migrate to a real database — a natural follow-on modernization.)

## Talking points
- The **multi-stage** .NET image is the highlight: Node builds the SPA in stage 1, the .NET
  SDK publishes in stage 2, and a slim ASP.NET runtime serves both in stage 3.
- Containerization surfaced the **hard-coded URL** smell — a great example of why config
  belongs in the environment.
- WPF reminds the class that **not everything containerizes**; pick the right packaging per
  tier.

🎉 That completes the journey: **modernized → fast → secure → containerized.**
