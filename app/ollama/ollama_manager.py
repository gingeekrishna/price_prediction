"""
Ollama Integration Manager
Local LLM integration for vehicle price predictions and explanations
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

from ..config.settings import settings

logger = logging.getLogger(__name__)

class OllamaManager:
    """
    Production-ready Ollama integration for local LLM inference
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'ollama_base_url', 'http://localhost:11434')
        self.model = getattr(settings, 'ollama_model', 'llama3.2:3b')
        self.embedding_model = getattr(settings, 'embedding_model', 'nomic-embed-text:latest')
        self.timeout = 30
        self.is_available = False
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0
        self.error_count = 0
    
    async def initialize(self):
        """Initialize Ollama connection and verify models"""
        try:
            logger.info(f"🦙 Initializing Ollama connection to {self.base_url}")
            
            # Check if Ollama is available
            if await self._health_check():
                self.is_available = True
                
                # Verify models are available
                available_models = await self._list_models()
                
                if self.model not in available_models:
                    logger.warning(f"⚠️ Model {self.model} not found, pulling...")
                    await self._pull_model(self.model)
                
                if self.embedding_model not in available_models:
                    logger.warning(f"⚠️ Embedding model {self.embedding_model} not found, pulling...")
                    await self._pull_model(self.embedding_model)
                
                logger.info(f"✅ Ollama initialized successfully with model: {self.model}")
            else:
                logger.warning("⚠️ Ollama not available, using fallback responses")
                
        except Exception as e:
            logger.error(f"❌ Ollama initialization failed: {e}")
            self.is_available = False
    
    async def _health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
            return False
    
    async def _list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            return []
    
    async def _pull_model(self, model_name: str):
        """Pull a model from Ollama registry"""
        try:
            logger.info(f"📥 Pulling model: {model_name}")
            
            async with aiohttp.ClientSession() as session:
                payload = {"name": model_name}
                
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
                ) as response:
                    if response.status == 200:
                        # Stream the response to show progress
                        async for line in response.content:
                            if line:
                                try:
                                    progress = json.loads(line.decode())
                                    if 'status' in progress:
                                        logger.info(f"📥 {progress['status']}")
                                except json.JSONDecodeError:
                                    continue
                        
                        logger.info(f"✅ Model {model_name} pulled successfully")
                    else:
                        logger.error(f"❌ Failed to pull model {model_name}: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Error pulling model {model_name}: {e}")
    
    async def generate_explanation(
        self, 
        vehicle_data: Dict[str, Any], 
        predicted_price: float,
        similar_vehicles: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI explanation for price prediction using Ollama"""
        start_time = datetime.now()
        
        try:
            if not self.is_available:
                return self._get_fallback_explanation(vehicle_data, predicted_price)
            
            # Create prompt for vehicle price explanation
            prompt = self._build_explanation_prompt(vehicle_data, predicted_price, similar_vehicles)
            
            # Generate response using Ollama
            response = await self._generate_text(prompt)
            
            # Track performance
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_stats(response_time, success=True)
            
            return {
                "explanation": response,
                "confidence": 0.85,
                "model": self.model,
                "response_time_ms": response_time,
                "source": "ollama"
            }
            
        except Exception as e:
            logger.error(f"❌ Ollama explanation generation failed: {e}")
            self._update_stats(0, success=False)
            return self._get_fallback_explanation(vehicle_data, predicted_price)
    
    async def _generate_text(self, prompt: str) -> str:
        """Generate text using Ollama API"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '').strip()
                    else:
                        logger.error(f"❌ Ollama API error: {response.status}")
                        return "Unable to generate explanation at this time."
                        
        except Exception as e:
            logger.error(f"❌ Text generation failed: {e}")
            raise
    
    def _build_explanation_prompt(
        self, 
        vehicle_data: Dict[str, Any], 
        predicted_price: float,
        similar_vehicles: List[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for vehicle price explanation"""
        
        prompt = f"""As an automotive expert, explain the predicted price for this vehicle:

Vehicle Details:
- Brand: {vehicle_data.get('brand', 'Unknown')}
- Model: {vehicle_data.get('model', 'Unknown')}
- Year: {vehicle_data.get('year', 'Unknown')}
- Mileage: {vehicle_data.get('mileage', 'Unknown'):,} miles
- Condition: {vehicle_data.get('condition', 'Unknown')}
- Type: {vehicle_data.get('vehicle_type', 'Unknown')}

Predicted Price: ${predicted_price:,.2f}

Please provide a clear, professional explanation covering:
1. Key factors affecting this vehicle's value
2. How the price compares to market expectations
3. Any notable value considerations (depreciation, demand, etc.)

Keep the explanation concise (2-3 sentences) and focus on the most important pricing factors."""

        # Add similar vehicles context if available
        if similar_vehicles:
            prompt += f"\n\nSimilar vehicles in the market:\n"
            for i, vehicle in enumerate(similar_vehicles[:3], 1):
                prompt += f"{i}. {vehicle.get('brand')} {vehicle.get('model')} ({vehicle.get('year')}) - ${vehicle.get('price', 0):,.2f}\n"
        
        return prompt
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama"""
        try:
            if not self.is_available:
                # Return mock embeddings if Ollama unavailable
                return [[0.1] * 384 for _ in texts]
            
            embeddings = []
            
            async with aiohttp.ClientSession() as session:
                for text in texts:
                    payload = {
                        "model": self.embedding_model,
                        "prompt": text
                    }
                    
                    async with session.post(
                        f"{self.base_url}/api/embeddings",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            embeddings.append(data.get('embedding', [0.1] * 384))
                        else:
                            # Fallback embedding
                            embeddings.append([0.1] * 384)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            return [[0.1] * 384 for _ in texts]
    
    def _get_fallback_explanation(
        self, 
        vehicle_data: Dict[str, Any], 
        predicted_price: float
    ) -> Dict[str, Any]:
        """Generate fallback explanation when Ollama is unavailable"""
        
        brand = vehicle_data.get('brand', 'Unknown')
        year = vehicle_data.get('year', 0)
        mileage = vehicle_data.get('mileage', 0)
        
        # Simple rule-based explanation
        factors = []
        
        if year >= 2020:
            factors.append("recent model year")
        elif year >= 2015:
            factors.append("relatively modern vehicle")
        else:
            factors.append("older vehicle with higher depreciation")
        
        if mileage < 30000:
            factors.append("low mileage")
        elif mileage < 80000:
            factors.append("moderate mileage")
        else:
            factors.append("high mileage")
        
        explanation = (
            f"The predicted price of ${predicted_price:,.2f} for this {brand} "
            f"is based on key factors including {', '.join(factors)}. "
            f"Market conditions and vehicle condition also influence the final valuation."
        )
        
        return {
            "explanation": explanation,
            "confidence": 0.6,
            "model": "rule_based_fallback",
            "response_time_ms": 10,
            "source": "fallback"
        }
    
    def _update_stats(self, response_time: float, success: bool):
        """Update performance statistics"""
        self.request_count += 1
        
        if success:
            self.total_response_time += response_time
        else:
            self.error_count += 1
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get Ollama performance statistics"""
        avg_response_time = 0
        if self.request_count > 0:
            successful_requests = self.request_count - self.error_count
            if successful_requests > 0:
                avg_response_time = self.total_response_time / successful_requests
        
        return {
            "is_available": self.is_available,
            "model": self.model,
            "embedding_model": self.embedding_model,
            "base_url": self.base_url,
            "total_requests": self.request_count,
            "successful_requests": self.request_count - self.error_count,
            "error_count": self.error_count,
            "avg_response_time_ms": avg_response_time,
            "error_rate": self.error_count / max(1, self.request_count)
        }
    
    async def health_check(self) -> bool:
        """Perform health check on Ollama service"""
        return await self._health_check()
    
    async def cleanup(self):
        """Cleanup Ollama resources"""
        logger.info("🧹 Cleaning up Ollama manager resources...")
        self.is_available = False
