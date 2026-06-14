using System.Net.Http;
using System.Text;
using System.Text.Json;

namespace OrderManagement.Web.Services;

// ============================================================================
// TEACHING ARTIFACT - intentionally bad HTTP client for the Python API.
// Planted problems:
//   * A new HttpClient is allocated on every call (socket exhaustion under load).
//   * Every method is SYNCHRONOUS and blocks on async with .Result / .GetResult()
//     -> thread-pool starvation, the #1 thing to find with dotnet-trace.
//   * The base URL and a fake API key are hard-coded.
//   * No timeouts, no cancellation tokens, no error handling.
// ============================================================================
public class PythonApiClient
{
    // BAD: hard-coded downstream URL + secret in source.
    private const string BaseUrl = "http://localhost:5001";
    private const string ApiKey = "supersecret-api-key-123";

    public string GetOrdersJson()
    {
        // BAD: new HttpClient per call.
        var http = new HttpClient();
        http.DefaultRequestHeaders.Add("X-Api-Key", ApiKey);
        // BAD: .Result blocks a thread-pool thread on async I/O.
        return http.GetStringAsync(BaseUrl + "/orders").Result;
    }

    public string GetProductsJson()
    {
        var http = new HttpClient();
        return http.GetStringAsync(BaseUrl + "/products").Result;
    }

    public string GetCustomersJson()
    {
        var http = new HttpClient();
        return http.GetStringAsync(BaseUrl + "/customers").Result;
    }

    public string GetRevenueReportJson()
    {
        var http = new HttpClient();
        // BAD: no timeout, blocks on the deliberately slow report.
        return http.GetStringAsync(BaseUrl + "/reports/revenue").Result;
    }

    public string Login(string email, string password)
    {
        var http = new HttpClient();
        var body = "{\"email\":\"" + email + "\",\"password\":\"" + password + "\"}";
        var content = new StringContent(body, Encoding.UTF8, "application/json");
        // BAD: .Result on PostAsync, then .Result again on ReadAsStringAsync.
        var resp = http.PostAsync(BaseUrl + "/login", content).Result;
        return resp.Content.ReadAsStringAsync().Result;
    }

    public string UpdateStatus(int orderId, string status)
    {
        var http = new HttpClient();
        var body = "{\"status\":\"" + status + "\"}";
        var content = new StringContent(body, Encoding.UTF8, "application/json");
        var resp = http.PutAsync(BaseUrl + "/orders/" + orderId + "/status", content).Result;
        return resp.Content.ReadAsStringAsync().Result;
    }
}
