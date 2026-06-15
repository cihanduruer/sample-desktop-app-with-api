# Prompts — React UI (`src/web/OrderManagement.Web/ClientApp`)

Copy-paste prompts for hardening the React + TypeScript UI. Review diffs; run `npm run build`
and `npm run dev`.

## Typing & strict mode (Lab 02/03)
> Turn on `strict` in `tsconfig.json`. Create `src/types.ts` with `Order` and `Product`
> interfaces that match the BFF JSON, replace every `any` in `App.tsx`, and fix the
> resulting type errors. Re-enable the build's type check (`tsc -b && vite build`).

## Data layer & error handling
> Extract all `fetch` calls into `src/api.ts`. Each function must check `response.ok`, throw
> typed errors, and accept an `AbortSignal`. Read the base URL from
> `import.meta.env.VITE_API_BASE` with a dev fallback of `http://localhost:5080/api`. Add a
> `.env` and document it.

## Hooks & components (Lab 03)
> Split the giant `App.tsx` into `LoginForm`, `OrdersTable`, `ProductsList`, and `Dashboard`
> components, plus a `useOrders` hook that owns loading/error state and cleans up its effect
> with an `AbortController`. Use the order `id` as the React key (not the array index) and
> `useMemo` for the grand total.

## Security
> Remove the auth token from `localStorage`; keep it in memory (or use httpOnly cookies set
> by the server). Replace `dangerouslySetInnerHTML` for the dashboard — have the BFF return
> JSON and render it as React elements, or render the HTML as escaped text. Never inject
> server HTML.

## UX polish
> Add loading and error UI for the orders/products fetches and a disabled/spinner state on
> the **Load Dashboard** button while the (slow) request is in flight. Add basic form labels
> and accessible markup.

## Tooling
> Add ESLint + Prettier with a sensible React/TypeScript config and an `npm run lint` script,
> then fix the reported issues.
