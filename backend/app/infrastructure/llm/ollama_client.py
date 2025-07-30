import httpx
import time
from typing import Optional, Dict, Any
from ...application.interfaces.llm_interface import LLMInterface
from ...core.config import settings
from ...core.exceptions import LLMException, ServiceUnavailableException, TimeoutException
from ...core.circuit_breaker import circuit_breaker_manager, CircuitBreakerConfig
from ...core.retry import retry_on_network_error, retry_on_timeout
from ...core.logging import get_logger, log_function_call


class OllamaClient(LLMInterface):
    """
    Ollama LLM client implementation with resilience features.
    """
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, 
                 model: str = "llama2"):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama host
            port: Ollama port
            model: Model name to use
        """
        self.host = host or settings.OLLAMA_HOST
        self.port = port or settings.OLLAMA_PORT
        self.model = model
        self.base_url = f"http://{self.host}:{self.port}"
        self.logger = get_logger("llm.ollama")
        
        # Setup circuit breaker
        circuit_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            expected_exception=(httpx.RequestError, httpx.HTTPStatusError, TimeoutException)
        )
        self.circuit_breaker = circuit_breaker_manager.get_circuit_breaker(
            f"ollama_{self.model}", circuit_config
        )
    
    @log_function_call
    async def generate_response(self, prompt: str, context: Optional[str] = None, 
                              **kwargs) -> str:
        """Generate a response from Ollama with circuit breaker protection."""
        try:
            return await self.circuit_breaker.call(
                self._generate_response_internal, prompt, context, **kwargs
            )
        except ServiceUnavailableException:
            raise LLMException(
                f"Ollama service is unavailable for model {self.model}",
                provider="ollama",
                model=self.model
            )
        except Exception as e:
            raise LLMException(
                f"Failed to generate response: {str(e)}",
                provider="ollama",
                model=self.model,
                details={"error": str(e)}
            )
    
    @retry_on_network_error(max_attempts=2)
    @retry_on_timeout(max_attempts=1)
    async def _generate_response_internal(self, prompt: str, context: Optional[str] = None, 
                                        **kwargs) -> str:
        """Internal method to generate response from Ollama."""
        try:
            # Build the full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        **kwargs
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
                
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout calling Ollama API: {e}")
            raise TimeoutException(
                f"Ollama API timeout after 60 seconds",
                operation="generate_response",
                timeout_seconds=60.0
            )
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error calling Ollama API: {e.response.status_code}")
            if e.response.status_code == 404:
                raise LLMException(
                    f"Model {self.model} not found in Ollama",
                    provider="ollama",
                    model=self.model
                )
            elif e.response.status_code >= 500:
                raise ServiceUnavailableException(
                    f"Ollama service error: {e.response.status_code}",
                    service="ollama"
                )
            else:
                raise LLMException(
                    f"Ollama API error: {e.response.status_code}",
                    provider="ollama",
                    model=self.model
                )
        except httpx.RequestError as e:
            self.logger.error(f"Request error calling Ollama API: {e}")
            raise ServiceUnavailableException(
                f"Ollama service unavailable: {str(e)}",
                service="ollama"
            )
    
    @log_function_call
    async def generate_response_with_metadata(self, prompt: str, context: Optional[str] = None,
                                           **kwargs) -> Dict[str, Any]:
        """Generate a response with metadata from Ollama."""
        start_time = time.time()
        
        try:
            response_text = await self.generate_response(prompt, context, **kwargs)
            
            processing_time = time.time() - start_time
            
            return {
                "response": response_text,
                "metadata": {
                    "provider": "ollama",
                    "model": self.model,
                    "processing_time": processing_time,
                    "prompt_tokens": len(prompt.split()),
                    "response_tokens": len(response_text.split()),
                    "total_tokens": len(prompt.split()) + len(response_text.split())
                }
            }
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "response": f"Error: {str(e)}",
                "metadata": {
                    "provider": "ollama",
                    "model": self.model,
                    "processing_time": processing_time,
                    "error": str(e)
                }
            }
    
    @log_function_call
    async def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Ollama availability check failed: {e}")
            return False
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "ollama"
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.model 