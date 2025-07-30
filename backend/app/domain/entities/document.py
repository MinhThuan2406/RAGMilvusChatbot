from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4


@dataclass
class Document:
    """
    Domain entity representing a document in the RAG system.
    """
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[list[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate and set default values after initialization."""
        if not self.id:
            self.id = str(uuid4())
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
        
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    @property
    def source(self) -> Optional[str]:
        """Get the source filename from metadata."""
        return self.metadata.get("source")
    
    @property
    def page(self) -> Optional[int]:
        """Get the page number from metadata."""
        return self.metadata.get("page")
    
    def update_embedding(self, embedding: list[float]) -> None:
        """Update the document's embedding vector."""
        self.embedding = embedding
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create a Document instance from a dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"])
        
        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data["metadata"],
            embedding=data.get("embedding"),
            created_at=created_at,
            updated_at=updated_at
        ) 