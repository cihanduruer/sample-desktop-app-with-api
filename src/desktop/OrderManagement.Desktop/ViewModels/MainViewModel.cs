using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
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
    private readonly IApiClient _api;

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

    /// <summary>
    /// Parameterless constructor used by XAML. Uses the real API client and kicks off the
    /// initial load WITHOUT blocking the UI thread so the window renders immediately.
    /// </summary>
    public MainViewModel() : this(new ApiClient())
    {
        // Fire-and-forget initial load (errors are handled inside LoadOrdersAsync).
        _ = LoadOrdersAsync();
    }

    /// <summary>
    /// Testable constructor that accepts any <see cref="IApiClient"/> implementation.
    /// Does NOT auto-load, so tests control exactly when API calls happen.
    /// </summary>
    public MainViewModel(IApiClient api)
    {
        _api = api;
    }

    [RelayCommand]
    private async Task LoginAsync()
    {
        try
        {
            // FIX: await keeps the UI thread free instead of blocking on .Result.
            var result = await _api.LoginAsync(Email, Password);
            StatusMessage = "Login response: " + result;
        }
        catch (Exception ex)
        {
            StatusMessage = "Login failed: " + ex.Message;
        }
    }

    [RelayCommand]
    private async Task LoadOrdersAsync()
    {
        try
        {
            StatusMessage = "Loading orders...";

            // FIX: await the async call so the UI thread is never blocked.
            var list = await _api.GetOrdersAsync();

            Orders.Clear();
            foreach (var o in list)
            {
                Orders.Add(o);
            }

            StatusMessage = "Loaded " + Orders.Count + " orders";
        }
        catch (Exception ex)
        {
            StatusMessage = "Failed to load orders: " + ex.Message;
        }
    }

    [RelayCommand]
    private async Task UpdateStatusAsync()
    {
        if (SelectedOrder == null)
        {
            MessageBox.Show("Pick an order first");
            return;
        }

        try
        {
            // FIX: await instead of blocking the UI thread.
            await _api.UpdateStatusAsync(SelectedOrder.Id, NewStatus);
            StatusMessage = "Order " + SelectedOrder.Id + " -> " + NewStatus;

            await LoadOrdersAsync();
        }
        catch (Exception ex)
        {
            StatusMessage = "Failed to update status: " + ex.Message;
        }
    }

    [RelayCommand]
    private async Task LoadRevenueReportAsync()
    {
        try
        {
            StatusMessage = "Loading revenue report...";

            // FIX: await the slow endpoint so the window stays responsive.
            RevenueReport = await _api.GetRevenueReportAsync();
            StatusMessage = "Revenue report loaded";
        }
        catch (Exception ex)
        {
            StatusMessage = "Failed to load revenue report: " + ex.Message;
        }
    }
}
