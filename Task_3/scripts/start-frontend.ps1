$ErrorActionPreference = "Stop"
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location "$taskRoot\frontend"
npm.cmd run dev

