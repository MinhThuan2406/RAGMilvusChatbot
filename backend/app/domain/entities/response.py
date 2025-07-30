from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from .document import Document


@dataclass
class Response:
    """
    Domain entity representing a RAG response with context and sources.
    """
    id: str
    answer: str
    query_id: str
    context_documents: List[Document]
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate and set default values after initialization."""
        if not self.id:
            self.id = str(uuid4())
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @property
    def sources(self) -> List[str]:
        """Get list of unique source files used in the response."""
        sources = []
        for doc in self.context_documents:
            if doc.source and doc.source not in sources:
                sources.append(doc.source)
        return sources
    
    @property
    def context_text(self) -> str:
        """Get the combined context text from all documents."""
        return "\n".join([doc.content for doc in self.context_documents])
    
    @property
    def provider(self) -> Optional[str]:
        """Get the LLM provider from metadata."""
        return self.metadata.get("provider")
    
    @property
    def processing_time(self) -> Optional[float]:
        """Get the processing time in seconds from metadata."""
        return self.metadata.get("processing_time")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary representation."""
        return {
            "id": self.id,
            "answer": self.answer,
            "query_id": self.query_id,
            "context_documents": [doc.to_dict() for doc in self.context_documents],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sources": self.sources,
            "context_text": self.context_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Response":
        """Create a Response instance from a dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        context_documents = []
        for doc_data in data.get("context_documents", []):
            context_documents.append(Document.from_dict(doc_data))
        
        return cls(
            id=data["id"],
            answer=data["answer"],
            query_id=data["query_id"],
            context_documents=context_documents,
            metadata=data["metadata"],
            created_at=created_at
        ) 