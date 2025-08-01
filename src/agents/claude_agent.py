"""
Claude Agent for Anthropic Claude LLM Integration

Provides natural language explanations and insights using Anthropic Claude models.
"""

import os
import logging
from typing import Dict, Any

try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

class ClaudeAgent:
    """
    Agent for interacting with Anthropic Claude LLM models.
    """
    def __init__(self, model_name: str = "claude-3-opus-20240229", api_key: str = None, timeout: int = 10):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.timeout = timeout
        self.available = anthropic is not None and self.api_key is not None
        if not self.available:
            logger.warning("Claude agent not available: missing anthropic package or API key.")
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_explanation(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any], predicted_price: float) -> str:
        if not self.available:
            return "Claude LLM not available. Please set ANTHROPIC_API_KEY and install anthropic package."
        prompt = f"""
As an automotive expert, explain this vehicle price prediction concisely:

Vehicle: {vehicle_data.get('year', 'Unknown')} {vehicle_data.get('make', '')} {vehicle_data.get('model', '')}, {vehicle_data.get('mileage', 'Unknown')} km
Market: {market_data.get('trend', 'N/A')}, Avg Price: ${market_data.get('avg_price', 'N/A')}
Predicted Price: ${predicted_price:,.2f}

Provide a brief explanation covering:
1. Why this price is reasonable
2. Key factors affecting the value
3. One actionable recommendation

Keep response under 100 words and professional."""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=256,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip() if response and response.content else ""
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return "Claude LLM error."
