import asyncio
import time
import random
from typing import Callable, Any, Optional, Type, Union, List
from functools import wraps
from .exceptions import TimeoutException


class RetryConfig:
    """Configuration for retry mechanism."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
        timeout: Optional[float] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [Exception]
        self.timeout = timeout


class RetryHandler:
    """
    Retry mechanism with exponential backoff and jitter.
    """
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception after all retries exhausted
            TimeoutException: If timeout is exceeded
        """
        last_exception = None
        start_time = time.time()
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                # Check timeout
                if self.config.timeout and (time.time() - start_time) > self.config.timeout:
                    raise TimeoutException(
                        f"Operation timed out after {self.config.timeout} seconds",
                        operation=func.__name__,
                        timeout_seconds=self.config.timeout
                    )
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
            except tuple(self.config.retryable_exceptions) as e:
                last_exception = e
                
                # Don't retry on last attempt
                if attempt == self.config.max_attempts:
                    break
                
                # Calculate delay with exponential backoff
                delay = self._calculate_delay(attempt)
                
                # Add jitter if enabled
                if self.config.jitter:
                    delay = delay * (0.5 + random.random() * 0.5)
                
                # Wait before retry
                await asyncio.sleep(delay)
        
        # All retries exhausted
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        return min(delay, self.config.max_delay)


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
    timeout: Optional[float] = None
):
    """
    Decorator for retry functionality.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: List of exceptions to retry on
        timeout: Overall timeout for all attempts
        
    Returns:
        Decorated function
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
        timeout=timeout
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            handler = RetryHandler(config)
            return await handler.execute(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            handler = RetryHandler(config)
            return asyncio.run(handler.execute(func, *args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Predefined retry configurations
def retry_on_network_error(max_attempts: int = 3):
    """Retry decorator for network-related errors."""
    return retry(
        max_attempts=max_attempts,
        base_delay=1.0,
        max_delay=30.0,
        retryable_exceptions=[ConnectionError, TimeoutError, OSError]
    )


def retry_on_timeout(max_attempts: int = 3):
    """Retry decorator for timeout errors."""
    return retry(
        max_attempts=max_attempts,
        base_delay=2.0,
        max_delay=60.0,
        retryable_exceptions=[TimeoutError, TimeoutException]
    )


def retry_on_rate_limit(max_attempts: int = 3):
    """Retry decorator for rate limit errors."""
    return retry(
        max_attempts=max_attempts,
        base_delay=5.0,
        max_delay=300.0,
        retryable_exceptions=[Exception]  # Will be filtered by specific exception handling
    ) 