using System.Text.Json.Serialization;

namespace OrderManagement.Desktop.Models;

// Teaching artifact: anemic DTOs with public setters everywhere and double money.
public class Customer
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("name")] public string? Name { get; set; }
    [JsonPropertyName("email")] public string? Email { get; set; }

    // BAD: the API returns the plaintext password and we happily deserialize it.
    [JsonPropertyName("password")] public string? Password { get; set; }
}

public class Product
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("name")] public string? Name { get; set; }
    [JsonPropertyName("price")] public double Price { get; set; }
    [JsonPropertyName("stock")] public int Stock { get; set; }
}

public class Order
{
    [JsonPropertyName("id")] public int Id { get; set; }
    [JsonPropertyName("customer_id")] public int CustomerId { get; set; }
    [JsonPropertyName("customer_name")] public string? CustomerName { get; set; }
    [JsonPropertyName("status")] public string? Status { get; set; }
    [JsonPropertyName("created_at")] public string? CreatedAt { get; set; }
    [JsonPropertyName("item_count")] public int ItemCount { get; set; }

    // BAD: money as double.
    [JsonPropertyName("total")] public double Total { get; set; }
}
