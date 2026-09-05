$ErrorActionPreference = "Stop"
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location "$taskRoot\backend"
& .\.venv\Scripts\python.exe -m pytest
& .\.venv\Scripts\python.exe -m ruff check app tests
& .\.venv\Scripts\python.exe -m mypy app
Set-Location "$taskRoot\frontend"
npm.cmd run build

