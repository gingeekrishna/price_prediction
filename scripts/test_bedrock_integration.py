#!/usr/bin/env python3
"""
Test script for AWS Bedrock integration in Vehicle Price Prediction Agent.

This script tests the BedrockAgent functionality and integration with the 
ExplainerAgentRAG system.
"""

import os
import sys
import logging

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bedrock_agent():
    """Test BedrockAgent initialization and basic functionality."""
    try:
        from src.agents.bedrock_agent import BedrockAgent
        
        print("🔮 Testing AWS Bedrock Agent...")
        bedrock_agent = BedrockAgent()
        
        if bedrock_agent.available:
            print(f"✅ Bedrock Agent available with models: {bedrock_agent.available_models}")
            print(f"🌍 Region: {bedrock_agent.region}")
            
            # Test explanation generation
            vehicle_data = {
                'vehicle_age': 5,
                'mileage': 50000,
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2019
            }
            
            market_data = {
                'market_index': 1050,
                'fuel_price': 3.25,
                'avg_price': 18500,
                'trend': 'stable'
            }
            
            predicted_price = 18500.0
            
            print(f"\n🚗 Testing explanation for: {vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}")
            print(f"💰 Predicted price: ${predicted_price:,.2f}")
            
            explanation = bedrock_agent.generate_explanation(vehicle_data, market_data, predicted_price)
            
            if explanation:
                print(f"\n✅ Bedrock explanation generated successfully:")
                print("=" * 60)
                print(explanation)
                print("=" * 60)
            else:
                print("❌ Failed to generate explanation")
                
        else:
            print("❌ Bedrock Agent not available - check AWS credentials and region")
            print("💡 Make sure you have AWS credentials configured and Bedrock access enabled")
            
    except Exception as e:
        print(f"❌ Error testing Bedrock Agent: {e}")
        import traceback
        traceback.print_exc()

def test_explainer_integration():
    """Test BedrockAgent integration with ExplainerAgentRAG."""
    try:
        from src.agents.explainer_agent import ExplainerAgentRAG
        
        print("\n🧠 Testing ExplainerAgentRAG with Bedrock integration...")
        
        # Initialize with all providers
        explainer = ExplainerAgentRAG(
            use_bedrock=True,
            use_claude=False,  # Disable to focus on Bedrock
            use_ollama=False,  # Disable to focus on Bedrock
            llm_provider="bedrock"
        )
        
        # Test data
        input_data = {
            'vehicle_age': 3,
            'mileage': 35000,
            'make': 'Honda',
            'model': 'Accord',
            'year': 2021,
            'market_index': 1100,
            'fuel_price': 3.40
        }
        
        predicted_price = 22500.0
        
        print(f"\n🚗 Testing integrated explanation for: {input_data['year']} {input_data['make']} {input_data['model']}")
        print(f"💰 Predicted price: ${predicted_price:,.2f}")
        
        explanation = explainer.explain(input_data, predicted_price)
        
        if explanation:
            print(f"\n✅ Integrated explanation generated successfully:")
            print("=" * 60)
            print(explanation)
            print("=" * 60)
            
            # Check if Bedrock was used
            if "AWS Bedrock AI" in explanation:
                print("🎉 Successfully used AWS Bedrock for explanation!")
            else:
                print("⚠️  Bedrock wasn't used - fallback to other provider")
                
        else:
            print("❌ Failed to generate integrated explanation")
            
    except Exception as e:
        print(f"❌ Error testing integrated explanation: {e}")
        import traceback
        traceback.print_exc()

def test_multi_model_support():
    """Test different Bedrock models if available."""
    try:
        from src.agents.bedrock_agent import BedrockAgentManager
        
        print("\n🔧 Testing BedrockAgentManager multi-model support...")
        
        manager = BedrockAgentManager()
        available_models = manager.list_available_models()
        
        if available_models:
            print(f"✅ Available Bedrock models: {list(available_models.keys())}")
            
            # Test with different models
            test_models = ["anthropic.claude-3-sonnet-20240229-v1:0", "amazon.titan-text-express-v1"]
            
            for model_id in test_models:
                if model_id in available_models:
                    print(f"\n🧪 Testing model: {model_id}")
                    agent = manager.get_agent(model_id)
                    if agent and agent.available:
                        print(f"✅ {model_id} agent created successfully")
                    else:
                        print(f"❌ Failed to create agent for {model_id}")
                else:
                    print(f"⚠️  Model {model_id} not in available models list")
        else:
            print("❌ No Bedrock models available")
            
    except Exception as e:
        print(f"❌ Error testing multi-model support: {e}")

def main():
    """Run all Bedrock integration tests."""
    print("🚀 AWS Bedrock Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Basic Bedrock Agent
    test_bedrock_agent()
    
    # Test 2: Integration with ExplainerAgentRAG
    test_explainer_integration()
    
    # Test 3: Multi-model support
    test_multi_model_support()
    
    print("\n✅ Bedrock integration testing complete!")
    print("\n💡 Tips:")
    print("   - Ensure AWS credentials are configured (AWS CLI, IAM role, or environment variables)")
    print("   - Verify Bedrock model access is enabled in your AWS account")
    print("   - Check that your region supports the requested Bedrock models")

if __name__ == "__main__":
    main()
