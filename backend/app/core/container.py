import os
from typing import Optional
from .config import settings
from ..domain.services.rag_service import RAGService
from ..domain.repositories.document_repository import DocumentRepository
from ..application.interfaces.llm_interface import LLMInterface
from ..application.interfaces.embedding_interface import EmbeddingInterface
from ..application.use_cases.chat_use_case import ChatUseCase
from ..presentation.controllers.chat_controller import ChatController
from ..infrastructure.database.milvus_repository import MilvusDocumentRepository
from ..infrastructure.llm.ollama_client import OllamaClient
from ..infrastructure.llm.openai_client import OpenAIClient
from ..infrastructure.llm.openai_embedding_client import OpenAIEmbeddingClient


class Container:
    """
    Dependency injection container for the application.
    """
    
    def __init__(self):
        self._rag_service: Optional[RAGService] = None
        self._chat_use_case: Optional[ChatUseCase] = None
        self._chat_controller: Optional[ChatController] = None
        self._document_repository: Optional[DocumentRepository] = None
        self._llm_provider: Optional[LLMInterface] = None
        self._embedding_provider: Optional[EmbeddingInterface] = None
    
    def get_embedding_provider(self) -> EmbeddingInterface:
        """Get the embedding provider instance."""
        if self._embedding_provider is None:
            # Always use OpenAI for embeddings
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self._embedding_provider = OpenAIEmbeddingClient(api_key=api_key)
        
        return self._embedding_provider
    
    def get_llm_provider(self, provider: str = "ollama") -> LLMInterface:
        """Get the LLM provider instance."""
        if self._llm_provider is None:
            if provider.lower() == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is required")
                self._llm_provider = OpenAIClient(api_key=api_key)
            else:
                # Default to Ollama
                self._llm_provider = OllamaClient(
                    host=settings.OLLAMA_HOST,
                    port=settings.OLLAMA_PORT
                )
        
        return self._llm_provider
    
    def get_document_repository(self) -> DocumentRepository:
        """Get the document repository instance."""
        if self._document_repository is None:
            embedding_provider = self.get_embedding_provider()
            
            # Create embedding function wrapper
            async def embedding_function(text: str) -> list[float]:
                return await embedding_provider.create_embedding(text)
            
            self._document_repository = MilvusDocumentRepository(
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
                embedding_function=embedding_function
            )
        
        return self._document_repository
    
    def get_rag_service(self, provider: str = "ollama") -> RAGService:
        """Get the RAG service instance."""
        if self._rag_service is None:
            document_repository = self.get_document_repository()
            llm_provider = self.get_llm_provider(provider)
            embedding_provider = self.get_embedding_provider()
            
            self._rag_service = RAGService(
                document_repository=document_repository,
                llm_provider=llm_provider,
                embedding_provider=embedding_provider
            )
        
        return self._rag_service
    
    def get_chat_use_case(self, provider: str = "ollama") -> ChatUseCase:
        """Get the chat use case instance."""
        if self._chat_use_case is None:
            rag_service = self.get_rag_service(provider)
            self._chat_use_case = ChatUseCase(rag_service=rag_service)
        
        return self._chat_use_case
    
    def get_chat_controller(self, provider: str = "ollama") -> ChatController:
        """Get the chat controller instance."""
        if self._chat_controller is None:
            chat_use_case = self.get_chat_use_case(provider)
            self._chat_controller = ChatController(chat_use_case=chat_use_case)
        
        return self._chat_controller


# Global container instance
container = Container() 