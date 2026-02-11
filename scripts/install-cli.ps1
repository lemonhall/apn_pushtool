$ErrorActionPreference = "Stop"

Write-Host "Installing apn-pushtool CLI as a global command via uv tool..." -ForegroundColor Cyan

uv tool install -e . --force
uv tool update-shell

Write-Host ""
Write-Host "Done. Re-open your terminal, then run:" -ForegroundColor Green
Write-Host "  apn-pushtool --help"
