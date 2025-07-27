#!/usr/bin/env python3
"""
Startup script for the Vehicle Price Prediction API
"""
import sys
import os
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    # Set environment variable for Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    # Start uvicorn with the correct environment
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "src.api:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ], env=env)
