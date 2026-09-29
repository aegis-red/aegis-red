# One-script start for Windows: venv, install, portal + live demo SUT.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  py -3 -m venv .venv
} else {
  python -m venv .venv
}

$activate = Join-Path (Get-Location) ".venv\Scripts\Activate.ps1"
. $activate
python -m pip install -U pip
pip install -e ".[dev]"

Write-Host ""
Write-Host "Portal:     http://127.0.0.1:8080"
Write-Host "Live SUT:   http://127.0.0.1:8090/health"
Write-Host "UAT:        open Try now, add a seed, run it."
Write-Host ""
aegis-red try
