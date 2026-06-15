# Prompts — WPF desktop (`src/desktop/OrderManagement.Desktop`)

Copy-paste prompts for modernizing the WPF app (CommunityToolkit.Mvvm). Review diffs; run
`dotnet run --project src/desktop/OrderManagement.Desktop` (with the Python API running).

## Lab 01 — Upgrade to .NET 9
> Upgrade `src/desktop/OrderManagement.Desktop` from `net8.0-windows` to `net9.0-windows`.
> Update the `TargetFramework`, keep `CommunityToolkit.Mvvm`, fix any obsolete APIs, and
> rebuild until clean. Launch the app and confirm orders still load.

## Async MVVM — stop freezing the UI (Lab 03)
> Refactor `ViewModels/MainViewModel.cs` to be fully async. Convert the `[RelayCommand]`
> methods that call `.Result`/`.GetAwaiter().GetResult()` into **async relay commands**
> (`[RelayCommand] private async Task ...Async()` using `await`). Remove the blocking call
> from the constructor — load orders from a `Loaded`/async-init command instead. Ensure the
> window stays responsive while **Load Revenue Report** runs.

## HttpClient & services
> In `Services/ApiClient.cs`, stop newing up `HttpClient` per call and make the methods
> properly async with error handling (no empty catches). Register services and the
> `ApiClient` in DI (`Microsoft.Extensions.DependencyInjection`) and inject them into the
> view model instead of `new`-ing them. Read the API base URL from configuration.

## Get logic out of code-behind
> Move the CSV export from `MainWindow.xaml.cs` `ExportButton_Click` into an async
> `[RelayCommand]` on the view model bound from XAML. Use a `SaveFileDialog` (not a
> hard-coded `C:\temp` path), build the CSV with `StringBuilder`, and surface errors to the
> user instead of swallowing them.

## Security
> Replace the plaintext password `TextBox` with a `PasswordBox` and stop storing the
> password as an observable string. Don't deserialize or keep the `Password` field on the
> `Customer` model.

## Data model (Lab 02)
> Change money fields (`Order.Total`, `Product.Price`) from `double` to `decimal` and format
> currency for display with `StringFormat` in XAML bindings.

## Polish
> Update the `Orders` collection in place on refresh (e.g. diff/merge or `ObservableCollection`
> replacement via `CollectionViewSource`) instead of `Clear()`+`Add` in a loop. Add a busy
> indicator bound to the async commands' `IsRunning`.
