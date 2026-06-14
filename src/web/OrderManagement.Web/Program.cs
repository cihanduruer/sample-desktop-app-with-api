using OrderManagement.Web.Models;
using OrderManagement.Web.Services;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// BAD: services registered as singletons even though PythonApiClient news up an
// HttpClient on every call. The right answer is IHttpClientFactory / typed clients.
builder.Services.AddSingleton<PythonApiClient>();
builder.Services.AddSingleton<ReportService>();

// BAD: CORS open to everything. AllowAnyOrigin + AllowCredentials is actually an
// invalid/insecure combination and defeats the purpose of CORS.
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader();
    });
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();

// Serve the built React app from wwwroot (populated by `npm run build`).
app.UseDefaultFiles();
app.UseStaticFiles();

var api = app.MapGroup("/api");

// GET /api/orders - enriched orders. BAD: blocks threads + O(n^2) join in the service.
api.MapGet("/orders", (ReportService reports) =>
{
    var orders = reports.GetEnrichedOrders();
    return Results.Json(orders);
});

// GET /api/products - straight proxy. BAD: re-serializes already-serialized JSON.
api.MapGet("/products", (PythonApiClient client) =>
{
    var json = client.GetProductsJson();
    var products = JsonSerializer.Deserialize<List<ProductDto>>(json);
    return Results.Json(products);
});

// GET /api/dashboard - the slow endpoint. BAD: Thread.Sleep + CPU burn + no caching.
// This is the primary target for the dotnet-trace performance exercise.
api.MapGet("/dashboard", (ReportService reports) =>
{
    var html = reports.BuildDashboardHtml();
    return Results.Content(html, "text/html");
});

// GET /api/revenue - proxies the deliberately slow Python report. BAD: blocking.
api.MapGet("/revenue", (PythonApiClient client) =>
{
    var json = client.GetRevenueReportJson();
    return Results.Content(json, "application/json");
});

// POST /api/login - proxies login. BAD: forwards plaintext creds, no validation.
api.MapPost("/login", (LoginRequest req, PythonApiClient client) =>
{
    var result = client.Login(req.Email, req.Password);
    // BAD: log the credentials in clear text.
    app.Logger.LogInformation("Login attempt for {Email} with password {Password}", req.Email, req.Password);
    return Results.Content(result, "application/json");
});

// PUT /api/orders/{id}/status - proxies a status update. BAD: no validation/allow-list.
api.MapPut("/orders/{id}/status", (int id, StatusRequest req, PythonApiClient client) =>
{
    var result = client.UpdateStatus(id, req.Status);
    return Results.Content(result, "application/json");
});

// SPA fallback so client-side routes resolve to index.html (when wwwroot is populated).
app.MapFallbackToFile("index.html");

app.Run();

record LoginRequest(string Email, string Password);
record StatusRequest(string Status);
