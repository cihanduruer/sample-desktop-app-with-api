using System;
using System.IO;
using System.Text;
using System.Windows;
using OrderManagement.Desktop.ViewModels;

namespace OrderManagement.Desktop;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    // ========================================================================
    // TEACHING ARTIFACT - business logic living in the code-behind.
    // This breaks MVVM: the export feature should be a command on the view model,
    // it builds a CSV with string concatenation in a loop, writes synchronously to
    // a hard-coded path, and swallows errors.
    // ========================================================================
    private void ExportButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var vm = (MainViewModel)DataContext;

            // BAD: string concatenation in a loop instead of StringBuilder/CSV writer.
            var csv = "Id,Customer,Status,Items,Total,Created\n";
            foreach (var o in vm.Orders)
            {
                csv = csv + o.Id + "," + o.CustomerName + "," + o.Status + ","
                    + o.ItemCount + "," + o.Total + "," + o.CreatedAt + "\n";
            }

            // BAD: hard-coded path on the C: drive; synchronous write on the UI thread.
            var path = "C:\\temp\\orders_export.csv";
            Directory.CreateDirectory("C:\\temp");
            File.WriteAllText(path, csv, Encoding.UTF8);

            MessageBox.Show("Exported to " + path);
        }
        catch
        {
            // BAD: empty catch hides any failure from the user.
        }
    }
}
