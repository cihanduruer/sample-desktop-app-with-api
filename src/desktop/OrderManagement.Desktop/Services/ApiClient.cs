using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Collections.Generic;
using System.Threading.Tasks;
using OrderManagement.Desktop.Models;

namespace OrderManagement.Desktop.Services;

// ============================================================================
// TEACHING ARTIFACT - intentionally bad HTTP client.
// Planted problems:
//   * A brand new HttpClient is created for every single call (socket exhaustion).
//   * The base URL and credentials are hard-coded.
//   * Exceptions are swallowed and turned into empty lists / nulls.
//   * No timeouts, no cancellation, no retry, no logging abstraction.
// ============================================================================
public class ApiClient
{
    // BAD: hard-coded endpoint. No configuration, no environment override.
    private const string BaseUrl = "http://localhost:5001";

    // BAD: the "auth token" is just stored in a public mutable field.
    public string? Token;

    public async Task<List<Order>> GetOrdersAsync()
    {
        // BAD: new HttpClient per call.
        var http = new HttpClient();
        try
        {
            var json = await http.GetStringAsync(BaseUrl + "/orders");
            var orders = JsonSerializer.Deserialize<List<Order>>(json);
            return orders ?? new List<Order>();
        }
        catch
        {
            // BAD: swallow everything, caller can't tell success from failure.
            return new List<Order>();
        }
    }

    public async Task<List<Product>> GetProductsAsync()
    {
        var http = new HttpClient();
        try
        {
            var json = await http.GetStringAsync(BaseUrl + "/products");
            return JsonSerializer.Deserialize<List<Product>>(json) ?? new List<Product>();
        }
        catch
        {
            return new List<Product>();
        }
    }

    public async Task<string> LoginAsync(string email, string password)
    {
        var http = new HttpClient();
        // BAD: builds JSON with string concatenation; breaks on quotes; logs nothing.
        var body = "{\"email\":\"" + email + "\",\"password\":\"" + password + "\"}";
        var content = new StringContent(body, Encoding.UTF8, "application/json");
        var resp = await http.PostAsync(BaseUrl + "/login", content);
        var text = await resp.Content.ReadAsStringAsync();
        // BAD: stuff the whole response body in as the "token".
        Token = text;
        return text;
    }

    public async Task UpdateStatusAsync(int orderId, string status)
    {
        var http = new HttpClient();
        var body = "{\"status\":\"" + status + "\"}";
        var content = new StringContent(body, Encoding.UTF8, "application/json");
        // BAD: ignores the response entirely; no error handling.
        await http.PutAsync(BaseUrl + "/orders/" + orderId + "/status", content);
    }

    public async Task<string> GetRevenueReportAsync()
    {
        var http = new HttpClient();
        // BAD: no timeout, so the deliberately slow report can hang the caller forever.
        return await http.GetStringAsync(BaseUrl + "/reports/revenue");
    }
}
