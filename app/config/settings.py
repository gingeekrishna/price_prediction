"""
Configuration Settings for Vehicle Price Prediction System
Handles environment variables, model paths, and framework configurations
"""

import os
from typing import Optional, List
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic import BaseSettings, Field
    except ImportError:
        # Fallback for older versions
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        def Field(*args, **kwargs):
            return None

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Settings
    app_name: str = "Vehicle Price Prediction System"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    # Database Settings
    database_url: str = Field(default="sqlite:///./predictions.db", env="DATABASE_URL")
    
    # ML Model Settings
    model_path: str = Field(default="./models/price_prediction_model.pkl", env="MODEL_PATH")
    model_retrain_interval: int = Field(default=24, env="MODEL_RETRAIN_INTERVAL")  # hours
    model_confidence_threshold: float = Field(default=0.85, env="MODEL_CONFIDENCE_THRESHOLD")
    
    # LangChain Settings
    # AI/LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Ollama Configuration
    use_ollama: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text:latest"
    claude_api_key: Optional[str] = Field(default=None, env="CLAUDE_API_KEY")
    bedrock_region: str = Field(default="us-east-1", env="BEDROCK_REGION")
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # Vector Search Settings
    vector_db_path: str = Field(default="./vector_db", env="VECTOR_DB_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    vector_search_k: int = Field(default=5, env="VECTOR_SEARCH_K")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    
    # RAG Settings
    knowledge_base_path: str = Field(default="./knowledge_docs", env="KNOWLEDGE_BASE_PATH")
    chunk_size: int = Field(default=1000, env="RAG_CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="RAG_CHUNK_OVERLAP")
    
    # Data Pipeline Settings
    data_source_path: str = Field(default="./data", env="DATA_SOURCE_PATH")
    batch_size: int = Field(default=1000, env="BATCH_SIZE")
    max_training_samples: int = Field(default=100000, env="MAX_TRAINING_SAMPLES")
    
    # Monitoring & Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")  # seconds
    
    # Security Settings
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Helper functions for path management
def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent

def get_models_path() -> Path:
    """Get the models directory path"""
    return get_project_root() / "models"

def get_data_path() -> Path:
    """Get the data directory path"""
    return get_project_root() / "data"

def get_logs_path() -> Path:
    """Get the logs directory path"""
    return get_project_root() / "logs"

def get_cache_path() -> Path:
    """Get the cache directory path"""
    return get_project_root() / "cache"

def get_knowledge_base_path() -> Path:
    """Get the knowledge base directory path"""
    return get_project_root() / "knowledge_base"

def get_vector_cache_path() -> Path:
    """Get the vector cache directory path"""
    return get_cache_path() / "vectors"

# Helper functions
def get_model_path() -> Path:
    """Get absolute path to ML model"""
    return Path(settings.model_path).resolve()

def get_vector_db_path() -> Path:
    """Get absolute path to vector database"""
    return Path(settings.vector_db_path).resolve()

def get_knowledge_base_path() -> Path:
    """Get absolute path to knowledge base"""
    return Path(settings.knowledge_base_path).resolve()

def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment.lower() == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return settings.environment.lower() == "development"
