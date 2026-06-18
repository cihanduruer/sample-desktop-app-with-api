using System.Collections.Generic;
using System.Threading.Tasks;
using OrderManagement.Desktop.Models;

namespace OrderManagement.Desktop.Services;

/// <summary>
/// Abstraction over the Order Management REST API. Extracted so the view model can be
/// unit/smoke-tested against a fake implementation instead of the live HTTP service.
/// </summary>
public interface IApiClient
{
    string? Token { get; }

    Task<List<Order>> GetOrdersAsync();

    Task<List<Product>> GetProductsAsync();

    Task<string> LoginAsync(string email, string password);

    Task UpdateStatusAsync(int orderId, string status);

    Task<string> GetRevenueReportAsync();
}
