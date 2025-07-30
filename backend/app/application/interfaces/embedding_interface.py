from abc import ABC, abstractmethod
from typing import List, Dict, Any


class EmbeddingInterface(ABC):
    """
    Abstract interface for embedding providers.
    """
    
    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for the given text.
        
        Args:
            text: The input text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        pass
    
    @abstractmethod
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the embedding service is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the name of the embedding provider.
        
        Returns:
            str: Provider name (e.g., 'openai', 'sentence-transformers')
        """
        pass
    
    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: Embedding dimension
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the specific embedding model being used.
        
        Returns:
            str: Model name
        """
        pass 