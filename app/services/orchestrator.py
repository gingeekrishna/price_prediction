"""
Main Orchestrator Service
Coordinates all framework components for production-ready predictions
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from ..config.settings import settings
from ..models.price_predictor import PricePredictionModel
from ..langchain.chain_manager import LangChainManager
from ..rag.rag_engine import RAGEngine
from ..vector_search.search_engine import VectorSearchEngine
from ..data.data_pipeline import DataPipeline
from ..utils.monitoring import MetricsCollector
from ..utils.caching import CacheManager

logger = logging.getLogger(__name__)

class PredictionOrchestrator:
    """
    Main orchestrator that coordinates all framework components
    for scalable, production-ready vehicle price predictions
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.is_initialized = False
        
        # Framework components
        self.ml_model: Optional[PricePredictionModel] = None
        self.langchain_manager: Optional[LangChainManager] = None
        self.rag_engine: Optional[RAGEngine] = None
        self.vector_search: Optional[VectorSearchEngine] = None
        self.data_pipeline: Optional[DataPipeline] = None
        
        # Utilities
        self.metrics: Optional[MetricsCollector] = None
        self.cache: Optional[CacheManager] = None
        
        # Training tracking
        self.training_tasks: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize all framework components"""
        try:
            logger.info("🔄 Initializing orchestrator components...")
            
            # Initialize utilities first
            self.metrics = MetricsCollector()
            self.cache = CacheManager()
            
            # Initialize data pipeline
            logger.info("📊 Initializing data pipeline...")
            self.data_pipeline = DataPipeline()
            await self.data_pipeline.initialize()
            
            # Initialize ML model
            logger.info("🤖 Initializing ML prediction model...")
            self.ml_model = PricePredictionModel()
            await self.ml_model.load_model()
            
            # Initialize vector search
            logger.info("🔍 Initializing vector search engine...")
            self.vector_search = VectorSearchEngine()
            await self.vector_search.initialize()
            
            # Initialize RAG engine
            logger.info("📚 Initializing RAG engine...")
            self.rag_engine = RAGEngine(self.vector_search)
            await self.rag_engine.initialize()
            
            # Initialize LangChain manager
            logger.info("🔗 Initializing LangChain manager...")
            self.langchain_manager = LangChainManager(self.rag_engine)
            await self.langchain_manager.initialize()
            
            self.is_initialized = True
            logger.info("✅ All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def predict(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main prediction method with full framework integration
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request_data)
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info("📋 Returning cached prediction")
                return cached_result
            
            # Extract features for ML model
            features = self._extract_features(request_data)
            
            # Get ML prediction
            ml_prediction = await self.ml_model.predict(features)
            
            # Get similar vehicles via vector search
            similar_vehicles = await self.vector_search.find_similar_vehicles(
                request_data, limit=5
            )
            
            # Get market insights via RAG
            market_insights = await self.rag_engine.get_market_insights(
                request_data, similar_vehicles
            )
            
            # Generate explanation via LangChain
            explanation = await self.langchain_manager.generate_explanation(
                request_data, ml_prediction, similar_vehicles, market_insights
            )
            
            # Combine results
            result = {
                "predicted_price": ml_prediction["price"],
                "confidence_score": ml_prediction["confidence"],
                "price_range": ml_prediction["price_range"],
                "explanation": explanation,
                "similar_vehicles": similar_vehicles,
                "market_insights": market_insights,
                "model_version": ml_prediction["model_version"],
                "processing_time_ms": (time.time() - start_time) * 1000
            }
            
            # Cache the result
            await self.cache.set(cache_key, result, ttl=3600)  # 1 hour TTL
            
            # Record metrics
            await self.metrics.record_prediction(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    async def predict_with_langchain(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prediction using primarily LangChain integration"""
        return await self.langchain_manager.predict_with_chain(request_data)
    
    async def predict_with_rag(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prediction using primarily RAG approach"""
        return await self.rag_engine.predict_with_rag(request_data)
    
    async def search_similar_vehicles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vehicles using vector search"""
        return await self.vector_search.search(query, limit)
    
    async def trigger_training(self, request_data: Dict[str, Any], background_tasks) -> str:
        """Trigger model retraining in background"""
        task_id = str(uuid.uuid4())
        
        # Schedule background training
        background_tasks.add_task(
            self._background_training,
            task_id,
            request_data
        )
        
        self.training_tasks[task_id] = {
            "status": "started",
            "started_at": datetime.now(),
            "request": request_data
        }
        
        return task_id
    
    async def _background_training(self, task_id: str, request_data: Dict[str, Any]):
        """Background task for model training"""
        try:
            logger.info(f"🏋️ Starting background training task: {task_id}")
            
            # Update task status
            self.training_tasks[task_id]["status"] = "training"
            
            # Load new training data
            training_data = await self.data_pipeline.load_training_data(
                request_data.get("data_source")
            )
            
            # Retrain ML model
            await self.ml_model.retrain(training_data)
            
            # Update vector search index
            await self.vector_search.update_index(training_data)
            
            # Update RAG knowledge base
            await self.rag_engine.update_knowledge_base(training_data)
            
            # Mark task as completed
            self.training_tasks[task_id]["status"] = "completed"
            self.training_tasks[task_id]["completed_at"] = datetime.now()
            
            logger.info(f"✅ Training task completed: {task_id}")
            
        except Exception as e:
            logger.error(f"❌ Training task failed: {task_id}, error: {e}")
            self.training_tasks[task_id]["status"] = "failed"
            self.training_tasks[task_id]["error"] = str(e)
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all components"""
        health_status = {
            "status": "healthy",
            "services": {},
            "version": settings.app_version,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }
        
        try:
            # Check ML model
            if self.ml_model:
                model_health = await self.ml_model.health_check()
                health_status["services"]["ml_model"] = "healthy" if model_health else "unhealthy"
            
            # Check vector search
            if self.vector_search:
                vector_health = await self.vector_search.health_check()
                health_status["services"]["vector_search"] = "healthy" if vector_health else "unhealthy"
            
            # Check RAG engine
            if self.rag_engine:
                rag_health = await self.rag_engine.health_check()
                health_status["services"]["rag_engine"] = "healthy" if rag_health else "unhealthy"
            
            # Check LangChain
            if self.langchain_manager:
                langchain_health = await self.langchain_manager.health_check()
                health_status["services"]["langchain"] = "healthy" if langchain_health else "unhealthy"
            
            # Check if any service is unhealthy
            if "unhealthy" in health_status["services"].values():
                health_status["status"] = "degraded"
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get application metrics"""
        if self.metrics:
            return await self.metrics.get_metrics()
        return {}
    
    async def cleanup(self):
        """Cleanup all resources"""
        logger.info("🧹 Cleaning up orchestrator resources...")
        
        if self.ml_model:
            await self.ml_model.cleanup()
        if self.vector_search:
            await self.vector_search.cleanup()
        if self.rag_engine:
            await self.rag_engine.cleanup()
        if self.langchain_manager:
            await self.langchain_manager.cleanup()
        if self.cache:
            await self.cache.cleanup()
    
    def _extract_features(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from request data"""
        return {
            "vehicle_age": request_data.get("vehicle_age"),
            "mileage": request_data.get("mileage"),
            "vehicle_type": request_data.get("vehicle_type", "car"),
            "brand": request_data.get("brand"),
            "model": request_data.get("model"),
            "fuel_type": request_data.get("fuel_type", "gasoline"),
            "transmission": request_data.get("transmission", "automatic"),
            "condition": request_data.get("condition", "good"),
            "location": request_data.get("location")
        }
    
    def _generate_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        import hashlib
        import json
        
        # Create deterministic hash of request data
        data_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
