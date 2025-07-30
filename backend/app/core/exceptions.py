from typing import Optional, Dict, Any


class RAGException(Exception):
    """Base exception for RAG application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class LLMException(RAGException):
    """Exception raised when LLM operations fail."""
    
    def __init__(self, message: str, provider: str, model: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "LLM_ERROR", details)
        self.provider = provider
        self.model = model


class EmbeddingException(RAGException):
    """Exception raised when embedding operations fail."""
    
    def __init__(self, message: str, provider: str, model: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EMBEDDING_ERROR", details)
        self.provider = provider
        self.model = model


class DatabaseException(RAGException):
    """Exception raised when database operations fail."""
    
    def __init__(self, message: str, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation


class ValidationException(RAGException):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str, field: str, value: Any, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value


class ServiceUnavailableException(RAGException):
    """Exception raised when external services are unavailable."""
    
    def __init__(self, message: str, service: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SERVICE_UNAVAILABLE", details)
        self.service = service


class ConfigurationException(RAGException):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key


class RateLimitException(RAGException):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str, service: str, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.service = service
        self.retry_after = retry_after


class AuthenticationException(RAGException):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str, service: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)
        self.service = service


class TimeoutException(RAGException):
    """Exception raised when operations timeout."""
    
    def __init__(self, message: str, operation: str, timeout_seconds: float, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "TIMEOUT_ERROR", details)
        self.operation = operation
        self.timeout_seconds = timeout_seconds 