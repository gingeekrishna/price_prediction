#!/usr/bin/env python3
"""
Cross-platform startup script for Vehicle Price Prediction API
Compatible with Windows, macOS, and Linux
"""
import sys
import os
from pathlib import Path
import platform

def setup_environment():
    """Setup the Python path and environment for cross-platform compatibility."""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(project_root)
    
    return project_root

def main():
    """Main entry point for the application."""
    project_root = setup_environment()
    
    print("🚗 Vehicle Price Prediction API")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Project Root: {project_root}")
    print("=" * 50)
    
    try:
        print("📦 Loading modules...")
        import uvicorn
        from src.api import app
        
        print("✅ All modules loaded successfully!")
        print("🚀 Starting Vehicle Price Prediction API Server...")
        print("")
        print("📍 Server endpoints:")
        print("   • Web Interface: http://localhost:8000")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Health Check: http://localhost:8000/health")
        print("")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            access_log=True,
            reload=False  # Set to True for development
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Solutions:")
        print("   1. Ensure you're in the project root directory")
        print("   2. Activate virtual environment:")
        if platform.system() == "Windows":
            print("      .\\venv\\Scripts\\activate")
        else:
            print("      source venv/bin/activate")
        print("   3. Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
