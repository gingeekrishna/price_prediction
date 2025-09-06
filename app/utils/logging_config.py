"""
Logging configuration and utilities
"""

import logging
import logging.handlers
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import traceback

from ..config.settings import settings, get_logs_path

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    
    def __init__(self, include_extra=True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add thread and process info
        if hasattr(record, 'process'):
            log_entry["process_id"] = record.process
        if hasattr(record, 'thread'):
            log_entry["thread_id"] = record.thread
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if enabled
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'message', 'exc_info', 'exc_text', 
                              'stack_info']:
                    log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class ColorFormatter(logging.Formatter):
    """
    Colorized console formatter
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def __init__(self, use_colors=True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        if self.use_colors:
            level_color = self.COLORS.get(record.levelname, '')
            reset_color = self.COLORS['RESET']
            
            # Create colored level name
            colored_level = f"{level_color}{record.levelname:8}{reset_color}"
            
            # Format timestamp
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            
            # Create log line
            log_line = f"{timestamp} | {colored_level} | {record.name:20} | {record.getMessage()}"
            
            # Add location info for errors
            if record.levelno >= logging.ERROR:
                log_line += f" ({record.filename}:{record.lineno})"
            
            return log_line
        else:
            # Fallback to standard formatting
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            return f"{timestamp} | {record.levelname:8} | {record.name:20} | {record.getMessage()}"

class StructuredLogger:
    """
    Enhanced logger with structured logging capabilities
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra fields"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with extra fields"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra fields"""
        self.logger.critical(message, extra=kwargs)
    
    def log_prediction(self, vehicle_data: Dict[str, Any], prediction: Dict[str, Any], duration_ms: float):
        """Log a prediction event"""
        self.info(
            "Price prediction completed",
            vehicle_brand=vehicle_data.get("brand"),
            vehicle_model=vehicle_data.get("model"),
            vehicle_year=vehicle_data.get("year"),
            predicted_price=prediction.get("predicted_price"),
            confidence=prediction.get("confidence_score"),
            duration_ms=duration_ms,
            event_type="prediction"
        )
    
    def log_api_request(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """Log an API request"""
        self.info(
            f"API request: {method} {path}",
            http_method=method,
            http_path=path,
            http_status=status_code,
            duration_ms=duration_ms,
            event_type="api_request",
            **kwargs
        )
    
    def log_model_training(self, samples_count: int, accuracy: float, duration_ms: float):
        """Log model training event"""
        self.info(
            "Model training completed",
            samples_count=samples_count,
            accuracy=accuracy,
            duration_ms=duration_ms,
            event_type="model_training"
        )
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with additional context"""
        self.error(
            f"Error occurred: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            event_type="error",
            exc_info=True
        )

def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_format: bool = False,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up application logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        json_format: Whether to use JSON formatting for file logs
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
    """
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root level
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Create logs directory
    logs_path = get_logs_path()
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        if json_format:
            console_formatter = JSONFormatter()
        else:
            console_formatter = ColorFormatter()
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        # Main log file
        log_file = logs_path / "application.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Error log file (separate file for errors and above)
        error_log_file = logs_path / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        
        if json_format:
            error_formatter = JSONFormatter()
        else:
            error_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s | %(pathname)s:%(lineno)d',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger("app.setup")
    logger.info("Logging configured: level=%s, log_to_file=%s, log_to_console=%s, json_format=%s, logs_path=%s", 
                level, log_to_file, log_to_console, json_format, str(logs_path))

def get_logger(name: str, structured: bool = False) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        structured: Whether to return a StructuredLogger instance
        
    Returns:
        Logger instance
    """
    if structured:
        return StructuredLogger(name)
    else:
        return logging.getLogger(name)

class LogContext:
    """
    Context manager for adding context to log messages
    """
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = None
    
    def __enter__(self):
        # Store the old factory
        self.old_factory = logging.getLogRecordFactory()
        
        # Create new factory that adds context
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the old factory
        logging.setLogRecordFactory(self.old_factory)

def log_with_context(**context):
    """
    Decorator to add context to all log messages in a function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            with LogContext(logger, **context):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Performance logging utilities
class PerformanceLogger:
    """
    Logger for performance metrics
    """
    
    def __init__(self):
        self.logger = get_logger("performance", structured=True)
    
    def log_response_time(self, operation: str, duration_ms: float, **context):
        """Log response time for an operation"""
        self.logger.info(
            f"{operation} completed",
            operation=operation,
            duration_ms=duration_ms,
            metric_type="response_time",
            **context
        )
    
    def log_throughput(self, operation: str, count: int, duration_ms: float, **context):
        """Log throughput metrics"""
        throughput = (count / duration_ms) * 1000  # operations per second
        
        self.logger.info(
            f"{operation} throughput",
            operation=operation,
            count=count,
            duration_ms=duration_ms,
            throughput_ops_per_sec=throughput,
            metric_type="throughput",
            **context
        )
    
    def log_resource_usage(self, cpu_percent: float, memory_mb: float, **context):
        """Log resource usage"""
        self.logger.info(
            "Resource usage",
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            metric_type="resource_usage",
            **context
        )

# Global performance logger
_performance_logger = None

def get_performance_logger() -> PerformanceLogger:
    """Get the global performance logger"""
    global _performance_logger
    if _performance_logger is None:
        _performance_logger = PerformanceLogger()
    return _performance_logger
