$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
$BackendDir = Join-Path $ProjectRoot "backend"
$VenvActivate = Join-Path $BackendDir ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $VenvActivate)) {
    Write-Error "Virtuelle Umgebung nicht gefunden: $VenvActivate"
}

Set-Location $BackendDir

. $VenvActivate

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
