# Prompts — .NET BFF (`src/web/OrderManagement.Web`)

Copy-paste prompts for modernizing the ASP.NET Core BFF. Use **Agent mode** for multi-file
tasks; review diffs; run `dotnet build OrderManagement.sln` and `tools/smoke-test.ps1`.

## Lab 01 — Upgrade to .NET 9
> Upgrade `src/web/OrderManagement.Web` from `net8.0` to `net9.0`. Change the
> `TargetFramework`, update `Microsoft.AspNetCore.OpenApi` to a 9.0 version, fix any
> obsolete API usage, and rebuild until the build is clean. Then run the app and confirm
> `/swagger` and `/api/products` work.

(WPF equivalent is in [`desktop-wpf-prompts.md`](desktop-wpf-prompts.md).)

## HTTP layer — async + IHttpClientFactory
> In `Services/PythonApiClient.cs`, stop creating `new HttpClient()` per call. Register a
> **typed client** with `builder.Services.AddHttpClient<PythonApiClient>()` and inject
> `HttpClient`. Make every method `async Task<...>` and `await` the calls — remove all
> `.Result`. Set a `Timeout`. Update `Program.cs` handlers and `ReportService` to be async
> end-to-end. Keep `PythonApi:BaseUrl` configurable.

## Performance (Lab 04)
> Optimize `Services/ReportService.cs`. Replace `ComputeExpensiveChecksum`'s trial-division
> prime check with a Sieve of Eratosthenes (or check up to √n) and **cache** the result.
> Remove the `Thread.Sleep(250)`. Replace the O(n²) order→customer join with a
> `Dictionary<int, CustomerDto>` lookup. Build the dashboard with `StringBuilder` or return
> JSON. Re-run and confirm `/api/dashboard` is dramatically faster.

## Money as decimal (Lab 02)
> Change money fields from `double` to `decimal` across `Models/Dtos.cs` and `ReportService`.
> Keep the `[JsonPropertyName]` mappings so the JSON contract is unchanged. Format currency
> once at the edge.

## Security & config
> Remove the secrets from `appsettings.json` and the `ApiKey` constant; read them from
> user-secrets/environment via `IConfiguration`/Options. Stop logging credentials in the
> `/api/login` handler. Tighten CORS to the known origins (`http://localhost:5173`) instead
> of `AllowAnyOrigin`.

## Error handling & validation
> Add model validation to the minimal-API endpoints, return `ProblemDetails` on failure, and
> add a global exception handler. Don't let downstream failures surface as raw 500s with
> stack traces.

## Tests
> Add an xUnit test project that uses `WebApplicationFactory` to test `/api/products` and
> `/api/orders` with a stubbed `PythonApiClient`. Wire it into the solution and run
> `dotnet test`.
