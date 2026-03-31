# Shimeji Mascot Launcher for Windows (PowerShell)
# Detects environment and runs with appropriate settings

$ErrorActionPreference = "Stop"

# Change to script directory
Set-Location -Path $PSScriptRoot

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check PyQt6
Write-Host "Checking PyQt6..." -ForegroundColor Cyan
python -c "import PyQt6" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyQt6 not found. Installing..." -ForegroundColor Yellow
    pip install PyQt6
} else {
    Write-Host "PyQt6 is installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "   Starting Shimeji Mascot" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "- Left click and drag to move the mascot"
Write-Host "- Right click for menu options"
Write-Host "- Press Ctrl+C in this window to stop"
Write-Host ""

# Run the mascot
python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error occurred while running Shimeji (Exit code: $LASTEXITCODE)" -ForegroundColor Red
    Write-Host ""
    pause
}
