import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.domain.entities.document import Document
from app.domain.entities.query import Query
from app.domain.entities.response import Response
from app.application.dto.chat_dto import ChatRequestDTO, ChatResponseDTO
from app.application.use_cases.chat_use_case import ChatUseCase
from app.domain.services.rag_service import RAGService
from app.application.interfaces.llm_interface import LLMInterface
from app.application.interfaces.embedding_interface import EmbeddingInterface
from app.domain.repositories.document_repository import DocumentRepository
from typing import Optional


class MockLLMProvider(LLMInterface):
    """Mock LLM provider for testing."""
    
    async def generate_response(self, prompt: str, context: Optional[str] = None, **kwargs) -> str:
        return "This is a mock response."
    
    async def generate_response_with_metadata(self, prompt: str, context: Optional[str] = None, **kwargs):
        return {
            "response": "This is a mock response.",
            "metadata": {
                "provider": "mock",
                "model": "mock-model",
                "processing_time": 0.1
            }
        }
    
    async def is_available(self) -> bool:
        return True
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    @property
    def model_name(self) -> str:
        return "mock-model"


class MockEmbeddingProvider(EmbeddingInterface):
    """Mock embedding provider for testing."""
    
    async def create_embedding(self, text: str) -> list[float]:
        return [0.1] * 768  # Mock embedding
    
    async def create_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 768 for _ in texts]
    
    async def is_available(self) -> bool:
        return True
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    @property
    def embedding_dimension(self) -> int:
        return 768
    
    @property
    def model_name(self) -> str:
        return "mock-model"


class MockDocumentRepository(DocumentRepository):
    """Mock document repository for testing."""
    
    async def add_documents(self, documents: list[Document]) -> bool:
        return True
    
    async def get_document_by_id(self, document_id: str):
        return Document(
            id=document_id,
            content="Mock document content",
            metadata={"source": "mock.pdf"}
        )
    
    async def get_documents_by_metadata(self, metadata_filter: dict, limit: int = 10):
        return [
            Document(
                id="mock-1",
                content="Mock document content 1",
                metadata={"source": "mock.pdf", "page": 1}
            ),
            Document(
                id="mock-2", 
                content="Mock document content 2",
                metadata={"source": "mock.pdf", "page": 2}
            )
        ]
    
    async def search_similar_documents(self, query_embedding: list[float], n_results: int = 5, metadata_filter=None):
        return [
            Document(
                id="mock-1",
                content="Mock document content 1",
                metadata={"source": "mock.pdf", "page": 1}
            ),
            Document(
                id="mock-2",
                content="Mock document content 2", 
                metadata={"source": "mock.pdf", "page": 2}
            )
        ]
    
    async def delete_document(self, document_id: str) -> bool:
        return True
    
    async def delete_documents_by_metadata(self, metadata_filter: dict) -> int:
        return 1
    
    async def get_collection_stats(self) -> dict:
        return {
            "collection_name": "mock_collection",
            "row_count": 10,
            "index_status": "built"
        }


@pytest.mark.asyncio
async def test_document_entity():
    """Test Document entity creation and methods."""
    doc = Document(
        id="test-1",
        content="Test document content",
        metadata={"source": "test.pdf", "page": 1}
    )
    
    assert doc.id == "test-1"
    assert doc.content == "Test document content"
    assert doc.source == "test.pdf"
    assert doc.page == 1
    
    # Test embedding update
    embedding = [0.1] * 768
    doc.update_embedding(embedding)
    assert doc.embedding == embedding


@pytest.mark.asyncio
async def test_query_entity():
    """Test Query entity creation and methods."""
    query = Query(
        id="query-1",
        text="What is the main topic?",
        metadata={"provider": "ollama", "source_filter": "test.pdf"}
    )
    
    assert query.id == "query-1"
    assert query.text == "What is the main topic?"
    assert query.provider == "ollama"
    assert query.source_filter == "test.pdf"


@pytest.mark.asyncio
async def test_response_entity():
    """Test Response entity creation and methods."""
    documents = [
        Document(id="doc-1", content="Content 1", metadata={"source": "test.pdf"}),
        Document(id="doc-2", content="Content 2", metadata={"source": "test.pdf"})
    ]
    
    response = Response(
        id="resp-1",
        answer="This is the answer",
        query_id="query-1",
        context_documents=documents,
        metadata={"provider": "ollama"}
    )
    
    assert response.id == "resp-1"
    assert response.answer == "This is the answer"
    assert len(response.sources) == 1
    assert "test.pdf" in response.sources


@pytest.mark.asyncio
async def test_rag_service():
    """Test RAG service functionality."""
    mock_llm = MockLLMProvider()
    mock_embedding = MockEmbeddingProvider()
    mock_repo = MockDocumentRepository()
    
    rag_service = RAGService(
        document_repository=mock_repo,
        llm_provider=mock_llm,
        embedding_provider=mock_embedding
    )
    
    # Test system stats
    stats = await rag_service.get_system_stats()
    assert "llm_provider" in stats
    assert "embedding_provider" in stats
    assert "document_repository" in stats


@pytest.mark.asyncio
async def test_chat_use_case():
    """Test Chat use case functionality."""
    mock_llm = MockLLMProvider()
    mock_embedding = MockEmbeddingProvider()
    mock_repo = MockDocumentRepository()
    
    rag_service = RAGService(
        document_repository=mock_repo,
        llm_provider=mock_llm,
        embedding_provider=mock_embedding
    )
    
    chat_use_case = ChatUseCase(rag_service=rag_service)
    
    # Test chat request
    request_dto = ChatRequestDTO(
        query="What is the main topic?",
        provider="ollama"
    )
    
    response_dto = await chat_use_case.execute(request_dto)
    
    assert isinstance(response_dto, ChatResponseDTO)
    assert response_dto.answer is not None
    assert response_dto.query_id is not None


@pytest.mark.asyncio
async def test_chat_dto():
    """Test Chat DTOs."""
    request_dto = ChatRequestDTO(
        query="Test question",
        provider="ollama",
        file_name="test.pdf",
        max_results=5
    )
    
    assert request_dto.query == "Test question"
    assert request_dto.provider == "ollama"
    assert request_dto.file_name == "test.pdf"
    assert request_dto.max_results == 5
    
    response_dto = ChatResponseDTO(
        answer="Test answer",
        query_id="query-1",
        sources=["test.pdf"],
        context_documents=[],
        metadata={"provider": "ollama"}
    )
    
    assert response_dto.answer == "Test answer"
    assert response_dto.query_id == "query-1"
    assert len(response_dto.sources) == 1 