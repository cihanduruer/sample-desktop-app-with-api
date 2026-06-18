using System.Collections.Generic;
using System.Threading.Tasks;
using OrderManagement.Desktop.Models;
using OrderManagement.Desktop.Services;

namespace OrderManagement.Desktop.Tests;

/// <summary>
/// In-memory <see cref="IApiClient"/> used by the button smoke tests. Returns canned data and
/// records how many times each endpoint was called, so tests run deterministically offline
/// (no dependency on the Python API at localhost:5001).
/// </summary>
internal sealed class FakeApiClient : IApiClient
{
    public string? Token { get; private set; }

    public int LoginCalls { get; private set; }
    public int GetOrdersCalls { get; private set; }
    public int GetProductsCalls { get; private set; }
    public int UpdateStatusCalls { get; private set; }
    public int RevenueCalls { get; private set; }

    public int? LastUpdatedOrderId { get; private set; }
    public string? LastUpdatedStatus { get; private set; }

    public List<Order> SeedOrders { get; } = new()
    {
        new Order { Id = 1, CustomerName = "Ada Lovelace", Status = "NEW", ItemCount = 2, Total = 42.50, CreatedAt = "2024-01-01" },
        new Order { Id = 2, CustomerName = "Grace Hopper", Status = "SHIPPED", ItemCount = 1, Total = 7.00, CreatedAt = "2024-01-02" },
    };

    public Task<List<Order>> GetOrdersAsync()
    {
        GetOrdersCalls++;
        return Task.FromResult(new List<Order>(SeedOrders));
    }

    public Task<List<Product>> GetProductsAsync()
    {
        GetProductsCalls++;
        return Task.FromResult(new List<Product>());
    }

    public Task<string> LoginAsync(string email, string password)
    {
        LoginCalls++;
        Token = "fake-token";
        return Task.FromResult("{\"token\":\"fake-token\"}");
    }

    public Task UpdateStatusAsync(int orderId, string status)
    {
        UpdateStatusCalls++;
        LastUpdatedOrderId = orderId;
        LastUpdatedStatus = status;
        return Task.CompletedTask;
    }

    public Task<string> GetRevenueReportAsync()
    {
        RevenueCalls++;
        return Task.FromResult("Total revenue: 49.50");
    }
}
