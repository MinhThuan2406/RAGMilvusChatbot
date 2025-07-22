from ..core.config import settings
from ..core.interfaces import AbstractLLMClient, AbstractEmbeddingClient

from ..adapters.ollama_adapter import OllamaAdapter
import os
from typing import Optional

class LLMFactory:
    @staticmethod
    def get_llm_client(provider: Optional[str] = None) -> AbstractLLMClient:
        provider_str = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()
        if provider_str == "openai":
            from ..adapters.openai_adapter import OpenAIAdapter
            return OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY", ""))
        return OllamaAdapter(host=settings.OLLAMA_HOST, port=settings.OLLAMA_PORT)

    @staticmethod
    def get_embedding_client(provider: Optional[str] = None) -> AbstractEmbeddingClient:
        """
        Always return an OpenAIAdapter for embeddings, regardless of provider.
        """
        from ..adapters.openai_adapter import OpenAIAdapter
        return OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY", ""))