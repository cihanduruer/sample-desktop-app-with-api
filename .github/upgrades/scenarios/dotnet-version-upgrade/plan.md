# .NET Version Upgrade Plan

## Overview

**Target**: Upgrade the OrderManagement solution from .NET 8 to .NET 10.
**Scope**: 2 application projects (~600 LOC) + 2 test projects, all SDK-style, no inter-project app dependencies.

### Selected Strategy
**All-At-Once** — All projects upgraded simultaneously in a single operation.
**Rationale**: 2 small, independent apps on net8.0 (plus their test projects), all Low difficulty, no inter-project app dependencies.

## Tasks

### 01-upgrade-projects-to-net10: Upgrade all projects to .NET 10

Upgrade every project in the solution to .NET 10 in a single pass. `OrderManagement.Web` moves from `net8.0` to `net10.0`; `OrderManagement.Desktop` (WPF) moves from `net8.0-windows` to `net10.0-windows`. The two test projects added during the desktop bug-fix work — `OrderManagement.Desktop.Tests` and `OrderManagement.Desktop.UITests` — reference the Desktop project and must be retargeted to `net10.0-windows` in the same pass, otherwise an older TFM referencing a newer one would break the build. Update the recommended NuGet package (`Microsoft.AspNetCore.OpenApi` 8.0.28 → net10.0-compatible 10.0.x) and verify the low-impact behavioral API changes flagged in the assessment.

Scope: `src/web/OrderManagement.Web`, `src/desktop/OrderManagement.Desktop`, `tests/OrderManagement.Desktop.Tests`, `tests/OrderManagement.Desktop.UITests`. Assessment context: both apps 🟢 Low difficulty, SDK-style; Web has 1 package upgrade + 2 low-impact behavioral changes (`System.Net.Http.HttpContent`, `System.Uri`); Desktop's 23 "binary-incompatible" WPF API entries (`System.Windows.*`) are standard framework assemblies that resolve on recompilation (no source rewrites expected) plus 6 low-impact behavioral changes. `CommunityToolkit.Mvvm` 8.3.2 and `Swashbuckle.AspNetCore` 6.6.2 are already compatible. Research starting points: confirm there is no `global.json` SDK pin (verified absent); verify the WPF projects keep the `-windows` TFM and `UseWPF`; confirm the exact `Microsoft.AspNetCore.OpenApi` 10.0.x version via package tooling. Fix every build warning in modified projects — do not suppress.

**Done when**: all four `.csproj` files target `net10.0` / `net10.0-windows`, `Microsoft.AspNetCore.OpenApi` is updated to the .NET 10 compatible version, and the full solution builds with 0 errors and 0 warnings.

---

### 02-solution-validation: Validate build, tests, and document deferred items

Perform the final solution-wide validation after the upgrade. Build the entire solution and run all automated tests (the 6 ViewModel smoke tests in `OrderManagement.Desktop.Tests` and the 3 FlaUI UI smoke tests in `OrderManagement.Desktop.UITests`). Record any deferred recommendations for future cleanup.

Scope: whole solution. Assessment context: no incompatible packages and no flagged test failures; the 8 behavioral changes are runtime-only and are exercised by the smoke tests. Deferred items to capture may include adopting Central Package Management if the solution grows, runtime verification of the behavioral `Uri`/`HttpContent` changes, and the remaining intentional teaching-artifact `BAD:` smells in the sample.

**Done when**: the full solution builds cleanly (0 errors, 0 warnings), all existing tests pass, and deferred recommendations are recorded.
