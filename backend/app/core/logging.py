import logging
import json
import time
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar
from functools import wraps
import asyncio


# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add context information
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        user_id = user_id_var.get()
        if user_id:
            log_entry["user_id"] = user_id
        
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id
        
        # Add exception information
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, default=str)


class RequestContextFilter(logging.Filter):
    """Filter to add request context to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to log record."""
        request_id = request_id_var.get()
        if request_id:
            record.request_id = request_id
        
        user_id = user_id_var.get()
        if user_id:
            record.user_id = user_id
        
        correlation_id = correlation_id_var.get()
        if correlation_id:
            record.correlation_id = correlation_id
        
        return True


def setup_logging(
    level: str = "INFO",
    format_type: str = "structured",
    log_file: Optional[str] = None
) -> None:
    """
    Setup application logging.
    
    Args:
        level: Logging level
        format_type: "structured" or "simple"
        log_file: Optional log file path
    """
    # Create logger
    logger = logging.getLogger("rag_chatbot")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    if format_type == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestContextFilter())
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestContextFilter())
        logger.addHandler(file_handler)
    
    # Set as default logger
    logging.getLogger().handlers = logger.handlers


def get_logger(name: str) -> logging.Logger:
    """Get logger with request context."""
    return logging.getLogger(f"rag_chatbot.{name}")


def log_function_call(func):
    """Decorator to log function calls with timing."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            logger.info(f"Calling {func.__name__}", extra={
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            })
            
            result = await func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            logger.info(f"Completed {func.__name__}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "success": True
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed {func.__name__}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "success": False,
                "error": str(e)
            })
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            logger.info(f"Calling {func.__name__}", extra={
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            })
            
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            logger.info(f"Completed {func.__name__}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "success": True
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed {func.__name__}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "success": False,
                "error": str(e)
            })
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class RequestContext:
    """Context manager for request tracking."""
    
    def __init__(self, request_id: Optional[str] = None, user_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.correlation_id = str(uuid.uuid4())
        self._request_id_token = None
        self._user_id_token = None
        self._correlation_id_token = None
    
    def __enter__(self):
        """Set context variables."""
        self._request_id_token = request_id_var.set(self.request_id)
        if self.user_id:
            self._user_id_token = user_id_var.set(self.user_id)
        self._correlation_id_token = correlation_id_var.set(self.correlation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset context variables."""
        if self._request_id_token:
            request_id_var.reset(self._request_id_token)
        if self._user_id_token:
            user_id_var.reset(self._user_id_token)
        if self._correlation_id_token:
            correlation_id_var.reset(self._correlation_id_token)


def set_request_context(request_id: str, user_id: Optional[str] = None):
    """Set request context for current execution."""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    correlation_id_var.set(str(uuid.uuid4()))


def get_request_context() -> Dict[str, Optional[str]]:
    """Get current request context."""
    return {
        "request_id": request_id_var.get(),
        "user_id": user_id_var.get(),
        "correlation_id": correlation_id_var.get()
    }


# Initialize logging
setup_logging() 