import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from app.core.exceptions import (
    RAGException, LLMException, EmbeddingException, DatabaseException,
    ValidationException, ServiceUnavailableException, ConfigurationException,
    RateLimitException, AuthenticationException, TimeoutException
)
from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState
from app.core.retry import RetryHandler, RetryConfig
from app.core.logging import get_logger, RequestContext


class TestExceptions:
    """Test custom exception classes."""
    
    def test_rag_exception(self):
        """Test base RAG exception."""
        exc = RAGException("Test error", "TEST_ERROR", {"detail": "test"})
        assert exc.message == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.details == {"detail": "test"}
    
    def test_llm_exception(self):
        """Test LLM exception."""
        exc = LLMException("LLM error", "openai", "gpt-4", {"tokens": 100})
        assert exc.message == "LLM error"
        assert exc.provider == "openai"
        assert exc.model == "gpt-4"
        assert exc.error_code == "LLM_ERROR"
    
    def test_embedding_exception(self):
        """Test embedding exception."""
        exc = EmbeddingException("Embedding error", "openai", "text-embedding-ada-002")
        assert exc.message == "Embedding error"
        assert exc.provider == "openai"
        assert exc.model == "text-embedding-ada-002"
        assert exc.error_code == "EMBEDDING_ERROR"
    
    def test_database_exception(self):
        """Test database exception."""
        exc = DatabaseException("DB error", "query", {"collection": "test"})
        assert exc.message == "DB error"
        assert exc.operation == "query"
        assert exc.error_code == "DATABASE_ERROR"
    
    def test_validation_exception(self):
        """Test validation exception."""
        exc = ValidationException("Invalid input", "query", "empty", {"max_length": 100})
        assert exc.message == "Invalid input"
        assert exc.field == "query"
        assert exc.value == "empty"
        assert exc.error_code == "VALIDATION_ERROR"
    
    def test_service_unavailable_exception(self):
        """Test service unavailable exception."""
        exc = ServiceUnavailableException("Service down", "ollama")
        assert exc.message == "Service down"
        assert exc.service == "ollama"
        assert exc.error_code == "SERVICE_UNAVAILABLE"
    
    def test_timeout_exception(self):
        """Test timeout exception."""
        exc = TimeoutException("Request timeout", "api_call", 30.0)
        assert exc.message == "Request timeout"
        assert exc.operation == "api_call"
        assert exc.timeout_seconds == 30.0
        assert exc.error_code == "TIMEOUT_ERROR"


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state (normal operation)."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)
        cb = CircuitBreaker("test_service", config)
        
        # Mock successful function
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)
        cb = CircuitBreaker("test_service", config)
        
        # Mock failing function
        async def fail_func():
            raise Exception("Test failure")
        
        # First failure
        with pytest.raises(Exception):
            await cb.call(fail_func)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 1
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            await cb.call(fail_func)
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 2
        
        # Third call should be rejected
        with pytest.raises(ServiceUnavailableException):
            await cb.call(fail_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=0.1,  # Short timeout for testing
            success_threshold=1
        )
        cb = CircuitBreaker("test_service", config)
        
        # Mock failing function
        async def fail_func():
            raise Exception("Test failure")
        
        # Cause failure to open circuit
        with pytest.raises(Exception):
            await cb.call(fail_func)
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Mock successful function
        async def success_func():
            return "success"
        
        # Should be in half-open state and succeed
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_breaker_status(self):
        """Test circuit breaker status reporting."""
        config = CircuitBreakerConfig()
        cb = CircuitBreaker("test_service", config)
        
        status = cb.get_status()
        assert status["name"] == "test_service"
        assert status["state"] == CircuitState.CLOSED.value
        assert status["failure_count"] == 0
        assert status["success_count"] == 0


class TestRetryHandler:
    """Test retry functionality."""
    
    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """Test retry succeeds on first attempt."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        handler = RetryHandler(config)
        
        call_count = 0
        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await handler.execute(success_func)
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self):
        """Test retry succeeds after some failures."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        handler = RetryHandler(config)
        
        call_count = 0
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await handler.execute(fail_then_succeed)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhausts_all_attempts(self):
        """Test retry exhausts all attempts and raises last exception."""
        config = RetryConfig(max_attempts=2, base_delay=0.1)
        handler = RetryHandler(config)
        
        call_count = 0
        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise Exception(f"Failure {call_count}")
        
        with pytest.raises(Exception) as exc_info:
            await handler.execute(always_fail)
        
        assert str(exc_info.value) == "Failure 2"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_timeout(self):
        """Test retry respects timeout."""
        config = RetryConfig(max_attempts=5, base_delay=0.5, timeout=0.1)
        handler = RetryHandler(config)
        
        async def slow_func():
            await asyncio.sleep(0.2)
            return "success"
        
        with pytest.raises(TimeoutException):
            await handler.execute(slow_func)


class TestLogging:
    """Test logging functionality."""
    
    def test_get_logger(self):
        """Test logger creation."""
        logger = get_logger("test.module")
        assert logger.name == "rag_chatbot.test.module"
    
    def test_request_context(self):
        """Test request context management."""
        with RequestContext("test-request", "test-user") as ctx:
            assert ctx.request_id == "test-request"
            assert ctx.user_id == "test-user"
            assert ctx.correlation_id is not None
    
    def test_set_request_context(self):
        """Test setting request context."""
        from app.core.logging import set_request_context, get_request_context
        
        set_request_context("test-request", "test-user")
        context = get_request_context()
        
        assert context["request_id"] == "test-request"
        assert context["user_id"] == "test-user"
        assert context["correlation_id"] is not None


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_llm_exception_handling(self):
        """Test LLM exception handling."""
        exc = LLMException("API error", "openai", "gpt-4")
        
        # Test exception properties
        assert exc.message == "API error"
        assert exc.provider == "openai"
        assert exc.model == "gpt-4"
        assert exc.error_code == "LLM_ERROR"
    
    @pytest.mark.asyncio
    async def test_rate_limit_exception(self):
        """Test rate limit exception."""
        exc = RateLimitException("Rate limit exceeded", "openai", 60)
        
        assert exc.message == "Rate limit exceeded"
        assert exc.service == "openai"
        assert exc.retry_after == 60
        assert exc.error_code == "RATE_LIMIT_ERROR"
    
    @pytest.mark.asyncio
    async def test_timeout_exception(self):
        """Test timeout exception."""
        exc = TimeoutException("Request timeout", "api_call", 30.0)
        
        assert exc.message == "Request timeout"
        assert exc.operation == "api_call"
        assert exc.timeout_seconds == 30.0
        assert exc.error_code == "TIMEOUT_ERROR"


if __name__ == "__main__":
    pytest.main([__file__]) 