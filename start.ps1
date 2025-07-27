# Cross-platform startup script for Windows PowerShell
# Vehicle Price Prediction API

Write-Host "🚗 Vehicle Price Prediction API - PowerShell Startup" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing/updating dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

# Start the application
Write-Host "🚀 Starting Vehicle Price Prediction API..." -ForegroundColor Green
python run_server.py

Read-Host "Press Enter to exit"
