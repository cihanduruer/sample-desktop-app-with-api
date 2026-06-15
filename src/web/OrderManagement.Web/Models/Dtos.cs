using System.Text.Json.Serialization;

namespace OrderManagement.Web.Models;

public class OrderDto
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("customer_id")] public int CustomerId { get; set; }
    [JsonPropertyName("customer_name")] public string? CustomerName { get; set; }
    [JsonPropertyName("status")] public string? Status { get; set; }
    [JsonPropertyName("created_at")] public string? CreatedAt { get; set; }
    [JsonPropertyName("item_count")] public int ItemCount { get; set; }
    [JsonPropertyName("total")] public double Total { get; set; }

    // Filled in by the (intentionally inefficient) enrichment step.
    public string? CustomerEmail { get; set; }
}

public class CustomerDto
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("name")] public string? Name { get; set; }
    [JsonPropertyName("email")] public string? Email { get; set; }

    // BAD: we deserialize the plaintext password the API leaks.
    [JsonPropertyName("password")] public string? Password { get; set; }
}

public class ProductDto
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("name")] public string? Name { get; set; }
    [JsonPropertyName("price")] public double Price { get; set; }
    [JsonPropertyName("stock")] public int Stock { get; set; }
}
