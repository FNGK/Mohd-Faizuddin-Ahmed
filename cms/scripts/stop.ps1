# Stop CMS dev server on port 8780 (kills all listeners on that port).
$ErrorActionPreference = "SilentlyContinue"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$port = if ($env:CMS_PORT) { [int]$env:CMS_PORT } else { 8780 }

Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

python "$repo\cms\port_util.py" --free $port 2>$null

Start-Sleep -Milliseconds 500
$left = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($left) {
  Write-Host "Warning: port $port may still be in use." -ForegroundColor Yellow
} else {
  Write-Host "CMS stopped (port $port free)."
}
