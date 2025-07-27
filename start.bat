@echo off
REM Cross-platform startup script for Windows
REM Vehicle Price Prediction API

echo 🚗 Vehicle Price Prediction API - Windows Startup
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing/updating dependencies...
pip install -r requirements.txt

REM Start the application
echo 🚀 Starting Vehicle Price Prediction API...
python run_server.py

pause
