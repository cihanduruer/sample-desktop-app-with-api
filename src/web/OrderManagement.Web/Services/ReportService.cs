using System.Text;
using System.Text.Json;
using OrderManagement.Web.Models;

namespace OrderManagement.Web.Services;

// ============================================================================
// TEACHING ARTIFACT - the perf hotspot for the dotnet-trace exercise.
// Planted problems:
//   * O(n*m) nested-loop "join" of orders to customers instead of a dictionary.
//   * Re-parses JSON repeatedly and re-fetches downstream data per call.
//   * Blocking Thread.Sleep on the request path.
//   * CPU-bound busy work (string concatenation + a naive prime sieve) so the
//     trace shows an obvious hot method.
//   * No caching whatsoever.
// ============================================================================
public class ReportService
{
    private readonly PythonApiClient _api;

    public ReportService(PythonApiClient api)
    {
        _api = api;
    }

    // Enriches every order with the customer email using a quadratic scan.
    public List<OrderDto> GetEnrichedOrders()
    {
        var orders = JsonSerializer.Deserialize<List<OrderDto>>(_api.GetOrdersJson()) ?? new();
        var customers = JsonSerializer.Deserialize<List<CustomerDto>>(_api.GetCustomersJson()) ?? new();

        // BAD: O(orders * customers). A Dictionary lookup would be O(1).
        foreach (var o in orders)
        {
            foreach (var c in customers)
            {
                if (c.Id == o.CustomerId)
                {
                    o.CustomerEmail = c.Email;
                }
            }
        }

        return orders;
    }

    // Builds an HTML-ish dashboard string the slow way.
    public string BuildDashboardHtml()
    {
        // BAD: artificial latency on the hot path.
        Thread.Sleep(250);

        var orders = GetEnrichedOrders();

        // BAD: string concatenation in a loop instead of StringBuilder.
        var html = "<h1>Order Dashboard</h1><ul>";
        foreach (var o in orders)
        {
            html = html + "<li>#" + o.Id + " " + o.CustomerName + " (" + o.CustomerEmail
                + ") - " + o.Status + " - $" + o.Total + "</li>";
        }
        html = html + "</ul>";

        // BAD: pointless CPU burn so the profiler has an obvious hotspot.
        html = html + "<p>checksum=" + ComputeExpensiveChecksum(orders.Count) + "</p>";
        return html;
    }

    // Naive, deliberately wasteful CPU work.
    private long ComputeExpensiveChecksum(int seed)
    {
        long acc = 0;
        var limit = 80_000; // bounded so the demo endpoint stays ~1s, not minutes
        for (int n = 2; n < limit; n++)
        {
            bool isPrime = true;
            // BAD: trial division to n instead of sqrt(n); recomputed every call.
            for (int d = 2; d < n; d++)
            {
                if (n % d == 0)
                {
                    isPrime = false;
                    break;
                }
            }
            if (isPrime)
            {
                acc += n;
            }
        }
        return acc;
    }
}
