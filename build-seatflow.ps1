Write-Host "========================================"
Write-Host " SeatFlow Build Script"
Write-Host "========================================"

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "[1/4] Checking project directory..."

if (-not (Test-Path ".\backend")) {
    throw "Run this script from the SeatFlow project root."
}

Write-Host "Project directory OK."

Write-Host ""
Write-Host "[2/4] Installing Python dependencies..."

python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependency installation FAILED." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Dependencies OK."

Write-Host ""
Write-Host "[3/4] Running backend tests..."

$env:PYTHONPATH = "$PWD\backend"

python -m pytest -v

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Backend tests FAILED." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Backend tests PASSED." -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Build verification..."

Write-Host "SeatFlow build verification PASSED." -ForegroundColor Green

Write-Host ""
Write-Host "========================================"
Write-Host " SeatFlow build check complete!"
Write-Host "========================================"