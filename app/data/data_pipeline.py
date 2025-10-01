"""
Data Pipeline
Automated data collection, processing, and model training pipeline
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

from ..config.settings import settings, get_data_path
from ..models.price_predictor import PricePredictionModel
from ..vector_search.search_engine import VectorSearchEngine
from ..rag.rag_engine import RAGEngine

logger = logging.getLogger(__name__)

class DataPipeline:
    """
    Production data pipeline for automated vehicle data collection,
    processing, validation, and model training
    """
    
    def __init__(self):
        self.data_path = get_data_path()
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.ml_model = None
        self.vector_search = None
        self.rag_engine = None
        
        self.pipeline_stats = {
            "last_run": None,
            "total_runs": 0,
            "success_rate": 1.0,
            "data_quality_score": 0.8,
            "records_processed": 0
        }
        
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def initialize(self):
        """Initialize data pipeline components"""
        try:
            logger.info("🔄 Initializing data pipeline...")
            
            # Initialize ML model
            self.ml_model = PricePredictionModel()
            await self.ml_model.load_model()
            
            # Initialize vector search
            self.vector_search = VectorSearchEngine()
            await self.vector_search.initialize()
            
            # Initialize RAG engine
            self.rag_engine = RAGEngine()
            await self.rag_engine.initialize()
            
            # Schedule automated runs
            self._schedule_pipeline()
            
            logger.info("✅ Data pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Data pipeline initialization failed: {e}")
            raise
    
    async def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete data pipeline"""
        if self.is_running:
            logger.warning("⚠️ Pipeline already running, skipping this run")
            return {"status": "skipped", "reason": "already_running"}
        
        start_time = datetime.now()
        self.is_running = True
        
        try:
            logger.info("🚀 Starting full data pipeline run...")
            
            results = {
                "start_time": start_time.isoformat(),
                "stages": {},
                "status": "running"
            }
            
            # Stage 1: Data Collection
            logger.info("📊 Stage 1: Data Collection")
            collection_result = await self._collect_data()
            results["stages"]["data_collection"] = collection_result
            
            # Stage 2: Data Validation and Cleaning
            logger.info("🔍 Stage 2: Data Validation")
            validation_result = await self._validate_and_clean_data(collection_result.get("data", []))
            results["stages"]["data_validation"] = validation_result
            
            # Stage 3: Feature Engineering
            logger.info("⚙️ Stage 3: Feature Engineering")
            feature_result = await self._engineer_features(validation_result.get("cleaned_data", []))
            results["stages"]["feature_engineering"] = feature_result
            
            # Stage 4: Model Training
            logger.info("🤖 Stage 4: Model Training")
            training_result = await self._train_models(feature_result.get("processed_data"))
            results["stages"]["model_training"] = training_result
            
            # Stage 5: Index Updates
            logger.info("🔄 Stage 5: Index Updates")
            index_result = await self._update_indexes(validation_result.get("cleaned_data", []))
            results["stages"]["index_updates"] = index_result
            
            # Stage 6: Quality Assessment
            logger.info("📈 Stage 6: Quality Assessment")
            quality_result = await self._assess_quality(training_result)
            results["stages"]["quality_assessment"] = quality_result
            
            # Update pipeline stats
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "completed",
                "success": True
            })
            
            self._update_pipeline_stats(True, len(validation_result.get("cleaned_data", [])))
            
            logger.info(f"✅ Data pipeline completed successfully in {duration:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"❌ Data pipeline failed: {e}")
            self._update_pipeline_stats(False, 0)
            
            return {
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "success": False
            }
            
        finally:
            self.is_running = False
    
    async def _collect_data(self) -> Dict[str, Any]:
        """Collect vehicle data from various sources"""
        try:
            collected_data = []
            
            # Source 1: Mock API data (simulating real data sources)
            api_data = await self._fetch_api_data()
            collected_data.extend(api_data)
            
            # Source 2: File-based data
            file_data = await self._load_file_data()
            collected_data.extend(file_data)
            
            # Source 3: Web scraping simulation
            web_data = await self._simulate_web_scraping()
            collected_data.extend(web_data)
            
            return {
                "status": "success",
                "sources": ["api", "files", "web"],
                "total_records": len(collected_data),
                "data": collected_data
            }
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "data": []
            }
    
    async def _fetch_api_data(self) -> List[Dict[str, Any]]:
        """Simulate fetching data from external APIs"""
        # In production, this would connect to real vehicle data APIs
        # like Kelley Blue Book, Edmunds, CarGurus, etc.
        
        mock_api_data = []
        
        brands = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Volkswagen", "Nissan"]
        models = {
            "Toyota": ["Camry", "Corolla", "Prius", "RAV4", "Highlander"],
            "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit"],
            "Ford": ["F-150", "Escape", "Explorer", "Mustang", "Focus"],
            "BMW": ["3 Series", "5 Series", "X3", "X5", "i3"],
            "Mercedes": ["C-Class", "E-Class", "GLC", "GLE", "A-Class"],
            "Audi": ["A3", "A4", "Q3", "Q5", "Q7"],
            "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf"],
            "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Leaf"]
        }
        
        # Generate realistic vehicle data
        for i in range(50):  # Simulate 50 new records
            brand = np.random.choice(brands)
            model = np.random.choice(models[brand])
            year = np.random.randint(2015, 2024)
            mileage = np.random.randint(5000, 150000)
            
            # Price calculation based on realistic factors
            base_price = {
                "Toyota": 25000, "Honda": 24000, "Ford": 28000, "BMW": 45000,
                "Mercedes": 50000, "Audi": 42000, "Volkswagen": 26000, "Nissan": 23000
            }[brand]
            
            # Depreciation and adjustments
            age = 2024 - year
            depreciation = 0.85 ** age  # 15% per year
            mileage_factor = max(0.6, 1 - (mileage / 200000) * 0.4)
            
            price = int(base_price * depreciation * mileage_factor * np.random.uniform(0.9, 1.1))
            
            vehicle = {
                "id": f"api_{i}",
                "brand": brand,
                "model": model,
                "year": year,
                "mileage": mileage,
                "price": price,
                "condition": np.random.choice(["excellent", "good", "fair"], p=[0.2, 0.6, 0.2]),
                "vehicle_type": np.random.choice(["sedan", "suv", "truck", "hatchback"], p=[0.4, 0.3, 0.2, 0.1]),
                "fuel_type": np.random.choice(["gasoline", "hybrid", "electric"], p=[0.8, 0.15, 0.05]),
                "transmission": np.random.choice(["automatic", "manual"], p=[0.9, 0.1]),
                "source": "api",
                "timestamp": datetime.now().isoformat()
            }
            
            mock_api_data.append(vehicle)
        
        logger.info(f"📡 Collected {len(mock_api_data)} records from API sources")
        return mock_api_data
    
    async def _load_file_data(self) -> List[Dict[str, Any]]:
        """Load data from local files"""
        try:
            file_data = []
            
            # Check for CSV files in data directory
            csv_files = list(self.data_path.glob("*.csv"))
            
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    records = df.to_dict('records')
                    
                    # Add metadata
                    for record in records:
                        record['source'] = 'file'
                        record['file_name'] = csv_file.name
                        record['timestamp'] = datetime.now().isoformat()
                    
                    file_data.extend(records)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {csv_file}: {e}")
            
            logger.info(f"📁 Loaded {len(file_data)} records from {len(csv_files)} files")
            return file_data
            
        except Exception as e:
            logger.error(f"❌ File data loading failed: {e}")
            return []
    
    async def _simulate_web_scraping(self) -> List[Dict[str, Any]]:
        """Simulate web scraping from vehicle listing sites"""
        # In production, this would scrape sites like AutoTrader, Cars.com, etc.
        # with proper rate limiting and respect for robots.txt
        
        web_data = []
        
        # Simulate 30 scraped listings
        for i in range(30):
            vehicle = {
                "id": f"web_{i}",
                "brand": np.random.choice(["Toyota", "Honda", "Ford", "Chevrolet", "Nissan"]),
                "model": "Unknown",  # Would be extracted from title
                "year": np.random.randint(2016, 2024),
                "mileage": np.random.randint(10000, 120000),
                "price": np.random.randint(15000, 60000),
                "condition": "good",  # Default assumption
                "location": np.random.choice(["CA", "TX", "FL", "NY", "IL"]),
                "source": "web_scraping",
                "timestamp": datetime.now().isoformat()
            }
            web_data.append(vehicle)
        
        logger.info(f"🌐 Simulated collection of {len(web_data)} records from web sources")
        return web_data
    
    async def _validate_and_clean_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and clean collected data"""
        try:
            if not raw_data:
                return {"status": "success", "cleaned_data": [], "quality_score": 0}
            
            df = pd.DataFrame(raw_data)
            original_count = len(df)
            
            # Data validation rules
            validation_results = {}
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['brand', 'model', 'year', 'mileage'], keep='first')
            validation_results['duplicates_removed'] = original_count - len(df)
            
            # Price validation
            df = df[(df['price'] > 1000) & (df['price'] < 200000)]
            validation_results['price_outliers_removed'] = original_count - len(df)
            
            # Year validation
            current_year = datetime.now().year
            df = df[(df['year'] >= 1990) & (df['year'] <= current_year + 1)]
            validation_results['year_outliers_removed'] = original_count - len(df)
            
            # Mileage validation
            df = df[(df['mileage'] >= 0) & (df['mileage'] <= 500000)]
            validation_results['mileage_outliers_removed'] = original_count - len(df)
            
            # Fill missing values
            df['condition'] = df['condition'].fillna('good')
            df['vehicle_type'] = df['vehicle_type'].fillna('sedan')
            df['fuel_type'] = df['fuel_type'].fillna('gasoline')
            df['transmission'] = df['transmission'].fillna('automatic')
            
            # Add derived features
            df['vehicle_age'] = current_year - df['year']
            df['price_per_mile'] = df['price'] / (df['mileage'] + 1)  # Avoid division by zero
            
            # Calculate quality score
            quality_score = len(df) / original_count if original_count > 0 else 0
            
            cleaned_data = df.to_dict('records')
            
            logger.info(f"🔍 Data validation: {original_count} → {len(cleaned_data)} records (quality: {quality_score:.2f})")
            
            return {
                "status": "success",
                "original_count": original_count,
                "cleaned_count": len(cleaned_data),
                "quality_score": quality_score,
                "validation_results": validation_results,
                "cleaned_data": cleaned_data
            }
            
        except Exception as e:
            logger.error(f"❌ Data validation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "cleaned_data": []
            }
    
    async def _engineer_features(self, cleaned_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Engineer features for machine learning"""
        try:
            if not cleaned_data:
                return {"status": "success", "processed_data": None}
            
            df = pd.DataFrame(cleaned_data)
            
            # Feature engineering
            features_added = []
            
            # Brand popularity score
            brand_counts = df['brand'].value_counts()
            df['brand_popularity'] = df['brand'].map(brand_counts)
            features_added.append('brand_popularity')
            
            # Age categories
            df['age_category'] = pd.cut(df['vehicle_age'], 
                                      bins=[0, 3, 7, 15, 100], 
                                      labels=['new', 'recent', 'mature', 'old'])
            features_added.append('age_category')
            
            # Mileage categories
            df['mileage_category'] = pd.cut(df['mileage'], 
                                          bins=[0, 30000, 80000, 150000, 1000000], 
                                          labels=['low', 'medium', 'high', 'very_high'])
            features_added.append('mileage_category')
            
            # Price categories
            df['price_category'] = pd.cut(df['price'], 
                                        bins=[0, 20000, 40000, 60000, 1000000], 
                                        labels=['budget', 'mid_range', 'premium', 'luxury'])
            features_added.append('price_category')
            
            # Depreciation rate
            df['depreciation_rate'] = (50000 - df['price']) / (df['vehicle_age'] + 1)  # Simplified
            features_added.append('depreciation_rate')
            
            logger.info(f"⚙️ Feature engineering: Added {len(features_added)} features")
            
            return {
                "status": "success",
                "features_added": features_added,
                "processed_data": df,
                "feature_count": len(df.columns)
            }
            
        except Exception as e:
            logger.error(f"❌ Feature engineering failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "processed_data": None
            }
    
    async def _train_models(self, processed_data) -> Dict[str, Any]:
        """Train machine learning models"""
        try:
            if processed_data is None or len(processed_data) < 10:
                logger.warning("⚠️ Insufficient data for model training")
                return {
                    "status": "skipped",
                    "reason": "insufficient_data"
                }
            
            # Train ML model
            training_data = processed_data.to_dict('records')
            
            if self.ml_model:
                training_result = await self.ml_model.train(training_data)
                
                return {
                    "status": "success",
                    "model_performance": training_result,
                    "training_samples": len(training_data)
                }
            else:
                return {
                    "status": "failed",
                    "error": "ML model not initialized"
                }
                
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _update_indexes(self, cleaned_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update search and RAG indexes"""
        try:
            results = {}
            
            # Update vector search index
            if self.vector_search and cleaned_data:
                await self.vector_search.update_index(cleaned_data)
                results['vector_search'] = "updated"
            
            # Update RAG knowledge base
            if self.rag_engine and cleaned_data:
                # Convert data to knowledge format
                await self.rag_engine.update_knowledge_base(pd.DataFrame(cleaned_data))
                results['rag_knowledge'] = "updated"
            
            return {
                "status": "success",
                "updates": results
            }
            
        except Exception as e:
            logger.error(f"❌ Index update failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _assess_quality(self, training_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall pipeline quality"""
        try:
            quality_metrics = {
                "data_quality": self.pipeline_stats.get("data_quality_score", 0),
                "model_performance": 0,
                "pipeline_success": training_result.get("status") == "success"
            }
            
            # Extract model performance if available
            if training_result.get("model_performance"):
                perf = training_result["model_performance"]
                if isinstance(perf, dict) and "accuracy" in perf:
                    quality_metrics["model_performance"] = perf["accuracy"]
                elif isinstance(perf, dict) and "r2_score" in perf:
                    quality_metrics["model_performance"] = max(0, perf["r2_score"])
                else:
                    quality_metrics["model_performance"] = 0.8  # Default
            
            # Overall quality score
            overall_quality = (
                quality_metrics["data_quality"] * 0.4 +
                quality_metrics["model_performance"] * 0.4 +
                (1.0 if quality_metrics["pipeline_success"] else 0.0) * 0.2
            )
            
            quality_metrics["overall_score"] = overall_quality
            
            return {
                "status": "success",
                "quality_metrics": quality_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Quality assessment failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _schedule_pipeline(self):
        """Schedule automated pipeline runs"""
        try:
            if not SCHEDULE_AVAILABLE:
                logger.warning("⚠️ Schedule module not available, automated scheduling disabled")
                return
            
            # Schedule daily run at 2 AM
            schedule.every().day.at("02:00").do(lambda: asyncio.create_task(self.run_full_pipeline()))
            
            # Schedule weekly full retraining on Sundays
            schedule.every().sunday.at("01:00").do(lambda: asyncio.create_task(self._full_retrain()))
            
            logger.info("📅 Pipeline scheduling configured")
            
        except Exception as e:
            logger.error(f"❌ Pipeline scheduling failed: {e}")
    
    async def _full_retrain(self):
        """Perform full model retraining"""
        logger.info("🔄 Starting full model retraining...")
        
        try:
            # Load all historical data
            all_data = await self._load_all_historical_data()
            
            # Run full pipeline with historical data
            if all_data:
                training_data = pd.DataFrame(all_data).to_dict('records')
                
                if self.ml_model:
                    result = await self.ml_model.train(training_data)
                    logger.info(f"✅ Full retraining completed: {result}")
                
        except Exception as e:
            logger.error(f"❌ Full retraining failed: {e}")
    
    async def _load_all_historical_data(self) -> List[Dict[str, Any]]:
        """Load all historical data for retraining"""
        try:
            historical_data = []
            
            # Load from all CSV files in data directory
            for csv_file in self.data_path.glob("*.csv"):
                try:
                    df = pd.read_csv(csv_file)
                    historical_data.extend(df.to_dict('records'))
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {csv_file}: {e}")
            
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Historical data loading failed: {e}")
            return []
    
    def _update_pipeline_stats(self, success: bool, records_processed: int):
        """Update pipeline statistics"""
        self.pipeline_stats["last_run"] = datetime.now().isoformat()
        self.pipeline_stats["total_runs"] += 1
        self.pipeline_stats["records_processed"] += records_processed
        
        # Update success rate
        if success:
            current_rate = self.pipeline_stats["success_rate"]
            total_runs = self.pipeline_stats["total_runs"]
            self.pipeline_stats["success_rate"] = (current_rate * (total_runs - 1) + 1.0) / total_runs
        else:
            current_rate = self.pipeline_stats["success_rate"]
            total_runs = self.pipeline_stats["total_runs"]
            self.pipeline_stats["success_rate"] = (current_rate * (total_runs - 1)) / total_runs
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "is_running": self.is_running,
            "stats": self.pipeline_stats,
            "components": {
                "ml_model": self.ml_model is not None,
                "vector_search": self.vector_search is not None,
                "rag_engine": self.rag_engine is not None
            },
            "next_scheduled_run": "Daily at 02:00",
            "data_path": str(self.data_path)
        }
    
    async def health_check(self) -> bool:
        """Check pipeline health"""
        try:
            # Check if components are initialized
            if not all([self.ml_model, self.vector_search, self.rag_engine]):
                return False
            
            # Check if data path is accessible
            if not self.data_path.exists():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup pipeline resources"""
        logger.info("🧹 Cleaning up data pipeline resources...")
        self.is_running = False
        
        if self.ml_model:
            await self.ml_model.cleanup()
        if self.vector_search:
            await self.vector_search.cleanup()
        if self.rag_engine:
            await self.rag_engine.cleanup()
        
        if self.executor:
            self.executor.shutdown(wait=True)
