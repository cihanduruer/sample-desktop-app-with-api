# .NET Version Upgrade

## Preferences
- **Flow Mode**: Automatic
- **Commit Strategy**: Single Commit at End
- **Pace**: Standard

## Source Control
- **Repository root**: C:\Projects\sample-desktop-app-with-api
- **Working branch**: upgrade-dotnet-10
- **Commit strategy**: Single Commit at End

## Upgrade Options
**Source**: .github/upgrades/scenarios/dotnet-version-upgrade/upgrade-options.md

### Strategy
- Upgrade Strategy: All-At-Once

## Strategy
**Selected**: All-At-Once
**Rationale**: 2 small, independent, SDK-style apps on net8.0 (plus their test projects), both Low difficulty, no inter-project app dependencies — a single atomic upgrade is lowest-risk.

### Execution Constraints
- Single atomic upgrade — bump both apps AND their test projects together; validate the full solution build after.
- Target: net10.0 (Desktop and its test projects: net10.0-windows; Web: net10.0).
- Update Microsoft.AspNetCore.OpenApi to the net10.0-compatible version (~10.0.x).
- Build to 0 errors / 0 warnings; never suppress warnings.
- Re-run the unit + UI smoke tests after the upgrade.

## Decisions
- User confirmed upgrade to .NET 10 (LTS, EOL 2028-11-14) after reviewing the plan.
- Assessment found both apps Low difficulty, SDK-style, no incompatible packages.
- Test projects (OrderManagement.Desktop.Tests, OrderManagement.Desktop.UITests) added during the desktop bug-fix must move to net10.0-windows alongside the Desktop project they reference (older TFM cannot reference a newer one).
- Prior session left scenario.json marking both tasks "Completed" without doing the work; planning artifacts rebuilt and the upgrade executed for real on branch upgrade-dotnet-10.

## Custom Instructions
<!-- Task-specific overrides: "For {taskId}: {instruction}" -->
