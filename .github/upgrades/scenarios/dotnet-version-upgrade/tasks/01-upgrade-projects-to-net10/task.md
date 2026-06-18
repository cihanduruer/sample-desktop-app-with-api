# 01-upgrade-projects-to-net10: Upgrade both projects to .NET 10

Verify the .NET 10 SDK toolchain (and any `global.json` constraint), then upgrade both projects in a single pass. `OrderManagement.Web` moves from `net8.0` to `net10.0`; `OrderManagement.Desktop` (WPF) moves from `net8.0-windows` to `net10.0-windows`. Update the recommended NuGet package and address the behavioral API changes flagged in the assessment, then build the full solution to zero errors and zero warnings.

Scope and assessment context: The Web project needs `Microsoft.AspNetCore.OpenApi` bumped from 8.0.28 to 10.0.9 (`Swashbuckle.AspNetCore` 6.6.2 is already compatible) and has 2 low-impact behavioral changes around `System.Net.Http.HttpContent` and `System.Uri`. The Desktop project keeps `CommunityToolkit.Mvvm` 8.3.2 (compatible); its 23 "binary-incompatible" WPF API entries (`System.Windows.*` — `MessageBox`, `Application`, `Window`, routed events, XAML component connectors) are standard WPF framework assemblies that resolve via recompilation against .NET 10 — no source rewrites are expected. It also has 6 low-impact behavioral changes (`HttpContent`, `Uri`).

Research starting points: confirm whether a `global.json` pins the SDK; review the `Uri` constructor and `HttpClient`/`HttpContent` usage in the Desktop `MainViewModel`/API client and the Web BFF's HTTP forwarding for the flagged behavioral changes; verify the WPF project keeps `<UseWPF>`/`-windows` TFM after the bump. Fix every build warning surfaced in the modified projects (do not suppress).

## Research findings (this session)
- **SDK**: .NET 10 SDK 10.0.301 installed; no `global.json` pins the SDK (verified).
- **Package version confirmed**: `Microsoft.AspNetCore.OpenApi` -> **10.0.9** for net10.0 (via package tooling).
- **Expanded scope — test projects**: `OrderManagement.Desktop.Tests` and `OrderManagement.Desktop.UITests` (both `net8.0-windows`) reference the Desktop project and MUST also move to `net10.0-windows`, otherwise an older TFM referencing a newer one breaks the build. So **4 projects** are retargeted in this task, not 2.
- **Behavioral changes** (`System.Uri`, `System.Net.Http.HttpContent`): low-impact, runtime-only; no source changes required — exercised by the smoke tests.

**Done when**: all four `.csproj` files target `net10.0` / `net10.0-windows`, `Microsoft.AspNetCore.OpenApi` is updated to the .NET 10 compatible version (10.0.9), and the full solution builds with 0 errors and 0 warnings.
