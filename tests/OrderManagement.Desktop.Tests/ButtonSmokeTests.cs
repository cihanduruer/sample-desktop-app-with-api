using System;
using System.Linq;
using System.Threading.Tasks;
using OrderManagement.Desktop.Models;
using OrderManagement.Desktop.Services;
using OrderManagement.Desktop.ViewModels;
using Xunit;

namespace OrderManagement.Desktop.Tests;

/// <summary>
/// Smoke tests for every button in MainWindow. Each test exercises the command (or, for the
/// code-behind Export button, the underlying CSV builder) and asserts the action completes
/// without throwing and produces a sensible result. The view model is fed a <see cref="FakeApiClient"/>
/// so the tests are deterministic and do not require the live API.
///
/// Button -> what is exercised:
///   Login              -> LoginCommand
///   Refresh Orders     -> LoadOrdersCommand
///   Update Status      -> UpdateStatusCommand
///   Load Revenue Report-> LoadRevenueReportCommand
///   Export CSV         -> OrderCsvExporter.BuildCsv (the testable core of ExportButton_Click)
/// </summary>
public class ButtonSmokeTests
{
    private static MainViewModel CreateViewModel(out FakeApiClient api)
    {
        api = new FakeApiClient();
        return new MainViewModel(api);
    }

    [Fact]
    public async Task LoginButton_CallsApi_AndReportsResult()
    {
        var vm = CreateViewModel(out var api);

        await vm.LoginCommand.ExecuteAsync(null);

        Assert.Equal(1, api.LoginCalls);
        Assert.Contains("Login response", vm.StatusMessage);
    }

    [Fact]
    public async Task RefreshOrdersButton_LoadsOrdersIntoGrid()
    {
        var vm = CreateViewModel(out var api);

        await vm.LoadOrdersCommand.ExecuteAsync(null);

        Assert.Equal(1, api.GetOrdersCalls);
        Assert.Equal(2, vm.Orders.Count);
        Assert.Contains("Loaded 2 orders", vm.StatusMessage);
    }

    [Fact]
    public async Task UpdateStatusButton_WithSelection_UpdatesAndReloads()
    {
        var vm = CreateViewModel(out var api);
        await vm.LoadOrdersCommand.ExecuteAsync(null);
        vm.SelectedOrder = vm.Orders.First();
        vm.NewStatus = "SHIPPED";

        await vm.UpdateStatusCommand.ExecuteAsync(null);

        Assert.Equal(1, api.UpdateStatusCalls);
        Assert.Equal(vm.SelectedOrder!.Id, api.LastUpdatedOrderId);
        Assert.Equal("SHIPPED", api.LastUpdatedStatus);
        // After a successful update the command reloads the grid, so the final
        // StatusMessage reflects the reload rather than the intermediate update text.
        Assert.Equal(2, vm.Orders.Count);
        Assert.Contains("Loaded", vm.StatusMessage);
    }

    [Fact]
    public async Task LoadRevenueReportButton_PopulatesReport()
    {
        var vm = CreateViewModel(out var api);

        await vm.LoadRevenueReportCommand.ExecuteAsync(null);

        Assert.Equal(1, api.RevenueCalls);
        Assert.False(string.IsNullOrWhiteSpace(vm.RevenueReport));
        Assert.Contains("Revenue report loaded", vm.StatusMessage);
    }

    [Fact]
    public void ExportCsvButton_BuildsCsvWithHeaderAndEscapedRows()
    {
        var orders = new[]
        {
            new Order { Id = 1, CustomerName = "Ada", Status = "NEW", ItemCount = 2, Total = 9.99, CreatedAt = "2024-01-01" },
            new Order { Id = 2, CustomerName = "Grace, Jr.", Status = "SHIPPED", ItemCount = 1, Total = 5, CreatedAt = "2024-01-02" },
        };

        var csv = OrderCsvExporter.BuildCsv(orders);
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);

        Assert.Equal(OrderCsvExporter.Header, lines[0]);
        Assert.Equal(3, lines.Length); // header + 2 rows
        Assert.Contains("1,Ada,NEW,2,9.99,2024-01-01", csv);
        Assert.Contains("\"Grace, Jr.\"", csv); // comma-containing field is quoted
    }

    [Fact]
    public void AllCommandButtons_AreExecutable()
    {
        var vm = CreateViewModel(out _);

        Assert.True(vm.LoginCommand.CanExecute(null));
        Assert.True(vm.LoadOrdersCommand.CanExecute(null));
        Assert.True(vm.UpdateStatusCommand.CanExecute(null));
        Assert.True(vm.LoadRevenueReportCommand.CanExecute(null));
    }
}
