#!/usr/bin/env python3
"""
Test script for Ollama integration with vehicle price predictions.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from src.agents.ollama_agent import OllamaAgent
import json

def test_ollama_integration():
    """Test the Ollama agent with vehicle price prediction data."""
    
    print("🚀 Testing Ollama Integration with Vehicle Price Predictions")
    print("=" * 60)
    
    # Initialize Ollama agent
    agent = OllamaAgent()
    print(f"✅ Ollama Agent Status: {'Available' if agent.available else 'Unavailable'}")
    print(f"🤖 Model: {agent.model_name}")
    print()
    
    if not agent.available:
        print("❌ Ollama not available. Please ensure Ollama is running.")
        return
    
    # Test data
    vehicle_data = {
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "mileage": 30000,
        "condition": "good",
        "engine_size": "2.5L",
        "fuel_type": "gasoline"
    }
    
    market_data = {
        "avg_price": 24000,
        "market_trend": "stable",
        "demand_level": "high",
        "supply_level": "medium",
        "seasonal_factor": 1.02
    }
    
    predicted_price = 25500.0
    
    print("🚗 Test Vehicle Data:")
    print(json.dumps(vehicle_data, indent=2))
    print()
    
    print("📊 Market Data:")
    print(json.dumps(market_data, indent=2))
    print()
    
    print(f"💰 Predicted Price: ${predicted_price:,.2f}")
    print()
    
    # Generate explanation
    print("🧠 Generating AI Explanation...")
    print("-" * 40)
    
    try:
        explanation = agent.generate_explanation(vehicle_data, market_data, predicted_price)
        print("✅ Generated Explanation:")
        print(explanation)
        print()
        
        # Test insights
        print("🔍 Generating Market Insights...")
        print("-" * 40)
        
        insights = agent.generate_insights({
            "vehicle_type": f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}",
            "predicted_price": predicted_price,
            "market_data": market_data
        })
        
        print("✅ Generated Insights:")
        print(insights)
        
    except Exception as e:
        print(f"❌ Error generating explanation: {e}")
        # Test fallback
        print("\n🔄 Testing fallback explanation...")
        fallback = agent._fallback_explanation(vehicle_data, market_data, predicted_price)
        print("✅ Fallback Explanation:")
        print(fallback)

if __name__ == "__main__":
    test_ollama_integration()
