using System;
using System.Collections.ObjectModel;
using System.Windows;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using OrderManagement.Desktop.Models;
using OrderManagement.Desktop.Services;

namespace OrderManagement.Desktop.ViewModels;

// ============================================================================
// TEACHING ARTIFACT - a "god" view model.
// It uses CommunityToolkit.Mvvm ([ObservableProperty]/[RelayCommand]) but then
// throws away most of the benefit:
//   * Commands are SYNCHRONOUS and call .Result / .GetAwaiter().GetResult() on
//     async work, which blocks and FREEZES the UI thread.
//   * The constructor does network I/O (blocking) before the window can render.
//   * The ObservableCollection is fully rebuilt on every refresh.
//   * The plaintext password lives on the view model as an observable property.
//   * Business logic, formatting and error handling are all crammed in here.
// ============================================================================
public partial class MainViewModel : ObservableObject
{
    private readonly ApiClient _api = new ApiClient();

    [ObservableProperty]
    private ObservableCollection<Order> _orders = new();

    [ObservableProperty]
    private Order? _selectedOrder;

    [ObservableProperty]
    private string _email = "admin@example.com";

    // BAD: plaintext password bound straight to the UI and kept in memory.
    [ObservableProperty]
    private string _password = "admin";

    [ObservableProperty]
    private string _statusMessage = "Ready";

    [ObservableProperty]
    private string _newStatus = "SHIPPED";

    [ObservableProperty]
    private string _revenueReport = "";

    public MainViewModel()
    {
        // BAD: blocking network call in the constructor. If the API is down or slow
        // the app hangs before it ever paints.
        LoadOrders();
    }

    [RelayCommand]
    private void Login()
    {
        try
        {
            // BAD: .Result blocks the UI thread on async I/O (deadlock risk + freeze).
            var result = _api.LoginAsync(Email, Password).Result;
            StatusMessage = "Login response: " + result;
        }
        catch (Exception ex)
        {
            // BAD: shows raw exception text to the user.
            StatusMessage = "Login failed: " + ex.Message;
        }
    }

    [RelayCommand]
    private void LoadOrders()
    {
        StatusMessage = "Loading orders...";

        // BAD: .GetAwaiter().GetResult() blocks the UI thread.
        var list = _api.GetOrdersAsync().GetAwaiter().GetResult();

        // BAD: clear + re-add in a loop rebuilds the whole grid and fires N change
        // notifications instead of updating in place.
        Orders.Clear();
        foreach (var o in list)
        {
            Orders.Add(o);
        }

        StatusMessage = "Loaded " + Orders.Count + " orders";
    }

    [RelayCommand]
    private void UpdateStatus()
    {
        if (SelectedOrder == null)
        {
            // BAD: blocking modal dialog from the view model (UI concern leaking in).
            MessageBox.Show("Pick an order first");
            return;
        }

        // BAD: blocks the UI thread again.
        _api.UpdateStatusAsync(SelectedOrder.Id, NewStatus).GetAwaiter().GetResult();
        StatusMessage = "Order " + SelectedOrder.Id + " -> " + NewStatus;

        // BAD: full reload after every single status change.
        LoadOrders();
    }

    [RelayCommand]
    private void LoadRevenueReport()
    {
        StatusMessage = "Crunching revenue report (this will freeze the window)...";

        // BAD: calls the deliberately slow endpoint synchronously on the UI thread,
        // so the entire window becomes unresponsive until it returns.
        RevenueReport = _api.GetRevenueReportAsync().GetAwaiter().GetResult();
        StatusMessage = "Revenue report loaded";
    }
}
