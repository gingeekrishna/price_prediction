"""
FastAPI Main Application
Production-ready API with all framework integrations
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any, List
import uvicorn

from ..config.settings import settings
from ..services.orchestrator import PredictionOrchestrator
from ..models.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    HealthResponse,
    TrainingRequest,
    TrainingResponse
)
from ..utils.logging_config import setup_logging
from ..utils.monitoring import metrics_middleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: PredictionOrchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    
    # Startup
    logger.info("🚀 Starting Vehicle Price Prediction API...")
    orchestrator = PredictionOrchestrator()
    await orchestrator.initialize()
    logger.info("✅ All systems initialized successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Vehicle Price Prediction API...")
    if orchestrator:
        await orchestrator.cleanup()
    logger.info("✅ Cleanup completed!")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready Vehicle Price Prediction API with LangChain, RAG, and Vector Search",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware (commented out due to middleware signature issue)
# TODO: Fix metrics middleware implementation
# app.add_middleware(metrics_middleware)

# Dependency to get orchestrator
async def get_orchestrator() -> PredictionOrchestrator:
    """Get the global orchestrator instance"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return orchestrator

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return f"""
    <html>
        <head><title>{settings.app_name}</title></head>
        <body>
            <h1>{settings.app_name}</h1>
            <h2>Version: {settings.app_version}</h2>
            <p>Environment: {settings.environment}</p>
            <ul>
                <li><a href="/docs">API Documentation (Swagger)</a></li>
                <li><a href="/redoc">API Documentation (ReDoc)</a></li>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/metrics">Metrics</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse)
async def health_check(orch: PredictionOrchestrator = Depends(get_orchestrator)):
    """Health check endpoint"""
    try:
        health_status = await orch.health_check()
        return HealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/predict", response_model=PredictionResponse)
async def predict_price(
    request: PredictionRequest,
    orch: PredictionOrchestrator = Depends(get_orchestrator)
):
    """Main prediction endpoint with all framework integrations"""
    try:
        logger.info(f"Prediction request: {request}")
        result = await orch.predict(request.dict())
        return PredictionResponse(**result)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/langchain", response_model=PredictionResponse)
async def predict_with_langchain(
    request: PredictionRequest,
    orch: PredictionOrchestrator = Depends(get_orchestrator)
):
    """Prediction with LangChain integration"""
    try:
        result = await orch.predict_with_langchain(request.dict())
        return PredictionResponse(**result)
    except Exception as e:
        logger.error(f"LangChain prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/rag", response_model=PredictionResponse)
async def predict_with_rag(
    request: PredictionRequest,
    orch: PredictionOrchestrator = Depends(get_orchestrator)
):
    """Prediction with RAG (Retrieval-Augmented Generation)"""
    try:
        result = await orch.predict_with_rag(request.dict())
        return PredictionResponse(**result)
    except Exception as e:
        logger.error(f"RAG prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/similar")
async def search_similar_vehicles(
    query: str,
    limit: int = 5,
    orch: PredictionOrchestrator = Depends(get_orchestrator)
):
    """Vector search for similar vehicles"""
    try:
        results = await orch.search_similar_vehicles(query, limit)
        return {"query": query, "results": results}
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train", response_model=TrainingResponse)
async def trigger_training(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    orch: PredictionOrchestrator = Depends(get_orchestrator)
):
    """Trigger model retraining"""
    try:
        task_id = await orch.trigger_training(request.dict(), background_tasks)
        return TrainingResponse(task_id=task_id, status="started")
    except Exception as e:
        logger.error(f"Training trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics(orch: PredictionOrchestrator = Depends(get_orchestrator)):
    """Get application metrics"""
    try:
        metrics = await orch.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )
