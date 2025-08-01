"""
Ollama Agent for Local LLM Integration

Provides natural language explanations and insights using local Ollama models.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class OllamaAgent:
    """
    Agent for interacting with local Ollama LLM models.
    
    Provides enhanced explanations, insights, and natural language
    processing capabilities for vehicle price predictions.
    """
    
    def __init__(self, 
                 model_name: str = "llama3.2:1b",
                 ollama_host: str = "http://localhost:11434",
                 timeout: int = 5):  # Reduced from 10 to 5 seconds for faster response
        """
        Initialize Ollama Agent.
        
        Args:
            model_name: Name of the Ollama model to use
            ollama_host: Ollama server host URL
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.timeout = timeout
        self.api_url = f"{ollama_host}/api"
        self.available = False
        
        # Add response caching to avoid repeated expensive calls
        self._response_cache = {}
        self._cache_max_size = 50
        
        # Try to connect to Ollama
        self._verify_setup()
        
    def _verify_setup(self) -> bool:
        """Verify Ollama is running and model is available."""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                logger.warning("Ollama server not responding - local LLM features disabled")
                return False
            
            # Check if model is available
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if self.model_name not in model_names:
                logger.info(f"Model {self.model_name} not found. Available models: {model_names}")
                # Use first available model as fallback
                if model_names:
                    self.model_name = model_names[0]
                    logger.info(f"Using fallback model: {self.model_name}")
                else:
                    logger.warning("No Ollama models available - consider running 'ollama pull llama3.1:8b'")
                    return False
            
            self.available = True
            logger.info(f"Ollama agent initialized with model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.warning(f"Ollama not available: {str(e)} - local LLM features disabled")
            return False
    
    def _create_cache_key(self, vehicle_data: Dict[str, Any], market_data: Dict[str, Any], predicted_price: float) -> str:
        """Create a cache key from input parameters."""
        import hashlib
        
        # Create a simplified key based on main factors
        key_data = {
            'make': vehicle_data.get('make', ''),
            'model': vehicle_data.get('model', ''),
            'year': vehicle_data.get('year', 0),
            'mileage_range': (vehicle_data.get('mileage', 0) // 10000) * 10000,  # Round to 10k
            'price_range': (predicted_price // 1000) * 1000  # Round to 1k
        }
        
        key_str = str(sorted(key_data.items()))
        return hashlib.md5(key_str.encode()).hexdigest()[:8]
    
    def _add_to_cache(self, key: str, response: str) -> None:
        """Add response to cache with size limit."""
        if len(self._response_cache) >= self._cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._response_cache))
            del self._response_cache[oldest_key]
        
        self._response_cache[key] = response
    
    def generate_explanation(self, 
                           vehicle_data: Dict[str, Any], 
                           market_data: Dict[str, Any], 
                           predicted_price: float) -> str:
        """
        Generate detailed explanation using Ollama LLM with caching.
        
        Args:
            vehicle_data: Vehicle information
            market_data: Market conditions
            predicted_price: Predicted price
            
        Returns:
            str: Detailed explanation from LLM
        """
        if not self.available:
            return self._fallback_explanation(vehicle_data, market_data, predicted_price)
        
        # Create cache key from input data
        cache_key = self._create_cache_key(vehicle_data, market_data, predicted_price)
        
        # Check cache first
        if cache_key in self._response_cache:
            logger.info("Using cached response for similar request")
            return self._response_cache[cache_key]
        
        # Create shorter, optimized prompt
        prompt = f"""Vehicle price analysis:

Car: {vehicle_data.get('year', 'N/A')} {vehicle_data.get('make', '')} {vehicle_data.get('model', '')}, {vehicle_data.get('mileage', 'Unknown')} km
Price: ${predicted_price:,.0f}
Market: Stable conditions

Explain in 100 words:
1. Price justification
2. Key value factors  
3. One recommendation"""
        
        response = self._query_ollama(prompt)
        
        # Cache the response if successful
        if response:
            self._add_to_cache(cache_key, response)
            
        return response if response else self._fallback_explanation(vehicle_data, market_data, predicted_price)
    
    def generate_insights(self, predicted_price: float, explanation: str) -> str:
        """
        Generate actionable insights using Ollama LLM.
        
        Args:
            predicted_price: Predicted vehicle price
            explanation: Previous explanation
            
        Returns:
            str: Actionable insights
        """
        if not self.available:
            return self._fallback_insights(predicted_price)
        
        prompt = f"""Based on this vehicle price of ${predicted_price:,.2f}, provide 3 specific actionable insights:

{explanation}

Format as:
• Buyers: [specific advice]
• Sellers: [specific advice] 
• Market: [trend insight]

Keep each point concise and actionable."""
        
        response = self._query_ollama(prompt)
        return response if response else self._fallback_insights(predicted_price)
    
    def natural_language_query(self, query: str, context: Dict[str, Any]) -> str:
        """
        Handle natural language queries about vehicle pricing.
        
        Args:
            query: User's natural language question
            context: Context including vehicle data, predictions, etc.
            
        Returns:
            str: Natural language response
        """
        if not self.available:
            return "Local LLM not available for natural language queries. Please ensure Ollama is running."
        
        prompt = f"""Answer this vehicle pricing question using the provided data:

Question: {query}

Available data: {json.dumps(context, indent=2)}

Provide a helpful, accurate response. If more information is needed, state what would be helpful."""
        
        return self._query_ollama(prompt)
    
    def _query_ollama(self, prompt: str) -> str:
        """
        Send query to Ollama and return response.
        
        Args:
            prompt: Text prompt for the LLM
            
        Returns:
            str: LLM response
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 150  # Reduced from 300 to 150 for faster responses
                }
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except requests.exceptions.Timeout:
            logger.warning("Ollama request timed out")
            return ""
        except Exception as e:
            logger.error(f"Error querying Ollama: {str(e)}")
            return ""
    
    def _fallback_explanation(self, vehicle_data: Dict[str, Any], 
                            market_data: Dict[str, Any], 
                            predicted_price: float) -> str:
        """Fallback explanation when Ollama is not available."""
        vehicle_age = vehicle_data.get('vehicle_age', 'Unknown')
        mileage = vehicle_data.get('mileage', 'Unknown')
        
        explanation = f"""Price Analysis: ${predicted_price:,.2f}

This prediction considers:
• Vehicle age ({vehicle_age} years): Older vehicles typically depreciate
• Mileage ({mileage} km): Higher mileage generally reduces value
• Market conditions: Current economic factors affect pricing

The price reflects standard depreciation patterns and market trends.
Consider vehicle history, condition, and local market variations."""
        
        return explanation
    
    def _fallback_insights(self, predicted_price: float) -> str:
        """Fallback insights when Ollama is not available."""
        if predicted_price < 15000:
            return """• Buyers: Inspect thoroughly for hidden issues, budget for potential repairs
• Sellers: Price competitively, highlight maintenance records
• Market: Lower price range - focus on reliability over features"""
        elif predicted_price > 40000:
            return """• Buyers: Verify maintenance history, consider certified pre-owned options
• Sellers: Professional detailing and comprehensive documentation recommended
• Market: Premium segment - luxury features and brand reputation matter"""
        else:
            return """• Buyers: Good value range, compare similar vehicles in local market
• Sellers: Market timing is important, clean vehicle presentation helps
• Market: Mainstream segment - balance of features and reliability key"""
    
    def list_available_models(self) -> List[str]:
        """
        List all available Ollama models.
        
        Returns:
            List[str]: List of available model names
        """
        if not self.available:
            return []
        
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    def switch_model(self, new_model: str) -> bool:
        """
        Switch to a different Ollama model.
        
        Args:
            new_model: Name of the new model to use
            
        Returns:
            bool: True if switch was successful
        """
        if not self.available:
            return False
        
        try:
            available_models = self.list_available_models()
            if new_model in available_models:
                self.model_name = new_model
                logger.info(f"Switched to model: {new_model}")
                return True
            else:
                logger.warning(f"Model {new_model} not available. Available: {available_models}")
                return False
        except Exception as e:
            logger.error(f"Error switching model: {str(e)}")
            return False
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        return self.available
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "current_model": self.model_name,
            "host": self.ollama_host,
            "available": self.available,
            "timeout": self.timeout
        }


# Singleton instance for global use
_ollama_agent = None

def get_ollama_agent() -> Optional[OllamaAgent]:
    """Get global Ollama agent instance."""
    global _ollama_agent
    if _ollama_agent is None:
        try:
            _ollama_agent = OllamaAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama agent: {e}")
            return None
    return _ollama_agent


# Example usage and testing
if __name__ == "__main__":
    # Initialize Ollama agent
    ollama = OllamaAgent()
    
    if ollama.is_available():
        print("✅ Ollama is available")
        print(f"Current model: {ollama.model_name}")
        print(f"Available models: {ollama.list_available_models()}")
        
        # Example vehicle data
        vehicle_data = {"vehicle_age": 3, "mileage": 45000, "brand": "Toyota", "model": "Camry"}
        market_data = {"market_index": 1125.0, "fuel_price": 3.80}
        predicted_price = 22500.0
        
        # Generate explanation
        print("\n📝 Generating explanation...")
        explanation = ollama.generate_explanation(vehicle_data, market_data, predicted_price)
        print("Explanation:", explanation)
        
        # Generate insights
        print("\n💡 Generating insights...")
        insights = ollama.generate_insights(predicted_price, explanation)
        print("Insights:", insights)
        
    else:
        print("❌ Ollama is not available")
        print("To use Ollama features:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Run: ollama serve")
        print("3. Pull a model: ollama pull llama3.1:8b")
