#!/usr/bin/env python3
"""
Performance Analysis Tool for Vehicle Price Prediction System
"""

import sys
import os
import time
import requests
import asyncio
import json
from datetime import datetime

sys.path.append(os.path.abspath('.'))

def measure_time(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"⏱️  {func.__name__} took: {execution_time:.3f} seconds")
        return result, execution_time
    return wrapper

@measure_time
def test_api_prediction():
    """Test API prediction speed."""
    try:
        response = requests.post(
            'http://localhost:8000/predict',
            json={
                'make': 'Toyota',
                'model': 'Camry', 
                'year': 2020,
                'mileage': 30000,
                'condition': 'good'
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": str(e)}

@measure_time
def test_model_loading():
    """Test model loading speed."""
    try:
        from src.model import VehiclePriceModel
        model = VehiclePriceModel()
        return {"status": "Model loaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@measure_time
def test_data_loading():
    """Test data loading speed."""
    try:
        from src.data_loader import VehicleDataLoader
        loader = VehicleDataLoader()
        data = loader.load_and_merge_data()
        return {"rows": len(data), "columns": len(data.columns) if hasattr(data, 'columns') else 0}
    except Exception as e:
        return {"error": str(e)}

@measure_time
def test_ollama_agent():
    """Test Ollama agent speed."""
    try:
        from src.agents.ollama_agent import OllamaAgent
        agent = OllamaAgent()
        if not agent.available:
            return {"error": "Ollama not available"}
        
        vehicle_data = {"make": "Toyota", "model": "Camry", "year": 2020, "mileage": 30000}
        market_data = {"avg_price": 24000, "trend": "stable"}
        explanation = agent.generate_explanation(vehicle_data, market_data, 25000.0)
        return {"explanation_length": len(explanation), "available": True}
    except Exception as e:
        return {"error": str(e)}

@measure_time
def test_claude_agent():
    """Test Claude agent speed."""
    try:
        from src.agents.claude_agent import ClaudeAgent
        agent = ClaudeAgent()
        if not agent.available:
            return {"error": "Claude not available - check ANTHROPIC_API_KEY"}
        
        vehicle_data = {"make": "Toyota", "model": "Camry", "year": 2020, "mileage": 30000}
        market_data = {"avg_price": 24000, "trend": "stable"}
        explanation = agent.generate_explanation(vehicle_data, market_data, 25000.0)
        return {"explanation_length": len(explanation), "available": True}
    except Exception as e:
        return {"error": str(e)}

@measure_time
def test_database_operations():
    """Test database read/write speed."""
    try:
        import sqlite3
        
        # Test connection
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        
        # Test write
        cursor.execute('''
            INSERT OR REPLACE INTO predictions 
            (id, vehicle_data, predicted_price, explanation, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', ('perf_test', '{"test": true}', 25000.0, 'Performance test', datetime.now().isoformat()))
        
        # Test read
        cursor.execute('SELECT * FROM predictions WHERE id = ?', ('perf_test',))
        result = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        return {"database_operations": "successful", "record_found": result is not None}
    except Exception as e:
        return {"error": str(e)}

def analyze_bottlenecks():
    """Analyze system bottlenecks and provide recommendations."""
    print("🔍 Vehicle Price Prediction Performance Analysis")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    bottlenecks = []
    total_time = 0
    
    # Test 1: Data Loading
    print("1️⃣  Testing Data Loading...")
    result, exec_time = test_data_loading()
    total_time += exec_time
    print(f"   Result: {result}")
    if exec_time > 2.0:
        bottlenecks.append(f"Data loading is slow ({exec_time:.3f}s)")
    print()
    
    # Test 2: Model Loading
    print("2️⃣  Testing Model Loading...")
    result, exec_time = test_model_loading()
    total_time += exec_time
    print(f"   Result: {result}")
    if exec_time > 1.0:
        bottlenecks.append(f"Model loading is slow ({exec_time:.3f}s)")
    print()
    
    # Test 3: Database Operations
    print("3️⃣  Testing Database Operations...")
    result, exec_time = test_database_operations()
    total_time += exec_time
    print(f"   Result: {result}")
    if exec_time > 0.5:
        bottlenecks.append(f"Database operations are slow ({exec_time:.3f}s)")
    print()
    
    # Test 4: Ollama Agent
    print("4️⃣  Testing Ollama Agent...")
    result, exec_time = test_ollama_agent()
    total_time += exec_time
    print(f"   Result: {result}")
    if exec_time > 5.0:
        bottlenecks.append(f"Ollama agent is slow ({exec_time:.3f}s)")
    print()
    
    # Test 5: Claude Agent
    print("5️⃣  Testing Claude Agent...")
    result, exec_time = test_claude_agent()
    total_time += exec_time
    print(f"   Result: {result}")
    if exec_time > 5.0:
        bottlenecks.append(f"Claude agent is slow ({exec_time:.3f}s)")
    print()
    
    # Test 6: Full API Request
    print("6️⃣  Testing Full API Request...")
    result, exec_time = test_api_prediction()
    total_time += exec_time
    print(f"   Result: {result}")
    if exec_time > 10.0:
        bottlenecks.append(f"API request is very slow ({exec_time:.3f}s)")
    elif exec_time > 5.0:
        bottlenecks.append(f"API request is slow ({exec_time:.3f}s)")
    print()
    
    # Analysis Summary
    print("📊 PERFORMANCE ANALYSIS SUMMARY")
    print("-" * 40)
    print(f"⏱️  Total Analysis Time: {total_time:.3f} seconds")
    print(f"🎯 Full API Request Time: {exec_time:.3f} seconds")
    print()
    
    if bottlenecks:
        print("⚠️  IDENTIFIED BOTTLENECKS:")
        for i, bottleneck in enumerate(bottlenecks, 1):
            print(f"   {i}. {bottleneck}")
        print()
        
        print("💡 OPTIMIZATION RECOMMENDATIONS:")
        
        if any("Data loading" in b for b in bottlenecks):
            print("   • Cache preprocessed data in memory")
            print("   • Use more efficient data formats (Parquet instead of CSV)")
            print("   • Implement lazy loading for large datasets")
        
        if any("Model loading" in b for b in bottlenecks):
            print("   • Keep model in memory after first load")
            print("   • Use model caching/singleton pattern")
            print("   • Consider lighter model formats")
        
        if any("Database" in b for b in bottlenecks):
            print("   • Add database indexes")
            print("   • Use connection pooling")
            print("   • Optimize database schema")
        
        if any("Ollama" in b for b in bottlenecks):
            print("   • Use smaller/faster Ollama model")
            print("   • Implement async Ollama calls")
            print("   • Add response caching")
            print("   • Reduce timeout values")
        
        if any("API request" in b for b in bottlenecks):
            print("   • Implement response caching")
            print("   • Use async processing where possible")
            print("   • Optimize agent coordination")
            print("   • Consider request batching")
    else:
        print("✅ No significant bottlenecks detected!")
        print("   System performance appears optimal.")
    
    print()
    print("🚀 QUICK FIXES TO TRY:")
    print("   1. Restart Ollama service: ollama serve")
    print("   2. Clear prediction cache/database")
    print("   3. Use smaller Ollama model (llama3.2:1b)")
    print("   4. Reduce API timeout values")
    print("   5. Check system memory usage")

if __name__ == "__main__":
    analyze_bottlenecks()
