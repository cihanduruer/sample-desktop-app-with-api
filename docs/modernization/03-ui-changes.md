# Lab 03 — UI changes

**Goal:** fix the user-facing problems in both UIs with Copilot: make the **WPF** desktop
app responsive (proper async MVVM, no UI-thread blocking, logic out of code-behind), and
**harden the React** UI (typed, error-handling, no XSS, componentized).

**Copilot capability:** Agent mode + inline chat; CommunityToolkit.Mvvm patterns.

**Time:** ~20–30 min · **Branch:** `git switch -c lab/03-ui`

---

## Part A — WPF desktop (async + MVVM)

### The problem
- `MainViewModel` constructor calls `LoadOrders()` which **blocks the UI thread**
  (`.GetAwaiter().GetResult()`).
- `[RelayCommand]` methods are synchronous and block on `.Result` — the window freezes on
  Login / Update Status / **Load Revenue Report**.
- Export logic lives in **code-behind** (`MainWindow.xaml.cs`), with an empty `catch`.
- `new HttpClient()` per call; plaintext password bound to a `TextBox`.

### Fix it with Copilot
Use the prompts in
[`prompts/desktop-wpf-prompts.md`](../prompts/desktop-wpf-prompts.md). Target end state:
- Async relay commands: `[RelayCommand] private async Task LoadOrdersAsync()` etc., using
  `await`. CommunityToolkit.Mvvm generates an `IAsyncRelayCommand` that disables the button
  while running and surfaces exceptions.
- No work in the constructor — load on a `Loaded` event or an async init command.
- A single injected `HttpClient` (via `IHttpClientFactory`) or one shared instance.
- Move the CSV export into an async command on the view model; use `StringBuilder`/a CSV
  writer and a save dialog instead of a hard-coded `C:\temp` path.
- Use a `PasswordBox` (bind via a helper) and stop holding the plaintext password.

### Verify
```powershell
dotnet run --project src/desktop/OrderManagement.Desktop
```
Click **Load Revenue Report** — the window now stays responsive (a spinner/disabled button
instead of a freeze). Commit.

> Demo tip: show the freeze *before* (drag the window while the report runs — it won't
> redraw) and the responsiveness *after*.

## Part B — React UI (hardening)

### The problem
`ClientApp/src/App.tsx` is one giant component: `any` types, `fetch` with no error handling
or cleanup, **token in `localStorage`**, **`dangerouslySetInnerHTML`** (XSS), array-index
keys, hard-coded API URL, totals recomputed each render.

### Fix it with Copilot
Use [`prompts/react-web-prompts.md`](../prompts/react-web-prompts.md). Target end state:
- Shared `types.ts` (`Order`, `Product`); remove `any`; turn on `strict` in `tsconfig.json`.
- A small `api.ts` data layer that checks `response.ok`, handles errors, and reads the base
  URL from `import.meta.env.VITE_API_BASE` (with a dev default).
- Split into components (`OrdersTable`, `LoginForm`, `Dashboard`) + a `useOrders` hook with
  `AbortController` cleanup and loading/error state.
- Replace `dangerouslySetInnerHTML` — have the BFF return JSON (or render text); never
  inject HTML.
- Stable keys (order id), `useMemo` for the grand total.

### Verify
```powershell
cd src/web/OrderManagement.Web/ClientApp
npm run build   # tsc strict + vite build must pass
npm run dev     # UI still works against the BFF
```
Commit.

## Talking points
- WPF: the fix is *small* but high-impact — async commands + no blocking. Tie it back to
  the `dotnet.instructions.md` rule "async all the way."
- React: `strict` TypeScript turns latent bugs into compile errors — let Copilot fix the
  cascade of new type errors. That cascade-fix is a great agent-mode demo.
