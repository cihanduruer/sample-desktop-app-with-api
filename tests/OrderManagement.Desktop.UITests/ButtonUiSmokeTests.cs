using System;
using System.IO;
using System.Linq;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.UIA3;
using Xunit;
using Xunit.Abstractions;

namespace OrderManagement.Desktop.UITests;

/// <summary>
/// End-to-end UI smoke tests. These launch the real WPF executable and drive the actual
/// buttons through Windows UI Automation (FlaUI). They validate that:
///   1. the main window actually appears (regression guard for the startup deadlock that
///      caused "I can't see anything"), and
///   2. every button is present, enabled, and can be invoked without freezing or crashing
///      the app — even with the backend API offline.
///
/// A fresh app instance is launched per test (xUnit creates one instance per test) and is
/// always shut down in <see cref="Dispose"/>.
/// </summary>
public sealed class ButtonUiSmokeTests : IDisposable
{
    private static readonly string[] ButtonNames =
    {
        "Login", "Refresh Orders", "Update Status", "Load Revenue Report", "Export CSV"
    };

    private const string WindowTitle = "Order Management (Desktop)";

    private readonly ITestOutputHelper _output;
    private readonly Application _app;
    private readonly UIA3Automation _automation;
    private readonly Window _window;

    public ButtonUiSmokeTests(ITestOutputHelper output)
    {
        _output = output;

        var exePath = FindAppExecutable();
        _output.WriteLine($"Launching: {exePath}");

        _app = Application.Launch(exePath);
        _automation = new UIA3Automation();

        _window = _app.GetMainWindow(_automation, TimeSpan.FromSeconds(20))
            ?? throw new InvalidOperationException(
                "Main window did not appear within 20 seconds (the app may have failed to render).");
    }

    [Fact]
    public void MainWindow_Appears_WithExpectedTitle()
    {
        Assert.NotNull(_window);
        Assert.Equal(WindowTitle, _window.Title);
        Assert.False(_window.IsOffscreen, "Main window is off-screen.");
    }

    [Fact]
    public void AllButtons_ArePresentAndEnabled()
    {
        foreach (var name in ButtonNames)
        {
            var button = FindButton(name);
            Assert.True(button is not null, $"Button '{name}' was not found in the window.");
            Assert.True(button!.IsEnabled, $"Button '{name}' is disabled.");
            _output.WriteLine($"Found enabled button: '{name}'");
        }
    }

    [Fact]
    public void ClickingEveryButton_KeepsAppResponsive()
    {
        // Buttons that update status text only (no modal dialog), safe to click directly.
        InvokeButton("Refresh Orders");
        InvokeButton("Login");
        InvokeButton("Load Revenue Report");

        // "Update Status" with no selected order shows a "Pick an order first" message box.
        InvokeButton("Update Status");
        DismissDialogIfPresent();

        // "Export CSV" writes a file and shows an "Exported to..." message box.
        InvokeButton("Export CSV");
        DismissDialogIfPresent();

        Assert.False(_app.HasExited, "App exited unexpectedly after clicking the buttons.");

        var window = _app.GetMainWindow(_automation, TimeSpan.FromSeconds(5));
        Assert.NotNull(window);
        Assert.Equal(WindowTitle, window!.Title);
        _output.WriteLine("App is still responsive after clicking every button.");
    }

    private Button? FindButton(string name) =>
        _window.FindFirstDescendant(cf => cf.ByName(name))?.AsButton();

    private void InvokeButton(string name)
    {
        var button = FindButton(name);
        Assert.True(button is not null, $"Button '{name}' was not found in the window.");
        _output.WriteLine($"Invoking button: '{name}'");
        button!.Invoke(); // InvokePattern: reliable and does not depend on window focus.
        Thread.Sleep(400); // let the async command settle
    }

    private void DismissDialogIfPresent()
    {
        Window? dialog = null;
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(3);
        while (DateTime.UtcNow < deadline && dialog is null)
        {
            dialog = _window.ModalWindows.FirstOrDefault()
                     ?? _app.GetAllTopLevelWindows(_automation).FirstOrDefault(w => w.Title != WindowTitle);
            if (dialog is null)
            {
                Thread.Sleep(200);
            }
        }

        if (dialog is not null)
        {
            _output.WriteLine($"Dismissing dialog: '{dialog.Title}'");
            var okButton = dialog.FindFirstDescendant(cf => cf.ByControlType(ControlType.Button))?.AsButton();
            okButton?.Invoke();
            Thread.Sleep(250);
        }
    }

    private static string FindAppExecutable()
    {
        const string exeName = "OrderManagement.Desktop.exe";

        // 1) Same output folder (copied via ProjectReference).
        var local = Path.Combine(AppContext.BaseDirectory, exeName);
        if (File.Exists(local))
        {
            return local;
        }

        // 2) Walk up to the repo root and use the app project's build output.
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "OrderManagement.sln")))
        {
            dir = dir.Parent;
        }

        if (dir is not null)
        {
            var candidate = Path.Combine(
                dir.FullName, "src", "desktop", "OrderManagement.Desktop",
                "bin", "Debug", "net8.0-windows", exeName);
            if (File.Exists(candidate))
            {
                return candidate;
            }
        }

        throw new FileNotFoundException($"Could not locate {exeName}. Build the Desktop project first.");
    }

    public void Dispose()
    {
        try
        {
            if (!_app.HasExited)
            {
                _app.Close();
                Thread.Sleep(500);
            }
        }
        catch
        {
            // ignore shutdown errors
        }

        try
        {
            if (!_app.HasExited)
            {
                _app.Kill();
            }
        }
        catch
        {
            // ignore
        }

        _automation.Dispose();
        _app.Dispose();
    }
}
