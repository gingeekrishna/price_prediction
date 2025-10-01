#!/usr/bin/env python3
"""
Simple script to run the Vehicle Price Prediction application locally
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['USE_OLLAMA'] = 'true'
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
os.environ['DEBUG'] = 'true'

try:
    import uvicorn
    from app.api.main import app
    
    print("🚀 Starting Vehicle Price Prediction Application...")
    print("📍 URL: http://localhost:8003")
    print("📖 API Docs: http://localhost:8003/docs")
    print("❤️  Health Check: http://localhost:8003/health")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8003,
        log_level="info",
        reload=False
    )
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)
