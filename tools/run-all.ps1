<#
  run-all.ps1
  Convenience launcher for the Order Management demo.
  Starts the Python API (5001) and the .NET BFF (5080), each in its own window.
  The WPF desktop app and the React dev server are started separately (see docs).

  Usage:
    pwsh tools/run-all.ps1            # start API + BFF
    pwsh tools/run-all.ps1 -WithWeb   # also start the React dev server (5173)
#>
param(
  [switch]$WithWeb
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$api  = Join-Path $repo "src\api"
$bff  = Join-Path $repo "src\web\OrderManagement.Web"
$ca   = Join-Path $bff  "ClientApp"

Write-Host "Repo: $repo" -ForegroundColor Cyan

# --- Python API -------------------------------------------------------------
$venvPy = Join-Path $api ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
  Write-Host "Creating Python venv + installing requirements..." -ForegroundColor Yellow
  python -m venv (Join-Path $api ".venv")
  & $venvPy -m pip install -r (Join-Path $api "requirements.txt")
}
Write-Host "Starting Python API on http://localhost:5001 ..." -ForegroundColor Green
Start-Process -FilePath "pwsh" -ArgumentList @(
  "-NoExit", "-Command",
  "Set-Location '$api'; & '$venvPy' app.py"
)

# --- .NET BFF ---------------------------------------------------------------
Write-Host "Starting .NET BFF on http://localhost:5080 (Swagger at /swagger) ..." -ForegroundColor Green
Start-Process -FilePath "pwsh" -ArgumentList @(
  "-NoExit", "-Command",
  "Set-Location '$bff'; dotnet run"
)

# --- React dev server (optional) -------------------------------------------
if ($WithWeb) {
  if (-not (Test-Path (Join-Path $ca "node_modules"))) {
    Write-Host "Installing React dependencies..." -ForegroundColor Yellow
    Start-Process -FilePath "pwsh" -ArgumentList @(
      "-NoExit", "-Command",
      "Set-Location '$ca'; npm install; npm run dev"
    )
  } else {
    Write-Host "Starting React dev server on http://localhost:5173 ..." -ForegroundColor Green
    Start-Process -FilePath "pwsh" -ArgumentList @(
      "-NoExit", "-Command",
      "Set-Location '$ca'; npm run dev"
    )
  }
}

Write-Host ""
Write-Host "Started. URLs:" -ForegroundColor Cyan
Write-Host "  Python API : http://localhost:5001/health"
Write-Host "  .NET BFF   : http://localhost:5080/swagger"
if ($WithWeb) { Write-Host "  React UI   : http://localhost:5173" }
Write-Host ""
Write-Host "Run the WPF desktop app with:  dotnet run --project src/desktop/OrderManagement.Desktop"
