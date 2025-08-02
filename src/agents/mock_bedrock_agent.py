"""
Mock Bedrock Agent for Local Development

This provides a local simulation of AWS Bedrock for development and testing
when AWS credentials are not available or for offline development.
"""

import json
import logging
from typing import Dict, Any, Optional
import time
import random

logger = logging.getLogger(__name__)

class MockBedrockAgent:
    """
    Mock implementation of BedrockAgent for local development.
    Simulates AWS Bedrock responses using local logic.
    """
    
    def __init__(self, 
                 model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                 region_name: str = "us-east-1",
                 **kwargs):
        """Initialize Mock Bedrock Agent."""
        self.model_id = model_id
        self.region_name = region_name
        self.available = True  # Always available for local development
        
        # Mock response templates
        self.response_templates = {
            "positive": [
                "This vehicle is priced competitively based on current market conditions. The {make} {model} has strong resale value and the {mileage} miles is reasonable for a {age}-year-old vehicle.",
                "Excellent value proposition. {make} vehicles maintain their worth well, and at {mileage} miles, this {model} represents a solid investment opportunity.",
                "Fair market pricing. The {age}-year age factor is offset by {make}'s reputation for reliability and the vehicle's well-maintained condition."
            ],
            "neutral": [
                "Market-appropriate pricing for this {year} {make} {model}. The {mileage} mileage is typical for this age vehicle, supporting the predicted price point.",
                "Standard market valuation. This {make} {model} with {mileage} miles fits the expected price range for vehicles of this specification."
            ],
            "recommendations": [
                "Consider negotiating based on maintenance history and local market conditions.",
                "Verify vehicle history report and recent service records before finalizing.",
                "Compare with similar vehicles in your area for the best deal.",
                "Factor in upcoming maintenance costs for vehicles of this age."
            ]
        }
        
        logger.info(f"Mock Bedrock agent initialized with model: {self.model_id}")
    
    def generate_explanation(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any], predicted_price: float) -> str:
        """
        Generate mock vehicle price explanation.
        
        Args:
            vehicle_data: Dictionary containing vehicle information
            market_data: Dictionary containing market data
            predicted_price: Predicted price value
            
        Returns:
            Generated explanation string
        """
        # Simulate API delay
        time.sleep(random.uniform(0.5, 1.5))
        
        # Extract vehicle info
        make = vehicle_data.get('make', 'Unknown')
        model = vehicle_data.get('model', 'Unknown')
        year = vehicle_data.get('year', 'Unknown')
        mileage = vehicle_data.get('mileage', 'Unknown')
        age = vehicle_data.get('vehicle_age', 'Unknown')
        
        # Select response template based on price range
        if predicted_price > 25000:
            template_type = "positive"
        elif predicted_price < 15000:
            template_type = "neutral"
        else:
            template_type = random.choice(["positive", "neutral"])
        
        # Generate main explanation
        template = random.choice(self.response_templates[template_type])
        explanation = template.format(
            make=make,
            model=model,
            year=year,
            mileage=f"{mileage:,}" if isinstance(mileage, (int, float)) else mileage,
            age=age
        )
        
        # Add recommendation
        recommendation = random.choice(self.response_templates["recommendations"])
        
        # Format final response
        mock_response = f"""🔮 Mock Bedrock Analysis (Local Development Mode):

{explanation}

Market Analysis:
• Current market trend: {market_data.get('trend', 'Stable')}
• Average price point: ${market_data.get('avg_price', predicted_price):,.2f}
• Price positioning: {"Above" if predicted_price > market_data.get('avg_price', predicted_price) else "Below"} market average

Recommendation: {recommendation}

💡 Note: This is a simulated response for local development. Enable AWS Bedrock for production-grade analysis."""
        
        return mock_response
    
    def get_available_models(self) -> list:
        """Return mock list of available models."""
        return [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "amazon.titan-text-express-v1",
            "ai21.j2-ultra-v1",
            "cohere.command-text-v14"
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return mock model information."""
        return {
            "model_id": self.model_id,
            "region": self.region_name,
            "available": True,
            "provider": "Mock AWS Bedrock (Local)",
            "model_family": self._get_model_family()
        }
    
    def _get_model_family(self) -> str:
        """Get the model family name."""
        if "anthropic.claude" in self.model_id:
            return "Mock Anthropic Claude"
        elif "amazon.titan" in self.model_id:
            return "Mock Amazon Titan"
        elif "ai21.j2" in self.model_id:
            return "Mock AI21 Jurassic"
        elif "cohere.command" in self.model_id:
            return "Mock Cohere Command"
        else:
            return "Mock Foundation Model"


class LocalBedrockAgent:
    """
    Enhanced Bedrock Agent that uses Mock for local development
    and real Bedrock when AWS credentials are available.
    """
    
    def __init__(self, **kwargs):
        """Initialize with automatic mock fallback."""
        try:
            # Try to import real BedrockAgent
            from .bedrock_agent import BedrockAgent
            self.agent = BedrockAgent(**kwargs)
            
            # If not available, use mock
            if not self.agent.available:
                logger.info("AWS Bedrock not available, using mock agent for local development")
                self.agent = MockBedrockAgent(**kwargs)
                self.is_mock = True
            else:
                self.is_mock = False
                
        except Exception as e:
            logger.info(f"Using mock Bedrock agent: {e}")
            self.agent = MockBedrockAgent(**kwargs)
            self.is_mock = True
    
    def __getattr__(self, name):
        """Delegate all method calls to the underlying agent."""
        return getattr(self.agent, name)
    
    @property
    def available(self):
        """Check if agent is available."""
        return self.agent.available
