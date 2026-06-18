using System.Collections.Generic;
using System.Globalization;
using System.Text;
using OrderManagement.Desktop.Models;

namespace OrderManagement.Desktop.Services;

/// <summary>
/// Builds CSV text for a set of orders. Extracted from the MainWindow code-behind so the
/// export logic can be unit-tested without a UI, a file system, or a message box.
/// </summary>
public static class OrderCsvExporter
{
    public const string Header = "Id,Customer,Status,Items,Total,Created";

    public static string BuildCsv(IEnumerable<Order> orders)
    {
        var sb = new StringBuilder();
        sb.Append(Header).Append('\n');

        foreach (var o in orders)
        {
            sb.Append(o.Id).Append(',')
              .Append(Escape(o.CustomerName)).Append(',')
              .Append(Escape(o.Status)).Append(',')
              .Append(o.ItemCount).Append(',')
              .Append(o.Total.ToString(CultureInfo.InvariantCulture)).Append(',')
              .Append(Escape(o.CreatedAt)).Append('\n');
        }

        return sb.ToString();
    }

    // Minimal CSV field escaping: quote fields containing a comma, quote, or newline.
    private static string Escape(string? value)
    {
        if (string.IsNullOrEmpty(value))
        {
            return string.Empty;
        }

        if (value.Contains(',') || value.Contains('"') || value.Contains('\n') || value.Contains('\r'))
        {
            return "\"" + value.Replace("\"", "\"\"") + "\"";
        }

        return value;
    }
}
