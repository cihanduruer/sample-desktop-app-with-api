# 01-upgrade-projects-to-net10 — Progress Details

## Summary
Upgraded the entire solution from .NET 8 to .NET 10 in a single All-At-Once pass, including the two test projects that reference the WPF app.

## Files modified
- `src/web/OrderManagement.Web/OrderManagement.Web.csproj` — `net8.0` → `net10.0`; `Microsoft.AspNetCore.OpenApi` `8.0.28` → `10.0.9`.
- `src/desktop/OrderManagement.Desktop/OrderManagement.Desktop.csproj` — `net8.0-windows` → `net10.0-windows` (kept `UseWPF`, `WinExe`).
- `tests/OrderManagement.Desktop.Tests/OrderManagement.Desktop.Tests.csproj` — `net8.0-windows` → `net10.0-windows` (must match the referenced Desktop project).
- `tests/OrderManagement.Desktop.UITests/OrderManagement.Desktop.UITests.csproj` — `net8.0-windows` → `net10.0-windows`; added `System.Drawing.Common` `8.0.0` to override FlaUI's vulnerable transitive `5.0.2`.

## Decisions / notes
- **Expanded scope**: the two test projects were added during the earlier desktop bug-fix work and reference the Desktop project. An older TFM cannot reference a newer one, so they had to move to `net10.0-windows` together with the app. 4 projects retargeted, not 2.
- `CommunityToolkit.Mvvm` 8.3.2 left as-is (assessment: compatible). `Swashbuckle.AspNetCore` updated to **10.2.1** to maintain full compatibility with net10.0 and `Microsoft.AspNetCore.OpenApi` 10.0.9.
- `Microsoft.AspNetCore.OpenApi` target version confirmed via package tooling as **10.0.9**.
- **NU1904 vulnerability** (`System.Drawing.Common` 5.0.2, critical) surfaced from FlaUI's transitive graph. Resolved by pinning a direct reference to the patched stable **8.0.0** (the tooling-suggested 11.0.0 was a preview, which was avoided). Not suppressed.
- Behavioral API changes flagged in the assessment (`System.Uri`, `System.Net.Http.HttpContent`) are low-impact/runtime-only; no source changes required.

## Validation
- `dotnet build OrderManagement.sln -c Debug` → **Build succeeded, 0 Warnings, 0 Errors**.
- Output assemblies confirmed at `bin\Debug\net10.0\` (Web) and `bin\Debug\net10.0-windows\` (Desktop + both test projects).
- `dotnet test OrderManagement.Desktop.Tests` → **6/6 passed** on `.NETCoreApp,Version=v10.0`.
- Full unit + UI suite runs in task 02 (solution-validation).

## Done-when verification
- ✅ All four `.csproj` target `net10.0` / `net10.0-windows`.
- ✅ `Microsoft.AspNetCore.OpenApi` updated to `10.0.9`.
- ✅ Full solution builds with 0 errors and 0 warnings.
