---
applyTo: "src/web/OrderManagement.Web/ClientApp/**"
---

# Instructions for the React + TypeScript UI

- **Type everything.** Replace `any` with shared interfaces/models. Turn TypeScript
  `strict` mode on.
- **Data fetching:** handle loading and error states, check `response.ok`, and clean up
  effects (AbortController) to avoid setting state after unmount. Consider a small data
  layer / React Query instead of bare `fetch` in components.
- **Security:** do not store auth tokens in `localStorage`; avoid
  `dangerouslySetInnerHTML`. Render server data as text.
- **Configuration:** read the API base URL from an env var (`import.meta.env`), not a
  hard-coded `http://localhost:5080`.
- **Structure:** split the single giant `App.tsx` into focused components and hooks; use
  stable keys (not array indices); memoize derived values (totals) where it matters.
