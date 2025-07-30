from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import traceback
from typing import Dict, Any
from ...core.exceptions import RAGException, LLMException, EmbeddingException, DatabaseException, ValidationException, ServiceUnavailableException, ConfigurationException, RateLimitException, AuthenticationException, TimeoutException
from ...core.logging import get_logger, set_request_context, get_request_context


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.error_handler")
    
    async def dispatch(self, request: Request, call_next):
        """Process request with error handling."""
        start_time = time.time()
        request_id = str(request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}"))
        
        # Set request context
        set_request_context(request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log successful request
            processing_time = time.time() - start_time
            self.logger.info("Request completed successfully", extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "processing_time": processing_time,
                "user_agent": request.headers.get("user-agent", ""),
                "client_ip": request.client.host if request.client else None
            })
            
            return response
            
        except Exception as exc:
            # Handle different types of exceptions
            response = await self._handle_exception(request, exc, start_time)
            return response
    
    async def _handle_exception(self, request: Request, exc: Exception, start_time: float) -> JSONResponse:
        """Handle different types of exceptions and return appropriate responses."""
        processing_time = time.time() - start_time
        context = get_request_context()
        
        # Determine status code and error details based on exception type
        if isinstance(exc, ValidationException):
            status_code = 400
            error_code = "VALIDATION_ERROR"
            error_message = f"Validation error: {exc.message}"
            error_details = {
                "field": exc.field,
                "value": str(exc.value),
                "details": exc.details
            }
            
        elif isinstance(exc, AuthenticationException):
            status_code = 401
            error_code = "AUTHENTICATION_ERROR"
            error_message = f"Authentication failed: {exc.message}"
            error_details = {
                "service": exc.service,
                "details": exc.details
            }
            
        elif isinstance(exc, RateLimitException):
            status_code = 429
            error_code = "RATE_LIMIT_ERROR"
            error_message = f"Rate limit exceeded: {exc.message}"
            error_details = {
                "service": exc.service,
                "retry_after": exc.retry_after,
                "details": exc.details
            }
            
        elif isinstance(exc, ServiceUnavailableException):
            status_code = 503
            error_code = "SERVICE_UNAVAILABLE"
            error_message = f"Service unavailable: {exc.message}"
            error_details = {
                "service": exc.service,
                "details": exc.details
            }
            
        elif isinstance(exc, TimeoutException):
            status_code = 408
            error_code = "TIMEOUT_ERROR"
            error_message = f"Request timeout: {exc.message}"
            error_details = {
                "operation": exc.operation,
                "timeout_seconds": exc.timeout_seconds,
                "details": exc.details
            }
            
        elif isinstance(exc, (LLMException, EmbeddingException)):
            status_code = 502
            error_code = "EXTERNAL_SERVICE_ERROR"
            error_message = f"External service error: {exc.message}"
            error_details = {
                "provider": getattr(exc, 'provider', 'unknown'),
                "model": getattr(exc, 'model', 'unknown'),
                "details": exc.details
            }
            
        elif isinstance(exc, DatabaseException):
            status_code = 500
            error_code = "DATABASE_ERROR"
            error_message = f"Database error: {exc.message}"
            error_details = {
                "operation": exc.operation,
                "details": exc.details
            }
            
        elif isinstance(exc, ConfigurationException):
            status_code = 500
            error_code = "CONFIGURATION_ERROR"
            error_message = f"Configuration error: {exc.message}"
            error_details = {
                "config_key": exc.config_key,
                "details": exc.details
            }
            
        elif isinstance(exc, RAGException):
            status_code = 500
            error_code = exc.error_code or "RAG_ERROR"
            error_message = exc.message
            error_details = exc.details
            
        else:
            # Generic error handling
            status_code = 500
            error_code = "INTERNAL_SERVER_ERROR"
            error_message = "An unexpected error occurred"
            error_details = {
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            }
        
        # Log error
        self.logger.error("Request failed", extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "processing_time": processing_time,
            "error_code": error_code,
            "error_message": error_message,
            "error_details": error_details,
            "traceback": traceback.format_exc() if status_code == 500 else None,
            "user_agent": request.headers.get("user-agent", ""),
            "client_ip": request.client.host if request.client else None
        })
        
        # Prepare error response
        error_response = {
            "error": {
                "code": error_code,
                "message": error_message,
                "details": error_details,
                "request_id": context.get("request_id"),
                "timestamp": time.time()
            }
        }
        
        # Add retry information for rate limits
        if isinstance(exc, RateLimitException) and exc.retry_after:
            error_response["error"]["retry_after"] = exc.retry_after
        
        response = JSONResponse(
            status_code=status_code,
            content=error_response,
            headers={"X-Request-ID": context.get("request_id", "")}
        )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware.request_logging")
    
    async def dispatch(self, request: Request, call_next):
        """Log request details."""
        start_time = time.time()
        
        # Log request start
        self.logger.info("Request started", extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent", ""),
            "client_ip": request.client.host if request.client else None,
            "content_length": request.headers.get("content-length", 0)
        })
        
        # Process request
        response = await call_next(request)
        
        # Log request completion
        processing_time = time.time() - start_time
        self.logger.info("Request completed", extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "processing_time": processing_time,
            "response_size": len(response.body) if hasattr(response, 'body') else 0
        })
        
        return response 