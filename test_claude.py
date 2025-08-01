#!/usr/bin/env python3
"""
Test Claude LLM Integration
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

def test_claude_integration():
    print("🧠 Testing Claude LLM Integration")
    print("=" * 50)
    
    # Test 1: Claude Agent availability
    print("1️⃣  Testing Claude Agent...")
    try:
        from src.agents.claude_agent import ClaudeAgent
        
        agent = ClaudeAgent()
        print(f"   ✅ Claude Agent initialized")
        print(f"   🤖 Model: {agent.model_name}")
        print(f"   🔗 Available: {agent.available}")
        
        if not agent.available:
            print("   ⚠️  Claude not available. Please:")
            print("      - Set ANTHROPIC_API_KEY environment variable")
            print("      - Install anthropic package: pip install anthropic")
            return False
            
        # Test explanation generation
        print("   💬 Testing explanation generation...")
        vehicle_data = {
            "make": "Toyota",
            "model": "Camry", 
            "year": 2020,
            "mileage": 30000
        }
        market_data = {
            "avg_price": 24000,
            "trend": "stable"
        }
        
        explanation = agent.generate_explanation(vehicle_data, market_data, 25500.0)
        print(f"   📝 Generated explanation: {explanation[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 2: ExplainerAgentRAG with Claude
    print("\n2️⃣  Testing ExplainerAgentRAG with Claude...")
    try:
        from src.agents.explainer_agent import ExplainerAgentRAG
        
        explainer = ExplainerAgentRAG(use_claude=True, llm_provider="claude")
        print(f"   ✅ ExplainerAgentRAG initialized with Claude")
        print(f"   🧠 Claude enabled: {explainer.use_claude}")
        print(f"   🤖 Ollama enabled: {explainer.use_ollama}")
        print(f"   🎯 LLM Provider: {explainer.llm_provider}")
        
        # Test explanation
        input_data = {
            "vehicle_age": 4,
            "mileage": 30000,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020
        }
        
        explanation = explainer.explain(input_data, 25500.0)
        print(f"   📝 Generated explanation: {explanation[:150]}...")
        
        if "Claude AI" in explanation:
            print("   🎉 SUCCESS: Using Claude for explanations!")
        elif "Ollama AI" in explanation:
            print("   ⚠️  Fallback: Using Ollama (Claude may not be available)")
        else:
            print("   ⚠️  Fallback: Using standard explanations")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main test function."""
    success = test_claude_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Claude integration test completed!")
        print("\n🚀 Ready to use Claude in your AI agent!")
        print("\n📡 Available API endpoints:")
        print("   • POST /predict_with_claude - Claude-powered predictions")
        print("   • POST /predict_with_ai - Smart AI selection (Claude > Ollama > Standard)")
        print("   • GET /claude/status - Check Claude availability")
    else:
        print("❌ Claude integration test failed!")
        print("\n🔧 Setup instructions:")
        print("   1. Get Anthropic API key from: https://console.anthropic.com/")
        print("   2. Set environment variable: ANTHROPIC_API_KEY=your_key_here")
        print("   3. Restart your application")

if __name__ == "__main__":
    main()
