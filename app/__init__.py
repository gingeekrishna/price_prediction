# Application Layer - Main Package
"""
Vehicle Price Prediction Application
Production-ready structure with frameworks:
- LangChain Integration
- ML Model Price Prediction  
- RAG Integration
- Vector Search
"""

__version__ = "1.0.0"
__author__ = "Vehicle Price Prediction Team"

from .config.settings import Settings
from .api.main import app
from .services.orchestrator import PredictionOrchestrator
from .models.price_predictor import PricePredictionModel
from .rag.rag_engine import RAGEngine
from .vector_search.search_engine import VectorSearchEngine
from .langchain.chain_manager import LangChainManager
from .ollama.ollama_manager import OllamaManager

__all__ = [
    "Settings",
    "app", 
    "PredictionOrchestrator",
    "PricePredictionModel",
    "RAGEngine", 
    "VectorSearchEngine",
    "LangChainManager",
    "OllamaManager"
]