from abc import ABC, abstractmethod

class AbstractLLMClient(ABC):
    """
    Abstract base class for LLM (Large Language Model) clients.
    """
    @abstractmethod
    async def generate_response(self, prompt: str, context: str | None = None) -> str:
        """
        Generate a response from the LLM given a prompt and optional context.
        Args:
            prompt (str): The user query or prompt.
            context (str | None): Optional context to augment the prompt.
        Returns:
            str: The generated response from the LLM.
        """
        pass

class AbstractEmbeddingClient(ABC):
    """
    Abstract base class for embedding clients.
    """
    @abstractmethod
    async def create_embedding(self, text: str) -> list[float]:
        """
        Create an embedding for the given text.
        Args:
            text (str): The input text to embed.
        Returns:
            list[float]: The embedding vector.
        """
        pass
