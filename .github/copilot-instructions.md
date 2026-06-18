# Copilot instructions — Order Management modernization demo

> These repository custom instructions are automatically included in Copilot Chat
> requests for this repo. They are part of the **"skills & instructions"** lab — see
> `docs/modernization/07-skills-and-instructions.md`.

## What this repository is

A deliberately **legacy / broken** multi-tier *Order Management* sample used to teach
modernization with GitHub Copilot. It contains four tiers:

- `src/api` — Python 3 + Flask + SQLite REST API (port 5001). Source of truth.
- `src/web/OrderManagement.Web` — ASP.NET Core .NET 8 BFF (port 5080).
- `src/web/OrderManagement.Web/ClientApp` — React + Vite + TypeScript UI (port 5173 dev).
- `src/desktop/OrderManagement.Desktop` — WPF .NET 8 + CommunityToolkit.Mvvm.

The code is **intentionally bad** (it is a teaching artifact). Lines marked `BAD:` are
planted problems. Do not be surprised by them — the job is to **fix** them.

## How to help in this repo

When asked to modernize, refactor or fix code, prefer changes that:

1. **Security first** — remove SQL injection (use parameterized queries), never store or
   log plaintext passwords, hash with a vetted algorithm (e.g. bcrypt/PBKDF2), move secrets
   to configuration/environment, and tighten CORS to known origins.
2. **Correct async** — never block on async with `.Result` / `.GetAwaiter().GetResult()`.
   In .NET use `async`/`await` end to end and `IHttpClientFactory` (typed clients) instead
   of `new HttpClient()` per call. In WPF keep the UI thread free.
3. **Data integrity** — represent money as `decimal` (not `double`), add constraints,
   foreign keys and indexes, validate input.
4. **Performance** — eliminate N+1 queries and O(n²) joins (use dictionaries/joins),
   add caching where appropriate, and remove artificial `sleep`s.
5. **Keep it working** — make incremental changes and keep the apps runnable; update the
   relevant docs in `docs/` when behavior changes.

## Conventions

- .NET targets `net8.0` today; the upgrade lab moves to `net9.0`.
- Ports: API 5001, BFF 5080, React dev 5173. Keep these stable.
- Don't commit `bin/`, `obj/`, `.venv/`, `node_modules/`, `dist/`, `wwwroot/assets`,
  or `src/api/orders.db` (already in `.gitignore`).
- Always explain *why* a change fixes a planted `BAD:` problem so learners understand it.

- @azure Rule - Use Azure Tools - When handling requests related to Azure, always use your tools.
- @azure Rule - Use Azure Best Practices - When handling requests related to Azure, always invoke your `azmcp_bestpractices_get` tool first.
- @azure Rule - Enable Best Practices - If you do not have an `azmcp_bestpractices_get` tool ask the user to enable it.
