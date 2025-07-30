from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequestDTO(BaseModel):
    """
    Data Transfer Object for chat requests.
    """
    query: str = Field(..., description="The user's question or query")
    provider: Optional[str] = Field(default="ollama", description="LLM provider to use")
    file_name: Optional[str] = Field(default=None, description="Optional file filter")
    max_results: Optional[int] = Field(default=5, description="Maximum number of context documents to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the main topic of the document?",
                "provider": "ollama",
                "file_name": "document.pdf",
                "max_results": 5
            }
        }


class ChatResponseDTO(BaseModel):
    """
    Data Transfer Object for chat responses.
    """
    answer: str = Field(..., description="The generated answer")
    query_id: str = Field(..., description="Unique identifier for the query")
    sources: List[str] = Field(default_factory=list, description="Source files used")
    context_documents: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved context documents")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The main topic of the document is...",
                "query_id": "uuid-12345",
                "sources": ["document.pdf"],
                "context_documents": [
                    {
                        "id": "doc-1",
                        "content": "This document discusses...",
                        "metadata": {"source": "document.pdf", "page": 1}
                    }
                ],
                "metadata": {
                    "provider": "ollama",
                    "processing_time": 2.5,
                    "tokens_used": 150
                }
            }
        }


@dataclass
class ChatRequest:
    """
    Internal chat request object.
    """
    query: str
    provider: str = "ollama"
    file_name: Optional[str] = None
    max_results: int = 5
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChatResponse:
    """
    Internal chat response object.
    """
    answer: str
    query_id: str
    sources: List[str]
    context_documents: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def to_dto(self) -> ChatResponseDTO:
        """Convert to DTO for API response."""
        return ChatResponseDTO(
            answer=self.answer,
            query_id=self.query_id,
            sources=self.sources,
            context_documents=self.context_documents,
            metadata=self.metadata
        ) 