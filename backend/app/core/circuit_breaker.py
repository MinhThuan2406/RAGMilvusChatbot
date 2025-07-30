import time
import asyncio
from typing import Callable, Any, Optional, Dict
from enum import Enum
from dataclasses import dataclass
from .exceptions import ServiceUnavailableException


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5        # Number of failures before opening
    recovery_timeout: float = 60.0    # Seconds to wait before half-open
    expected_exception: type = Exception  # Exception type to count as failure
    success_threshold: int = 2        # Number of successes to close circuit


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for external service calls.
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.success_count = 0
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            ServiceUnavailableException: When circuit is open
        """
        async with self._lock:
            await self._check_state()
            
            if self.state == CircuitState.OPEN:
                raise ServiceUnavailableException(
                    f"Circuit breaker '{self.name}' is OPEN",
                    service=self.name,
                    details={
                        "failure_count": self.failure_count,
                        "last_failure_time": self.last_failure_time,
                        "recovery_timeout": self.config.recovery_timeout
                    }
                )
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - update circuit state
            await self._on_success()
            return result
            
        except self.config.expected_exception as e:
            # Failure - update circuit state
            await self._on_failure()
            raise e
    
    async def _check_state(self):
        """Check and update circuit state."""
        current_time = time.time()
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if current_time - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.failure_count = 0
    
    async def _on_success(self):
        """Handle successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
    
    async def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold
            }
        }


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.
    """
    
    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    def get_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """
        Get or create a circuit breaker.
        
        Args:
            name: Circuit breaker name
            config: Configuration (uses default if not provided)
            
        Returns:
            CircuitBreaker instance
        """
        if name not in self._circuit_breakers:
            if config is None:
                config = CircuitBreakerConfig()
            self._circuit_breakers[name] = CircuitBreaker(name, config)
        
        return self._circuit_breakers[name]
    
    async def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {name: cb.get_status() for name, cb in self._circuit_breakers.items()}
    
    def reset_circuit_breaker(self, name: str):
        """Reset a circuit breaker to closed state."""
        if name in self._circuit_breakers:
            cb = self._circuit_breakers[name]
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
            cb.success_count = 0
            cb.last_failure_time = 0.0


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager() 