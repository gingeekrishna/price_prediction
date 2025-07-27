"""
Startup script for Vehicle Price Prediction API
Run this from the project root directory
"""
import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['PYTHONPATH'] = str(project_root)

# Import and run the server
try:
    print(f"Starting server from: {project_root}")
    print("Loading modules...")
    
    import uvicorn
    from src.api import app
    
    print("✅ All modules loaded successfully!")
    print("🚀 Starting Vehicle Price Prediction API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation at: http://localhost:8000/docs")
    print("📊 Web Interface at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info",
        access_log=True
    )
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the project root directory")
    print("and all dependencies are installed.")
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
