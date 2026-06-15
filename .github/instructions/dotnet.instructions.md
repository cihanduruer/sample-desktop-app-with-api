---
applyTo: "**/*.cs"
---

# Instructions for C# (.NET 8 BFF + WPF desktop)

- **Async all the way.** Never block with `.Result` or `.GetAwaiter().GetResult()`.
  Handlers, commands and services should be `async Task` and use `await`.
- **HttpClient:** use `IHttpClientFactory` / typed clients registered in DI. Never
  `new HttpClient()` per call.
- **Money is `decimal`,** never `double`.
- **WPF/MVVM:** keep logic in the view model, not code-behind. Long-running work must not
  run on the UI thread; use async commands (`[RelayCommand]` async) so the window stays
  responsive. Use `PasswordBox`/`SecureString` patterns, not plaintext string passwords.
- **Secrets** come from configuration/user-secrets/environment — not constants or
  `appsettings.json` committed to git.
- **Errors:** don't swallow exceptions; log with structured logging and surface friendly
  messages. Never log credentials.
- Prefer dictionary lookups/joins over nested-loop (O(n²)) joins; add caching where it
  is safe.
