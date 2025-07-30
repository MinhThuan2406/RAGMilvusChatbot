from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMInterface(ABC):
    """
    Abstract interface for LLM (Large Language Model) providers.
    """
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None, 
                              **kwargs) -> str:
        """
        Generate a response from the LLM given a prompt and optional context.
        
        Args:
            prompt: The user query or prompt
            context: Optional context to augment the prompt
            **kwargs: Additional parameters for the LLM call
            
        Returns:
            str: The generated response from the LLM
        """
        pass
    
    @abstractmethod
    async def generate_response_with_metadata(self, prompt: str, context: Optional[str] = None,
                                           **kwargs) -> Dict[str, Any]:
        """
        Generate a response with additional metadata (tokens used, processing time, etc.).
        
        Args:
            prompt: The user query or prompt
            context: Optional context to augment the prompt
            **kwargs: Additional parameters for the LLM call
            
        Returns:
            Dict containing response and metadata
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the LLM service is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the name of the LLM provider.
        
        Returns:
            str: Provider name (e.g., 'ollama', 'openai')
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the specific model being used.
        
        Returns:
            str: Model name
        """
        pass 