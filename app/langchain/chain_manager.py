"""
LangChain Integration Framework
Manages LLM chains, prompts, and AI-powered explanations
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio

try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.memory import ConversationBufferMemory
    from langchain.agents import initialize_agent, Tool, AgentType
except ImportError:
    logger.warning("LangChain not installed. Run: pip install langchain")
    OpenAI = ChatOpenAI = LLMChain = None

from ..config.settings import settings
from ..ollama.ollama_manager import OllamaManager

logger = logging.getLogger(__name__)

class LangChainManager:
    """
    Production-ready LangChain integration for vehicle price prediction
    Handles multiple LLM providers and AI-powered explanations
    """
    
    def __init__(self, rag_engine=None):
        self.rag_engine = rag_engine
        self.llm = None
        self.explanation_chain = None
        self.ollama_manager = None
        self.is_initialized = False
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0
        self.error_count = 0
        self.prediction_chain = None
        self.memory = None
        self.is_initialized = False
        
        # Prompt templates
        self.explanation_prompt = """
        You are an expert vehicle price analyst. Based on the following information, 
        provide a clear, professional explanation for the predicted vehicle price.
        
        Vehicle Details:
        - Age: {vehicle_age} years
        - Mileage: {mileage} miles
        - Type: {vehicle_type}
        - Brand: {brand}
        - Model: {model}
        - Condition: {condition}
        
        ML Prediction:
        - Predicted Price: ${predicted_price:,.2f}
        - Confidence: {confidence:.1%}
        - Price Range: ${min_price:,.2f} - ${max_price:,.2f}
        
        Market Context:
        {market_context}
        
        Similar Vehicles:
        {similar_vehicles}
        
        Provide a comprehensive explanation that includes:
        1. Key factors affecting the price
        2. Market positioning analysis
        3. Confidence assessment
        4. Recommendations for buyers/sellers
        
        Keep the explanation professional, concise, and actionable.
        """
        
        self.prediction_prompt = """
        You are an AI vehicle price prediction expert. Using your knowledge of the automotive market,
        analyze the following vehicle and provide a price estimate with reasoning.
        
        Vehicle Information:
        {vehicle_info}
        
        Market Data:
        {market_data}
        
        Please provide:
        1. Your price estimate
        2. Confidence level (1-10)
        3. Key factors considered
        4. Market comparison
        5. Risk factors
        
        Format your response as a structured analysis.
        """
    
    async def initialize(self):
        """Initialize LangChain components"""
        try:
            logger.info("🔗 Initializing LangChain manager...")
            
            # Initialize Ollama manager first if enabled
            if settings.use_ollama:
                self.ollama_manager = OllamaManager()
                await self.ollama_manager.initialize()
                
                if self.ollama_manager.is_available:
                    logger.info("✅ Ollama LLM initialized as primary")
                else:
                    logger.warning("⚠️ Ollama not available, using traditional LLM")
            
            # Initialize LLM based on available API keys (fallback)
            if settings.openai_api_key:
                self.llm = ChatOpenAI(
                    openai_api_key=settings.openai_api_key,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens
                )
                logger.info("✅ OpenAI LLM initialized as fallback")
            else:
                logger.warning("⚠️ No OpenAI API key found, using mock LLM")
                self.llm = MockLLM()
            
            # Initialize memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create explanation chain
            explanation_template = PromptTemplate(
                template=self.explanation_prompt,
                input_variables=[
                    "vehicle_age", "mileage", "vehicle_type", "brand", "model", "condition",
                    "predicted_price", "confidence", "min_price", "max_price",
                    "market_context", "similar_vehicles"
                ]
            )
            
            if LLMChain:
                self.explanation_chain = LLMChain(
                    llm=self.llm,
                    prompt=explanation_template,
                    memory=self.memory,
                    verbose=settings.debug
                )
            
            # Create prediction chain
            prediction_template = PromptTemplate(
                template=self.prediction_prompt,
                input_variables=["vehicle_info", "market_data"]
            )
            
            if LLMChain:
                self.prediction_chain = LLMChain(
                    llm=self.llm,
                    prompt=prediction_template,
                    verbose=settings.debug
                )
            
            self.is_initialized = True
            logger.info("✅ LangChain manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ LangChain initialization failed: {e}")
            # Use fallback mock implementation
            self.llm = MockLLM()
            self.is_initialized = True
    
    async def generate_explanation(
        self, 
        vehicle_data: Dict[str, Any], 
        ml_prediction: Dict[str, Any],
        similar_vehicles: List[Dict[str, Any]],
        market_insights: Dict[str, Any]
    ) -> str:
        """Generate AI-powered explanation for price prediction"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Try Ollama first if available
            if self.ollama_manager and self.ollama_manager.is_available:
                result = await self.ollama_manager.generate_explanation(
                    vehicle_data, 
                    ml_prediction.get('predicted_price', 0),
                    similar_vehicles
                )
                return result['explanation']
            
            # Fallback to traditional LangChain
            # Prepare context
            market_context = self._format_market_context(market_insights)
            similar_vehicles_text = self._format_similar_vehicles(similar_vehicles)
            
            # Generate explanation using LangChain
            if self.explanation_chain:
                explanation = await self._run_chain_async(
                    self.explanation_chain,
                    {
                        "vehicle_age": vehicle_data.get("vehicle_age", 0),
                        "mileage": vehicle_data.get("mileage", 0),
                        "vehicle_type": vehicle_data.get("vehicle_type", "car"),
                        "brand": vehicle_data.get("brand", "unknown"),
                        "model": vehicle_data.get("model", "unknown"),
                        "condition": vehicle_data.get("condition", "good"),
                        "predicted_price": ml_prediction.get("price", 0),
                        "confidence": ml_prediction.get("confidence", 0),
                        "min_price": ml_prediction.get("price_range", {}).get("min", 0),
                        "max_price": ml_prediction.get("price_range", {}).get("max", 0),
                        "market_context": market_context,
                        "similar_vehicles": similar_vehicles_text
                    }
                )
                return explanation
            else:
                # Fallback explanation
                return self._generate_fallback_explanation(vehicle_data, ml_prediction)
                
        except Exception as e:
            logger.error(f"❌ Explanation generation failed: {e}")
            return self._generate_fallback_explanation(vehicle_data, ml_prediction)
    
    async def predict_with_chain(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction using LangChain (AI-only approach)"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            vehicle_info = self._format_vehicle_info(vehicle_data)
            market_data = "Current market trends and data"
            
            if self.prediction_chain:
                prediction_text = await self._run_chain_async(
                    self.prediction_chain,
                    {
                        "vehicle_info": vehicle_info,
                        "market_data": market_data
                    }
                )
                
                # Parse AI response (simplified)
                estimated_price = self._extract_price_from_text(prediction_text)
                
                return {
                    "predicted_price": estimated_price,
                    "confidence_score": 0.7,  # Default for AI-only predictions
                    "price_range": {
                        "min": estimated_price * 0.9,
                        "max": estimated_price * 1.1
                    },
                    "explanation": prediction_text,
                    "model_version": "langchain-ai",
                    "processing_time_ms": 500
                }
            else:
                raise ValueError("LangChain not available")
                
        except Exception as e:
            logger.error(f"❌ LangChain prediction failed: {e}")
            raise
    
    async def _run_chain_async(self, chain, inputs: Dict[str, Any]) -> str:
        """Run LangChain asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, chain.run, inputs)
    
    def _format_market_context(self, market_insights: Dict[str, Any]) -> str:
        """Format market insights for prompt"""
        if not market_insights:
            return "General market conditions apply"
        
        context_parts = []
        for key, value in market_insights.items():
            context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts)
    
    def _format_similar_vehicles(self, similar_vehicles: List[Dict[str, Any]]) -> str:
        """Format similar vehicles for prompt"""
        if not similar_vehicles:
            return "No similar vehicles found in database"
        
        vehicles_text = []
        for i, vehicle in enumerate(similar_vehicles[:3], 1):
            vehicles_text.append(
                f"{i}. {vehicle.get('brand', 'Unknown')} {vehicle.get('model', '')} "
                f"({vehicle.get('year', 'N/A')}) - ${vehicle.get('price', 0):,.2f}"
            )
        
        return "\n".join(vehicles_text)
    
    def _format_vehicle_info(self, vehicle_data: Dict[str, Any]) -> str:
        """Format vehicle information for prompt"""
        info_parts = []
        for key, value in vehicle_data.items():
            if value is not None:
                info_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(info_parts)
    
    def _extract_price_from_text(self, text: str) -> float:
        """Extract price estimate from AI response"""
        import re
        
        # Look for price patterns in the text
        price_patterns = [
            r'\$([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*dollars?',
            r'estimate[d]?\s*[at]?\s*\$?([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    price_str = matches[0].replace(',', '')
                    return float(price_str)
                except ValueError:
                    continue
        
        # Default fallback price
        return 20000.0
    
    def _generate_fallback_explanation(
        self, 
        vehicle_data: Dict[str, Any], 
        ml_prediction: Dict[str, Any]
    ) -> str:
        """Generate fallback explanation when LangChain is not available"""
        return f"""
        Based on the vehicle features and market analysis, the predicted price of ${ml_prediction.get('price', 0):,.2f} 
        is reasonable for a {vehicle_data.get('vehicle_age', 0)}-year-old {vehicle_data.get('vehicle_type', 'vehicle')} 
        with {vehicle_data.get('mileage', 0):,} miles.
        
        Key factors considered:
        • Vehicle age and depreciation
        • Mileage impact on value
        • Current market conditions
        • Vehicle condition and features
        
        Confidence: {ml_prediction.get('confidence', 0):.1%}
        """
    
    async def health_check(self) -> bool:
        """Check LangChain components health"""
        try:
            if not self.is_initialized:
                return False
            
            # Test simple generation
            if isinstance(self.llm, MockLLM):
                return True  # Mock LLM is always healthy
            
            # Test with a simple prompt
            test_result = await self._run_chain_async(
                self.explanation_chain,
                {
                    "vehicle_age": 5,
                    "mileage": 50000,
                    "vehicle_type": "car",
                    "brand": "toyota",
                    "model": "camry",
                    "condition": "good",
                    "predicted_price": 20000,
                    "confidence": 0.85,
                    "min_price": 18000,
                    "max_price": 22000,
                    "market_context": "Test context",
                    "similar_vehicles": "Test vehicles"
                }
            )
            
            return len(test_result) > 0
            
        except Exception as e:
            logger.error(f"LangChain health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup LangChain resources"""
        logger.info("🧹 Cleaning up LangChain resources...")
        self.llm = None
        self.explanation_chain = None
        self.prediction_chain = None
        self.memory = None
        self.is_initialized = False

class MockLLM:
    """Mock LLM for when real LLM is not available"""
    
    def __init__(self):
        self.temperature = 0.1
        self.max_tokens = 2000
    
    def __call__(self, prompt: str) -> str:
        return "Mock LLM response: Price analysis based on vehicle features and market conditions."
    
    def predict(self, text: str) -> str:
        return "Mock prediction response"
