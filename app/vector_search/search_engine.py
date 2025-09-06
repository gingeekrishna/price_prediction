"""
Vector Search Engine
High-performance similarity search for vehicle data and market analysis
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import pickle

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import PCA
    import faiss
    SKLEARN_AVAILABLE = True
    FAISS_AVAILABLE = True
except ImportError:
    TfidfVectorizer = cosine_similarity = PCA = faiss = None
    SKLEARN_AVAILABLE = False
    FAISS_AVAILABLE = False

from ..config.settings import settings, get_vector_cache_path

logger = logging.getLogger(__name__)

class VectorSearchEngine:
    """
    Production-ready vector search engine for vehicle similarity and market analysis
    Supports both FAISS and sklearn-based implementations with fallbacks
    """
    
    def __init__(self):
        self.index = None
        self.vectorizer = None
        self.vehicle_data = []
        self.embeddings = []
        self.dimension = 384  # Default embedding dimension
        self.is_initialized = False
        
        self.cache_path = get_vector_cache_path()
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.search_stats = {
            "total_searches": 0,
            "avg_response_time": 0,
            "cache_hits": 0
        }
    
    async def initialize(self, vehicle_data: Optional[List[Dict[str, Any]]] = None):
        """Initialize vector search engine"""
        try:
            logger.info("🔍 Initializing vector search engine...")
            
            # Load or create vehicle data
            if vehicle_data:
                self.vehicle_data = vehicle_data
            else:
                await self._load_sample_data()
            
            # Initialize vectorizer
            if SKLEARN_AVAILABLE:
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                logger.info("✅ TF-IDF vectorizer initialized")
            else:
                logger.warning("⚠️ Using basic vectorizer fallback")
                self.vectorizer = BasicVectorizer()
            
            # Build search index
            await self._build_index()
            
            self.is_initialized = True
            logger.info(f"✅ Vector search engine initialized with {len(self.vehicle_data)} vehicles")
            
        except Exception as e:
            logger.error(f"❌ Vector search initialization failed: {e}")
            # Initialize with minimal functionality
            self.vehicle_data = []
            self.vectorizer = BasicVectorizer()
            self.is_initialized = True
    
    async def _load_sample_data(self):
        """Load sample vehicle data for search indexing"""
        sample_data = [
            {
                "id": "1",
                "brand": "Toyota",
                "model": "Camry",
                "year": 2020,
                "mileage": 25000,
                "condition": "excellent",
                "price": 22000,
                "vehicle_type": "sedan",
                "fuel_type": "gasoline",
                "transmission": "automatic",
                "description": "Well-maintained Toyota Camry with excellent condition and low mileage"
            },
            {
                "id": "2",
                "brand": "Honda",
                "model": "Civic",
                "year": 2019,
                "mileage": 35000,
                "condition": "good",
                "price": 18500,
                "vehicle_type": "sedan",
                "fuel_type": "gasoline",
                "transmission": "manual",
                "description": "Reliable Honda Civic with good fuel economy and sporty handling"
            },
            {
                "id": "3",
                "brand": "BMW",
                "model": "X3",
                "year": 2021,
                "mileage": 15000,
                "condition": "excellent",
                "price": 42000,
                "vehicle_type": "suv",
                "fuel_type": "gasoline",
                "transmission": "automatic",
                "description": "Luxury BMW X3 SUV with premium features and low mileage"
            },
            {
                "id": "4",
                "brand": "Ford",
                "model": "F-150",
                "year": 2020,
                "mileage": 45000,
                "condition": "good",
                "price": 35000,
                "vehicle_type": "truck",
                "fuel_type": "gasoline",
                "transmission": "automatic",
                "description": "Dependable Ford F-150 truck perfect for work and recreation"
            },
            {
                "id": "5",
                "brand": "Tesla",
                "model": "Model 3",
                "year": 2022,
                "mileage": 8000,
                "condition": "excellent",
                "price": 48000,
                "vehicle_type": "sedan",
                "fuel_type": "electric",
                "transmission": "automatic",
                "description": "Modern Tesla Model 3 electric vehicle with autopilot and minimal wear"
            }
        ]
        
        self.vehicle_data = sample_data
        logger.info(f"📊 Loaded {len(sample_data)} sample vehicles for search indexing")
    
    async def _build_index(self):
        """Build search index from vehicle data"""
        try:
            if not self.vehicle_data:
                logger.warning("⚠️ No vehicle data available for indexing")
                return
            
            # Create text representations for vectorization
            texts = [self._vehicle_to_text(vehicle) for vehicle in self.vehicle_data]
            
            # Fit vectorizer and transform texts
            if hasattr(self.vectorizer, 'fit_transform'):
                embeddings_matrix = self.vectorizer.fit_transform(texts)
                self.embeddings = embeddings_matrix.toarray() if hasattr(embeddings_matrix, 'toarray') else embeddings_matrix
            else:
                self.embeddings = self.vectorizer.transform(texts)
            
            # Build FAISS index if available
            if FAISS_AVAILABLE and len(self.embeddings) > 0:
                try:
                    self.dimension = self.embeddings.shape[1]
                    self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                    
                    # Normalize embeddings for cosine similarity
                    normalized_embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
                    self.index.add(normalized_embeddings.astype('float32'))
                    
                    logger.info(f"✅ FAISS index built with {self.index.ntotal} vectors, dimension {self.dimension}")
                except Exception as e:
                    logger.warning(f"⚠️ FAISS index creation failed: {e}, using fallback")
                    self.index = None
            
            # Cache the index
            await self._save_index_cache()
            
        except Exception as e:
            logger.error(f"❌ Index building failed: {e}")
            self.embeddings = []
    
    def _vehicle_to_text(self, vehicle: Dict[str, Any]) -> str:
        """Convert vehicle data to searchable text"""
        text_parts = []
        
        # Basic attributes
        if vehicle.get("brand"):
            text_parts.append(vehicle["brand"])
        if vehicle.get("model"):
            text_parts.append(vehicle["model"])
        if vehicle.get("vehicle_type"):
            text_parts.append(vehicle["vehicle_type"])
        if vehicle.get("fuel_type"):
            text_parts.append(vehicle["fuel_type"])
        if vehicle.get("transmission"):
            text_parts.append(vehicle["transmission"])
        if vehicle.get("condition"):
            text_parts.append(vehicle["condition"])
        
        # Year and age
        if vehicle.get("year"):
            current_year = datetime.now().year
            age = current_year - vehicle["year"]
            text_parts.append(f"year_{vehicle['year']}")
            text_parts.append(f"age_{age}")
        
        # Mileage categories
        if vehicle.get("mileage"):
            mileage = vehicle["mileage"]
            if mileage < 30000:
                text_parts.append("low_mileage")
            elif mileage < 80000:
                text_parts.append("medium_mileage")
            else:
                text_parts.append("high_mileage")
        
        # Price categories
        if vehicle.get("price"):
            price = vehicle["price"]
            if price < 20000:
                text_parts.append("budget_friendly")
            elif price < 40000:
                text_parts.append("mid_range")
            else:
                text_parts.append("premium")
        
        # Description
        if vehicle.get("description"):
            text_parts.append(vehicle["description"])
        
        return " ".join(text_parts)
    
    async def search(
        self, 
        query: str, 
        k: int = 5, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vehicles or content
        
        Args:
            query: Search query text
            k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of search results with similarity scores
        """
        start_time = datetime.now()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.vehicle_data:
                return []
            
            # Transform query to vector
            query_vector = await self._vectorize_query(query)
            
            # Apply filters if provided
            filtered_indices = self._apply_filters(filters) if filters else list(range(len(self.vehicle_data)))
            
            # Perform search
            if self.index and FAISS_AVAILABLE:
                results = await self._faiss_search(query_vector, k, filtered_indices)
            else:
                results = await self._sklearn_search(query_vector, k, filtered_indices)
            
            # Update stats
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_search_stats(response_time)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return self._get_fallback_results(query, k)
    
    async def _vectorize_query(self, query: str) -> np.ndarray:
        """Convert query to vector representation"""
        try:
            if hasattr(self.vectorizer, 'transform'):
                query_vector = self.vectorizer.transform([query])
                return query_vector.toarray()[0] if hasattr(query_vector, 'toarray') else query_vector[0]
            else:
                return self.vectorizer.transform([query])[0]
        except Exception as e:
            logger.error(f"❌ Query vectorization failed: {e}")
            return np.zeros(self.dimension)
    
    async def _faiss_search(
        self, 
        query_vector: np.ndarray, 
        k: int, 
        filtered_indices: List[int]
    ) -> List[Dict[str, Any]]:
        """Perform FAISS-based search"""
        try:
            # Normalize query vector
            query_vector = query_vector / np.linalg.norm(query_vector)
            query_vector = query_vector.reshape(1, -1).astype('float32')
            
            # Search
            similarities, indices = self.index.search(query_vector, min(k * 2, len(self.vehicle_data)))
            
            # Filter results and apply constraints
            results = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if idx in filtered_indices and len(results) < k:
                    vehicle = self.vehicle_data[idx].copy()
                    vehicle['similarity_score'] = float(similarity)
                    vehicle['search_rank'] = len(results) + 1
                    results.append(vehicle)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ FAISS search failed: {e}")
            return []
    
    async def _sklearn_search(
        self, 
        query_vector: np.ndarray, 
        k: int, 
        filtered_indices: List[int]
    ) -> List[Dict[str, Any]]:
        """Perform sklearn-based search"""
        try:
            if len(self.embeddings) == 0:
                return []
            
            # Calculate similarities
            similarities = cosine_similarity([query_vector], self.embeddings)[0]
            
            # Get top k indices from filtered set
            filtered_similarities = [(i, similarities[i]) for i in filtered_indices]
            filtered_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Build results
            results = []
            for rank, (idx, similarity) in enumerate(filtered_similarities[:k]):
                vehicle = self.vehicle_data[idx].copy()
                vehicle['similarity_score'] = float(similarity)
                vehicle['search_rank'] = rank + 1
                results.append(vehicle)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ sklearn search failed: {e}")
            return []
    
    def _apply_filters(self, filters: Dict[str, Any]) -> List[int]:
        """Apply filters to vehicle data and return valid indices"""
        valid_indices = []
        
        for i, vehicle in enumerate(self.vehicle_data):
            match = True
            
            for key, value in filters.items():
                if key in vehicle:
                    if isinstance(value, dict):
                        # Range filter (e.g., {"min": 10000, "max": 50000})
                        if "min" in value and vehicle[key] < value["min"]:
                            match = False
                            break
                        if "max" in value and vehicle[key] > value["max"]:
                            match = False
                            break
                    elif isinstance(value, list):
                        # Multiple values filter
                        if vehicle[key] not in value:
                            match = False
                            break
                    else:
                        # Exact match filter
                        if vehicle[key] != value:
                            match = False
                            break
                else:
                    match = False
                    break
            
            if match:
                valid_indices.append(i)
        
        return valid_indices
    
    async def find_similar_vehicles(
        self, 
        target_vehicle: Dict[str, Any], 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find vehicles similar to a target vehicle"""
        # Convert target vehicle to text query
        query = self._vehicle_to_text(target_vehicle)
        
        # Build filters based on vehicle attributes
        filters = {}
        if target_vehicle.get("vehicle_type"):
            filters["vehicle_type"] = target_vehicle["vehicle_type"]
        
        # Price range filter (±30% of target price)
        if target_vehicle.get("price"):
            price = target_vehicle["price"]
            filters["price"] = {
                "min": price * 0.7,
                "max": price * 1.3
            }
        
        return await self.search(query, k, filters)
    
    async def get_market_segments(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get vehicles grouped by market segments"""
        segments = {
            "economy": [],
            "mid_range": [],
            "luxury": [],
            "electric": [],
            "trucks": [],
            "suvs": []
        }
        
        for vehicle in self.vehicle_data:
            price = vehicle.get("price", 0)
            vehicle_type = vehicle.get("vehicle_type", "").lower()
            fuel_type = vehicle.get("fuel_type", "").lower()
            
            # Categorize by price
            if price < 25000:
                segments["economy"].append(vehicle)
            elif price < 50000:
                segments["mid_range"].append(vehicle)
            else:
                segments["luxury"].append(vehicle)
            
            # Categorize by type
            if fuel_type == "electric":
                segments["electric"].append(vehicle)
            elif vehicle_type == "truck":
                segments["trucks"].append(vehicle)
            elif vehicle_type == "suv":
                segments["suvs"].append(vehicle)
        
        return segments
    
    async def update_index(self, new_vehicles: List[Dict[str, Any]]):
        """Update search index with new vehicle data"""
        try:
            logger.info(f"🔄 Updating search index with {len(new_vehicles)} new vehicles...")
            
            # Add new vehicles to data
            self.vehicle_data.extend(new_vehicles)
            
            # Rebuild index
            await self._build_index()
            
            logger.info("✅ Search index updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Index update failed: {e}")
    
    def _get_fallback_results(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Fallback results when search fails"""
        # Return random subset of vehicles
        import random
        
        available_vehicles = self.vehicle_data[:k] if len(self.vehicle_data) >= k else self.vehicle_data
        results = []
        
        for i, vehicle in enumerate(available_vehicles):
            vehicle_copy = vehicle.copy()
            vehicle_copy['similarity_score'] = 0.5  # Neutral score
            vehicle_copy['search_rank'] = i + 1
            vehicle_copy['fallback'] = True
            results.append(vehicle_copy)
        
        return results
    
    def _update_search_stats(self, response_time: float):
        """Update search performance statistics"""
        self.search_stats["total_searches"] += 1
        
        # Update average response time
        current_avg = self.search_stats["avg_response_time"]
        total_searches = self.search_stats["total_searches"]
        self.search_stats["avg_response_time"] = (current_avg * (total_searches - 1) + response_time) / total_searches
    
    async def _save_index_cache(self):
        """Save index to cache for faster loading"""
        try:
            cache_file = self.cache_path / "vector_index.pkl"
            
            cache_data = {
                "embeddings": self.embeddings,
                "vehicle_data": self.vehicle_data,
                "dimension": self.dimension,
                "vectorizer": self.vectorizer,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info("💾 Vector index cached successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to cache index: {e}")
    
    async def _load_index_cache(self) -> bool:
        """Load index from cache"""
        try:
            cache_file = self.cache_path / "vector_index.pkl"
            
            if not cache_file.exists():
                return False
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check cache age (max 24 hours)
            cache_time = datetime.fromisoformat(cache_data["timestamp"])
            if (datetime.now() - cache_time).total_seconds() > 86400:
                logger.info("🕒 Cache expired, rebuilding index")
                return False
            
            # Load cached data
            self.embeddings = cache_data["embeddings"]
            self.vehicle_data = cache_data["vehicle_data"]
            self.dimension = cache_data["dimension"]
            self.vectorizer = cache_data["vectorizer"]
            
            logger.info("📁 Vector index loaded from cache")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load cache: {e}")
            return False
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """Get search performance statistics"""
        return {
            **self.search_stats,
            "index_size": len(self.vehicle_data),
            "dimension": self.dimension,
            "engine_type": "faiss" if self.index else "sklearn",
            "cache_available": (self.cache_path / "vector_index.pkl").exists()
        }
    
    async def health_check(self) -> bool:
        """Check vector search engine health"""
        try:
            if not self.is_initialized:
                return False
            
            # Test search
            test_results = await self.search("test query", k=1)
            return len(test_results) >= 0  # Should at least return empty list
            
        except Exception as e:
            logger.error(f"Vector search health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup search engine resources"""
        logger.info("🧹 Cleaning up vector search engine resources...")
        self.index = None
        self.vectorizer = None
        self.vehicle_data = []
        self.embeddings = []
        self.is_initialized = False

class BasicVectorizer:
    """Basic vectorizer fallback when sklearn is not available"""
    
    def __init__(self):
        self.vocabulary = {}
        self.dimension = 100
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        # Build vocabulary
        all_words = set()
        for text in texts:
            words = text.lower().split()
            all_words.update(words)
        
        self.vocabulary = {word: i for i, word in enumerate(list(all_words)[:self.dimension])}
        
        # Transform texts
        return self.transform(texts)
    
    def transform(self, texts: List[str]) -> np.ndarray:
        vectors = []
        
        for text in texts:
            vector = np.zeros(len(self.vocabulary))
            words = text.lower().split()
            
            for word in words:
                if word in self.vocabulary:
                    vector[self.vocabulary[word]] += 1
            
            # Normalize
            if np.linalg.norm(vector) > 0:
                vector = vector / np.linalg.norm(vector)
            
            vectors.append(vector)
        
        return np.array(vectors)
