import openai
from typing import List
from ...application.interfaces.embedding_interface import EmbeddingInterface


class OpenAIEmbeddingClient(EmbeddingInterface):
    """
    OpenAI embedding client implementation.
    """
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embedding client.
        
        Args:
            api_key: OpenAI API key
            model: Embedding model name
        """
        self.api_key = api_key
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create an embedding for the given text."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding from OpenAI: {e}")
            # Return a zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Error creating embeddings from OpenAI: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.embedding_dimension for _ in texts]
    
    async def is_available(self) -> bool:
        """Check if OpenAI embedding service is available."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input="test"
            )
            return True
        except Exception:
            return False
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"
    
    @property
    def embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        # OpenAI text-embedding-ada-002 has 1536 dimensions
        return 1536
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.model 