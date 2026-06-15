# Lab 02 — Data-model changes

**Goal:** make a cross-cutting data-model change with Copilot **agent mode**: represent
money as `decimal` instead of `double`, add real database constraints (PK/FK, NOT NULL,
indexes), stop leaking the password column, and flow the change through every tier.

**Copilot capability:** Agent mode multi-file edits; `.github` instructions steering.

**Time:** ~30 min · **Branch:** `git switch -c lab/02-data-model`

---

## The problem

- Money is `double` in C# (`Order.Total`, `Product.Price`, `OrderItem.unit_price`) and
  `REAL` in SQLite — floating-point money rounds wrong (you can see `269.84000000000003`
  in the dashboard output).
- No constraints/foreign keys/indexes (`src/api/database.py`).
- `/customers` returns the **plaintext `password`** column; the .NET and React models
  happily carry it.

## Step 1 — Decide the target shape

Talk through the desired model with the class:
- `price`/`unit_price`/`total` → `decimal` (C#), stored as INTEGER cents **or** `NUMERIC`
  in SQLite; never serialize the password.
- Add `FOREIGN KEY`s and `NOT NULL`, plus an index on `orders.customer_id` and
  `order_items.order_id`.

## Step 2 — Drive it tier by tier with Copilot (Agent mode)

Use the prompts in:
- [`prompts/python-api-prompts.md`](../prompts/python-api-prompts.md) → *Data model*
- [`prompts/dotnet-bff-prompts.md`](../prompts/dotnet-bff-prompts.md) → *Money as decimal*
- [`prompts/desktop-wpf-prompts.md`](../prompts/desktop-wpf-prompts.md) → *Money as decimal*
- [`prompts/react-web-prompts.md`](../prompts/react-web-prompts.md) → *Typed models*

Suggested sequence (one Copilot Agent request each, reviewing the diff between):

1. **Python schema + API**: add constraints/FKs/indexes in `database.py`; stop selecting
   `password` in `/customers` and `/login`; return money rounded to 2 dp (or cents).
2. **.NET models** (`src/web/OrderManagement.Web/Models/Dtos.cs` and
   `src/desktop/.../Models/Models.cs`): change `double` → `decimal`, remove the `Password`
   property, keep the `[JsonPropertyName]` mappings.
3. **.NET BFF logic** (`ReportService`): make totals `decimal`; format currency once.
4. **React** (`ClientApp/src`): introduce a typed `Order`/`Product` interface, drop `any`,
   format currency with `Intl.NumberFormat`.

> Because the `.github/instructions/*.instructions.md` files say "money is `decimal`" and
> "never return plaintext passwords", Copilot will push in the right direction
> automatically (lab 07 explains this).

## Step 3 — Reset the seeded DB

The schema changed, so drop the old SQLite file and let it re-seed:
```powershell
Remove-Item src/api/orders.db -ErrorAction SilentlyContinue
```

## Step 4 — Verify

```powershell
pwsh tools/run-all.ps1
pwsh tools/smoke-test.ps1
```
- `/customers` no longer contains a `password` field.
- Totals are exact (e.g. `269.84`, not `269.84000000000003`).
- The BFF and WPF still compile and display orders.

Commit: `git commit -am "lab 02: money as decimal, DB constraints, stop leaking passwords"`.

## Talking points
- A data-model change is the classic "touches everything" task — exactly where agent mode's
  **multi-file** edits save time.
- Stress **review discipline**: verify the JSON property names still line up across Python
  ↔ .NET ↔ React after the change.
- This pairs naturally with hashing passwords (do it here or in lab 05).
