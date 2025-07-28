#!/bin/bash
# Cross-platform startup script for Unix-like systems (macOS, Linux)
# Vehicle Price Prediction API

echo "🚗 Vehicle Price Prediction API - Unix Startup"
echo "=============================================="

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

echo "✅ Using Python: $PYTHON_CMD"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt venv/pyvenv.cfg ]; then
    echo "📥 Installing/updating dependencies..."
    pip install -r requirements.txt
fi

# Start the application
echo "🚀 Starting Vehicle Price Prediction API..."
echo "📍 Web Interface: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
$PYTHON_CMD run_app.py
