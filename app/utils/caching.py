"""
Caching utilities for improved performance
"""

import logging
import json
import time
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import asyncio
import threading
from abc import ABC, abstractmethod

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..config.settings import settings

logger = logging.getLogger(__name__)

class CacheInterface(ABC):
    """Abstract base class for cache implementations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        pass

class MemoryCache(CacheInterface):
    """
    In-memory cache implementation with TTL support
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache = {}
        self.access_times = {}
        self.expiry_times = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        
        # Stats
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            # Check if key exists and not expired
            if key not in self.cache:
                self.misses += 1
                return None
            
            # Check expiry
            if key in self.expiry_times:
                if time.time() > self.expiry_times[key]:
                    # Expired, remove it
                    del self.cache[key]
                    del self.expiry_times[key]
                    if key in self.access_times:
                        del self.access_times[key]
                    self.misses += 1
                    return None
            
            # Update access time
            self.access_times[key] = time.time()
            self.hits += 1
            
            return self.cache[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self.lock:
            try:
                # Ensure we don't exceed max size
                if len(self.cache) >= self.max_size and key not in self.cache:
                    self._evict_lru()
                
                # Set value
                self.cache[key] = value
                self.access_times[key] = time.time()
                
                # Set expiry
                if ttl is not None:
                    self.expiry_times[key] = time.time() + ttl
                elif self.default_ttl:
                    self.expiry_times[key] = time.time() + self.default_ttl
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Cache set failed: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                if key in self.expiry_times:
                    del self.expiry_times[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        value = await self.get(key)
        return value is not None
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.expiry_times.clear()
            return True
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        # Find LRU key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # Remove it
        del self.cache[lru_key]
        del self.access_times[lru_key]
        if lru_key in self.expiry_times:
            del self.expiry_times[lru_key]
        
        self.evictions += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests) if total_requests > 0 else 0
            
            return {
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_rate": hit_rate,
                "size": len(self.cache),
                "max_size": self.max_size
            }

class RedisCache(CacheInterface):
    """
    Redis-based cache implementation
    """
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        self.redis_url = redis_url or settings.redis_url
        self.default_ttl = default_ttl
        self.client = None
        self.connected = False
        
        # Stats
        self.hits = 0
        self.misses = 0
    
    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis is not available. Install with: pip install redis")
        
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            self.connected = True
            logger.info("✅ Connected to Redis cache")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.connected:
            await self.connect()
        
        try:
            value = self.client.get(key)
            if value is not None:
                self.hits += 1
                return json.loads(value)
            else:
                self.misses += 1
                return None
        except Exception as e:
            logger.error(f"❌ Redis get failed: {e}")
            self.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis"""
        if not self.connected:
            await self.connect()
        
        try:
            serialized_value = json.dumps(value, default=str)
            
            if ttl is not None:
                self.client.setex(key, ttl, serialized_value)
            elif self.default_ttl:
                self.client.setex(key, self.default_ttl, serialized_value)
            else:
                self.client.set(key, serialized_value)
            
            return True
        except Exception as e:
            logger.error(f"❌ Redis set failed: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.connected:
            await self.connect()
        
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"❌ Redis delete failed: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.connected:
            await self.connect()
        
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Redis exists check failed: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all keys from Redis (use with caution)"""
        if not self.connected:
            await self.connect()
        
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"❌ Redis clear failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests) if total_requests > 0 else 0
        
        stats = {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "connected": self.connected
        }
        
        if self.connected and self.client:
            try:
                info = self.client.info()
                stats.update({
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to get Redis info: {e}")
        
        return stats

class CacheManager:
    """
    High-level cache manager with multiple backends and features
    """
    
    def __init__(self):
        self.primary_cache = None
        self.fallback_cache = MemoryCache()
        self.prefix = "vprediction:"
        
        # Cache configuration
        self.use_redis = settings.use_redis_cache if hasattr(settings, 'use_redis_cache') else False
        
        # Performance tracking
        self.operation_times = []
    
    async def initialize(self):
        """Initialize cache manager"""
        try:
            if self.use_redis and REDIS_AVAILABLE:
                try:
                    self.primary_cache = RedisCache()
                    await self.primary_cache.connect()
                    logger.info("✅ Cache manager initialized with Redis")
                except Exception as e:
                    logger.warning(f"⚠️ Redis failed, using memory cache: {e}")
                    self.primary_cache = MemoryCache()
            else:
                self.primary_cache = MemoryCache()
                logger.info("✅ Cache manager initialized with memory cache")
        
        except Exception as e:
            logger.error(f"❌ Cache manager initialization failed: {e}")
            self.primary_cache = MemoryCache()
    
    def _make_key(self, key: str) -> str:
        """Create a prefixed cache key"""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with fallback"""
        cache_key = self._make_key(key)
        start_time = time.time()
        
        try:
            # Try primary cache first
            value = await self.primary_cache.get(cache_key)
            
            if value is None and self.primary_cache != self.fallback_cache:
                # Try fallback cache
                value = await self.fallback_cache.get(cache_key)
                
                # If found in fallback, promote to primary
                if value is not None:
                    await self.primary_cache.set(cache_key, value)
            
            self._record_operation_time(time.time() - start_time)
            return value
            
        except Exception as e:
            logger.error(f"❌ Cache get failed: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with fallback"""
        cache_key = self._make_key(key)
        start_time = time.time()
        
        try:
            # Set in primary cache
            success = await self.primary_cache.set(cache_key, value, ttl)
            
            # Also set in fallback if different
            if self.primary_cache != self.fallback_cache:
                await self.fallback_cache.set(cache_key, value, ttl)
            
            self._record_operation_time(time.time() - start_time)
            return success
            
        except Exception as e:
            logger.error(f"❌ Cache set failed: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from all caches"""
        cache_key = self._make_key(key)
        
        try:
            primary_success = await self.primary_cache.delete(cache_key)
            
            if self.primary_cache != self.fallback_cache:
                await self.fallback_cache.delete(cache_key)
            
            return primary_success
            
        except Exception as e:
            logger.error(f"❌ Cache delete failed: {e}")
            return False
    
    async def cache_prediction(self, vehicle_data: Dict[str, Any], prediction: Dict[str, Any], ttl: int = 1800):
        """Cache a price prediction"""
        # Create cache key from vehicle data hash
        key_data = {k: v for k, v in vehicle_data.items() if k in ['brand', 'model', 'year', 'mileage', 'condition']}
        cache_key = self._hash_vehicle_data(key_data)
        
        await self.set(f"prediction:{cache_key}", prediction, ttl)
    
    async def get_cached_prediction(self, vehicle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached price prediction"""
        key_data = {k: v for k, v in vehicle_data.items() if k in ['brand', 'model', 'year', 'mileage', 'condition']}
        cache_key = self._hash_vehicle_data(key_data)
        
        return await self.get(f"prediction:{cache_key}")
    
    async def cache_search_results(self, query: str, results: List[Dict[str, Any]], ttl: int = 900):
        """Cache search results"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        await self.set(f"search:{query_hash}", results, ttl)
    
    async def get_cached_search(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return await self.get(f"search:{query_hash}")
    
    def _hash_vehicle_data(self, vehicle_data: Dict[str, Any]) -> str:
        """Create hash from vehicle data for cache key"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(vehicle_data, sort_keys=True)
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    def _record_operation_time(self, duration: float):
        """Record cache operation timing"""
        self.operation_times.append(duration)
        
        # Keep only recent times
        if len(self.operation_times) > 1000:
            self.operation_times = self.operation_times[-1000:]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "cache_type": type(self.primary_cache).__name__,
            "fallback_type": type(self.fallback_cache).__name__,
            "use_redis": self.use_redis,
            "avg_operation_time_ms": 0
        }
        
        # Calculate average operation time
        if self.operation_times:
            stats["avg_operation_time_ms"] = (sum(self.operation_times) / len(self.operation_times)) * 1000
        
        # Get primary cache stats
        try:
            primary_stats = self.primary_cache.get_stats()
            stats["primary_cache"] = primary_stats
        except Exception as e:
            logger.warning(f"⚠️ Failed to get primary cache stats: {e}")
        
        # Get fallback cache stats if different
        if self.primary_cache != self.fallback_cache:
            try:
                fallback_stats = self.fallback_cache.get_stats()
                stats["fallback_cache"] = fallback_stats
            except Exception as e:
                logger.warning(f"⚠️ Failed to get fallback cache stats: {e}")
        
        return stats
    
    async def health_check(self) -> bool:
        """Check cache health"""
        try:
            # Test basic operations
            test_key = "health_check"
            test_value = {"timestamp": datetime.now().isoformat()}
            
            # Test set
            set_success = await self.set(test_key, test_value, 60)
            if not set_success:
                return False
            
            # Test get
            retrieved_value = await self.get(test_key)
            if retrieved_value != test_value:
                return False
            
            # Test delete
            delete_success = await self.delete(test_key)
            if not delete_success:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup cache resources"""
        logger.info("🧹 Cleaning up cache manager...")
        
        if hasattr(self.primary_cache, 'client') and self.primary_cache.client:
            try:
                self.primary_cache.client.close()
            except Exception as e:
                logger.warning(f"⚠️ Error closing Redis connection: {e}")

# Global cache manager instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

# Decorator for caching function results
def cached(ttl: int = 3600, key_func=None):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key from args
    """
    def decorator(func):
        cache_manager = get_cache_manager()
        
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to handle this differently
            # This is a simplified version - in production you might want
            # to use a sync cache or run the async cache in a thread
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
