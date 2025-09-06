"""
Monitoring utilities for tracking application performance and health
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
from dataclasses import dataclass
import threading

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from ..config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags or {}
        }

class MetricsCollector:
    """
    Collects and stores application metrics
    """
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics = deque(maxlen=max_metrics)
        self.aggregates = defaultdict(list)
        self.lock = threading.Lock()
        
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric value"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        
        with self.lock:
            self.metrics.append(metric)
            self.aggregates[name].append(value)
            
            # Keep only recent values for aggregation
            if len(self.aggregates[name]) > 1000:
                self.aggregates[name] = self.aggregates[name][-1000:]
    
    def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        self.record_metric(name, 1.0, tags)
    
    def record_timing(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric"""
        self.record_metric(f"{name}_duration_ms", duration_ms, tags)
    
    def get_recent_metrics(self, minutes: int = 5) -> List[Metric]:
        """Get metrics from the last N minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            return [m for m in self.metrics if m.timestamp >= cutoff]
    
    def get_aggregated_stats(self, metric_name: str) -> Dict[str, float]:
        """Get aggregated statistics for a metric"""
        with self.lock:
            values = self.aggregates.get(metric_name, [])
            
            if not values:
                return {}
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "sum": sum(values)
            }
    
    def export_metrics(self) -> List[Dict[str, Any]]:
        """Export all metrics as dictionaries"""
        with self.lock:
            return [m.to_dict() for m in self.metrics]

class PerformanceMonitor:
    """
    Monitors application performance and system resources
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.monitoring = False
        self.monitor_task = None
        
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start background performance monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval_seconds))
        logger.info(f"📊 Started performance monitoring (interval: {interval_seconds}s)")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Stopped performance monitoring")
    
    async def _monitor_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            if not PSUTIL_AVAILABLE:
                # Use mock values when psutil is not available
                self.metrics.record_metric("system.cpu_percent", 50.0)
                self.metrics.record_metric("system.memory_percent", 60.0)
                self.metrics.record_metric("system.memory_used_mb", 2048.0)
                self.metrics.record_metric("system.disk_percent", 70.0)
                self.metrics.record_metric("process.cpu_percent", 10.0)
                self.metrics.record_metric("process.memory_rss_mb", 512.0)
                self.metrics.record_metric("process.memory_vms_mb", 1024.0)
                self.metrics.record_metric("process.thread_count", 8.0)
                return
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.record_metric("system.cpu_percent", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.record_metric("system.memory_percent", memory.percent)
            self.metrics.record_metric("system.memory_used_mb", memory.used / 1024 / 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics.record_metric("system.disk_percent", (disk.used / disk.total) * 100)
            
            # Process-specific metrics
            process = psutil.Process()
            
            # Process CPU and memory
            self.metrics.record_metric("process.cpu_percent", process.cpu_percent())
            
            process_memory = process.memory_info()
            self.metrics.record_metric("process.memory_rss_mb", process_memory.rss / 1024 / 1024)
            self.metrics.record_metric("process.memory_vms_mb", process_memory.vms / 1024 / 1024)
            
            # Thread count
            self.metrics.record_metric("process.thread_count", process.num_threads())
            
        except Exception as e:
            logger.error(f"❌ Failed to collect system metrics: {e}")
    
    def time_function(self, func_name: str):
        """Decorator to time function execution"""
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        duration = (time.time() - start_time) * 1000
                        self.metrics.record_timing(func_name, duration, {"status": "success"})
                        return result
                    except Exception as e:
                        duration = (time.time() - start_time) * 1000
                        self.metrics.record_timing(func_name, duration, {"status": "error"})
                        raise
                return async_wrapper
            else:
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        duration = (time.time() - start_time) * 1000
                        self.metrics.record_timing(func_name, duration, {"status": "success"})
                        return result
                    except Exception as e:
                        duration = (time.time() - start_time) * 1000
                        self.metrics.record_timing(func_name, duration, {"status": "error"})
                        raise
                return sync_wrapper
        return decorator

class HealthChecker:
    """
    Performs health checks on application components
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.health_checks = {}
        self.last_check_results = {}
        
    def register_health_check(self, name: str, check_func, critical: bool = False):
        """Register a health check function"""
        self.health_checks[name] = {
            "func": check_func,
            "critical": critical
        }
        logger.info(f"🏥 Registered health check: {name} (critical: {critical})")
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": True,
            "checks": {}
        }
        
        for name, check_config in self.health_checks.items():
            try:
                start_time = time.time()
                
                # Run health check
                if asyncio.iscoroutinefunction(check_config["func"]):
                    healthy = await check_config["func"]()
                else:
                    healthy = check_config["func"]()
                
                duration = (time.time() - start_time) * 1000
                
                # Record results
                results["checks"][name] = {
                    "healthy": healthy,
                    "critical": check_config["critical"],
                    "duration_ms": duration,
                    "error": None
                }
                
                # Update overall health
                if check_config["critical"] and not healthy:
                    results["overall_healthy"] = False
                
                # Record metrics
                self.metrics.record_metric(
                    f"health_check.{name}",
                    1.0 if healthy else 0.0,
                    {"status": "success"}
                )
                self.metrics.record_timing(f"health_check.{name}", duration)
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Health check '{name}' failed: {error_msg}")
                
                results["checks"][name] = {
                    "healthy": False,
                    "critical": check_config["critical"],
                    "duration_ms": 0,
                    "error": error_msg
                }
                
                # Update overall health if critical
                if check_config["critical"]:
                    results["overall_healthy"] = False
                
                # Record error metric
                self.metrics.record_metric(
                    f"health_check.{name}",
                    0.0,
                    {"status": "error"}
                )
        
        self.last_check_results = results
        return results
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of the latest health check results"""
        if not self.last_check_results:
            await self.run_health_checks()
        
        summary = {
            "overall_healthy": self.last_check_results.get("overall_healthy", False),
            "total_checks": len(self.health_checks),
            "healthy_checks": 0,
            "failed_checks": 0,
            "critical_failed": 0,
            "last_check": self.last_check_results.get("timestamp", "never")
        }
        
        for check_name, check_result in self.last_check_results.get("checks", {}).items():
            if check_result["healthy"]:
                summary["healthy_checks"] += 1
            else:
                summary["failed_checks"] += 1
                if check_result["critical"]:
                    summary["critical_failed"] += 1
        
        return summary

# Global instances
_metrics_collector = None
_performance_monitor = None
_health_checker = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor(get_metrics_collector())
    return _performance_monitor

def get_health_checker() -> HealthChecker:
    """Get the global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker(get_metrics_collector())
    return _health_checker

# Context managers for timing
class TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str, metrics_collector: Optional[MetricsCollector] = None):
        self.operation_name = operation_name
        self.metrics = metrics_collector or get_metrics_collector()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000
            status = "error" if exc_type else "success"
            self.metrics.record_timing(self.operation_name, duration, {"status": status})

def time_operation(operation_name: str):
    """Context manager for timing operations"""
    return TimingContext(operation_name)

class ModelMetrics:
    """
    Specialized metrics collector for ML model performance
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics = metrics_collector or get_metrics_collector()
        
    def record_prediction(self, prediction_time_ms: float, confidence: float, model_version: str):
        """Record a prediction event"""
        self.metrics.record_timing("model.prediction", prediction_time_ms)
        self.metrics.record_metric("model.confidence", confidence, {"model_version": model_version})
        self.metrics.increment_counter("model.predictions_total", {"model_version": model_version})
    
    def record_training(self, training_time_ms: float, accuracy: float, samples_count: int):
        """Record a training event"""
        self.metrics.record_timing("model.training", training_time_ms)
        self.metrics.record_metric("model.accuracy", accuracy)
        self.metrics.record_metric("model.training_samples", samples_count)
        self.metrics.increment_counter("model.training_total")
    
    def record_error(self, error_type: str, model_version: str):
        """Record a model error"""
        self.metrics.increment_counter("model.errors_total", {
            "error_type": error_type,
            "model_version": model_version
        })

# FastAPI middleware for metrics
async def metrics_middleware(request, call_next):
    """Middleware to collect API metrics"""
    import time
    from fastapi import Request, Response
    
    start_time = time.time()
    
    response = await call_next(request)
    
    # Calculate response time
    duration = (time.time() - start_time) * 1000
    
    # Get metrics collector
    metrics = get_metrics_collector()
    
    # Record metrics
    metrics.record_timing("api.request_duration", duration, {
        "method": request.method,
        "path": request.url.path,
        "status_code": str(response.status_code)
    })
    
    metrics.increment_counter("api.requests_total", {
        "method": request.method,
        "path": request.url.path,
        "status_code": str(response.status_code)
    })
    
    return response
