# Start CMS (stops any existing listener on 8780 first).
$ErrorActionPreference = "Stop"
$repo = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repo

& (Join-Path $PSScriptRoot "stop.ps1")

$env:CMS_PORT = if ($env:CMS_PORT) { $env:CMS_PORT } else { "8780" }
Write-Host "Starting CMS at http://127.0.0.1:$env:CMS_PORT/admin/" -ForegroundColor Cyan
python cms/run.py
