$ErrorActionPreference = "Stop"
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location $taskRoot
if (-not (Test-Path "backend\.venv")) { python -m venv backend\.venv }
& backend\.venv\Scripts\python.exe -m pip install --upgrade pip
& backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
if (-not (Test-Path "frontend\.env")) { Copy-Item "frontend\.env.example" "frontend\.env" }
Push-Location frontend
npm.cmd install
Pop-Location
Write-Host "Setup complete. Run .\scripts\start-backend.ps1 and .\scripts\start-frontend.ps1 in separate terminals."

