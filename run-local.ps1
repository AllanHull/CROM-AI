# CROM Local Development Startup Script
# This script sets up and runs the CROM web app locally for development

param(
    [switch]$Fresh = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host @"
CROM Local Development Startup Script

Usage: .\run-local.ps1 [options]

Options:
    -Fresh      : Remove and recreate virtual environment
    -Help       : Show this help message

Examples:
    .\run-local.ps1              # Run with existing venv
    .\run-local.ps1 -Fresh       # Create fresh venv and run
"@
    exit 0
}

$ErrorActionPreference = "Stop"

# Colors
$SuccessColor = "Green"
$ErrorColor = "Red"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

Write-Host "CROM Local Development Environment" -ForegroundColor $InfoColor
Write-Host "===================================" -ForegroundColor $InfoColor

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor $InfoColor
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor $SuccessColor
} catch {
    Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor $ErrorColor
    exit 1
}

# Virtual environment path
$venvPath = ".\venv"
$venvActivate = "$venvPath\Scripts\Activate.ps1"

# Handle virtual environment
if ($Fresh -and (Test-Path $venvPath)) {
    Write-Host "Removing existing virtual environment..." -ForegroundColor $WarningColor
    Remove-Item -Recurse -Force $venvPath
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor $InfoColor
    python -m venv $venvPath
    Write-Host "✓ Virtual environment created" -ForegroundColor $SuccessColor
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor $InfoColor
& $venvActivate

# Install/upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor $InfoColor
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor $InfoColor
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt --quiet
    Write-Host "✓ Dependencies installed" -ForegroundColor $SuccessColor
} else {
    Write-Host "✗ requirements.txt not found" -ForegroundColor $ErrorColor
    exit 1
}

# Check for .env file
Write-Host "`nConfiguring environment..." -ForegroundColor $InfoColor
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Creating .env from .env.example..." -ForegroundColor $WarningColor
        Copy-Item ".env.example" ".env"
        Write-Host "⚠ Please update .env with your Azure credentials" -ForegroundColor $WarningColor
    } else {
        Write-Host "⚠ .env file not found. Create one with required Azure credentials" -ForegroundColor $WarningColor
    }
} else {
    Write-Host "✓ .env file found" -ForegroundColor $SuccessColor
}

# Display startup information
Write-Host "`n" -ForegroundColor $InfoColor
Write-Host "========================================" -ForegroundColor $InfoColor
Write-Host "Starting CROM Flask Application" -ForegroundColor $SuccessColor
Write-Host "========================================" -ForegroundColor $InfoColor
Write-Host "Local URL: http://localhost:5000" -ForegroundColor $InfoColor
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor $InfoColor
Write-Host "`nEndpoints:" -ForegroundColor $InfoColor
Write-Host "  GET  http://localhost:5000/                 (Welcome page)" -ForegroundColor $InfoColor
Write-Host "  GET  http://localhost:5000/health           (Health check)" -ForegroundColor $InfoColor
Write-Host "  POST http://localhost:5000/api/call-logic-app (Call Logic App)" -ForegroundColor $InfoColor
Write-Host "  GET  http://localhost:5000/api/blobs        (List blobs)" -ForegroundColor $InfoColor
Write-Host "`n" -ForegroundColor $InfoColor

# Run the Flask application
$env:FLASK_ENV = "development"
python app.py
