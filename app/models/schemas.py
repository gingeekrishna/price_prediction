"""
Pydantic Models/Schemas for API Request/Response
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class VehicleType(str, Enum):
    """Vehicle type enumeration"""
    CAR = "car"
    TRUCK = "truck"
    SUV = "suv"
    MOTORCYCLE = "motorcycle"
    VAN = "van"

class PredictionRequest(BaseModel):
    """Request model for price prediction"""
    vehicle_age: int = Field(..., ge=0, le=50, description="Age of vehicle in years")
    mileage: int = Field(..., ge=0, le=1000000, description="Vehicle mileage")
    vehicle_type: Optional[VehicleType] = Field(default=VehicleType.CAR, description="Type of vehicle")
    brand: Optional[str] = Field(default=None, description="Vehicle brand")
    model: Optional[str] = Field(default=None, description="Vehicle model")
    fuel_type: Optional[str] = Field(default="gasoline", description="Fuel type")
    transmission: Optional[str] = Field(default="automatic", description="Transmission type")
    condition: Optional[str] = Field(default="good", description="Vehicle condition")
    location: Optional[str] = Field(default=None, description="Vehicle location")
    additional_features: Optional[Dict[str, Any]] = Field(default={}, description="Additional vehicle features")
    
    @validator('vehicle_age')
    def validate_age(cls, v):
        if v < 0 or v > 50:
            raise ValueError('Vehicle age must be between 0 and 50 years')
        return v
    
    @validator('mileage')
    def validate_mileage(cls, v):
        if v < 0:
            raise ValueError('Mileage cannot be negative')
        return v

class PredictionResponse(BaseModel):
    """Response model for price prediction"""
    predicted_price: float = Field(..., description="Predicted vehicle price")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence score")
    price_range: Dict[str, float] = Field(..., description="Price range (min, max)")
    explanation: str = Field(..., description="AI-generated explanation")
    similar_vehicles: List[Dict[str, Any]] = Field(default=[], description="Similar vehicles from vector search")
    market_insights: Dict[str, Any] = Field(default={}, description="Market trend insights")
    model_version: str = Field(..., description="ML model version used")
    timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(..., description="Individual service statuses")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Uptime in seconds")

class TrainingRequest(BaseModel):
    """Request model for model training"""
    data_source: Optional[str] = Field(default=None, description="Data source path or URL")
    retrain_all: bool = Field(default=False, description="Whether to retrain all models")
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5, description="Validation data split ratio")
    hyperparameters: Optional[Dict[str, Any]] = Field(default={}, description="Custom hyperparameters")

class TrainingResponse(BaseModel):
    """Response model for training trigger"""
    task_id: str = Field(..., description="Training task ID")
    status: str = Field(..., description="Training status")
    started_at: datetime = Field(default_factory=datetime.now, description="Training start time")
    estimated_duration_minutes: Optional[int] = Field(default=None, description="Estimated training duration")

class VectorSearchRequest(BaseModel):
    """Request model for vector search"""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="Search filters")
    similarity_threshold: Optional[float] = Field(default=0.7, ge=0, le=1, description="Similarity threshold")

class VectorSearchResponse(BaseModel):
    """Response model for vector search"""
    query: str = Field(..., description="Original search query")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results found")
    processing_time_ms: float = Field(..., description="Search processing time")

class RAGRequest(BaseModel):
    """Request model for RAG (Retrieval-Augmented Generation)"""
    query: str = Field(..., min_length=1, description="RAG query")
    context_limit: int = Field(default=5, ge=1, le=20, description="Maximum context documents")
    include_sources: bool = Field(default=True, description="Include source documents in response")

class RAGResponse(BaseModel):
    """Response model for RAG"""
    query: str = Field(..., description="Original query")
    response: str = Field(..., description="Generated response")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source documents used")
    confidence: float = Field(..., ge=0, le=1, description="Response confidence")
    processing_time_ms: float = Field(..., description="Processing time")

class MetricsResponse(BaseModel):
    """Application metrics response"""
    total_predictions: int = Field(..., description="Total predictions made")
    avg_response_time_ms: float = Field(..., description="Average response time")
    model_accuracy: float = Field(..., description="Current model accuracy")
    active_users: int = Field(..., description="Active users count")
    system_resources: Dict[str, Any] = Field(..., description="System resource usage")
    last_updated: datetime = Field(default_factory=datetime.now, description="Metrics last updated")
