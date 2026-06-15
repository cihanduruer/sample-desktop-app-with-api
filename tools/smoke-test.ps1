<#
  smoke-test.ps1
  Hits the running services and prints a quick pass/fail. Assumes:
    Python API on :5001 and .NET BFF on :5080 are already running.
#>
function Test-Url($name, $url, $method = "GET", $body = $null) {
  try {
    if ($body) {
      $r = Invoke-WebRequest -UseBasicParsing -Method $method -ContentType "application/json" -Body $body $url -TimeoutSec 30
    } else {
      $r = Invoke-WebRequest -UseBasicParsing -Method $method $url -TimeoutSec 30
    }
    Write-Host ("PASS  {0,-28} HTTP {1}" -f $name, $r.StatusCode) -ForegroundColor Green
  } catch {
    Write-Host ("FAIL  {0,-28} {1}" -f $name, $_.Exception.Message) -ForegroundColor Red
  }
}

Test-Url "API /health"        "http://localhost:5001/health"
Test-Url "API /orders"        "http://localhost:5001/orders"
Test-Url "BFF /api/products"  "http://localhost:5080/api/products"
Test-Url "BFF /api/orders"    "http://localhost:5080/api/orders"
Test-Url "BFF /api/dashboard" "http://localhost:5080/api/dashboard"
Test-Url "BFF /api/login"     "http://localhost:5080/api/login" "POST" '{"Email":"alice@example.com","Password":"password123"}'
