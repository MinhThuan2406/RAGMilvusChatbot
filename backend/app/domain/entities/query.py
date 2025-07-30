from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


@dataclass
class Query:
    """
    Domain entity representing a user query in the RAG system.
    """
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[list[float]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate and set default values after initialization."""
        if not self.id:
            self.id = str(uuid4())
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
    
    @property
    def source_filter(self) -> Optional[str]:
        """Get the source filter from metadata."""
        return self.metadata.get("source_filter")
    
    @property
    def provider(self) -> Optional[str]:
        """Get the LLM provider from metadata."""
        return self.metadata.get("provider", "ollama")
    
    def update_embedding(self, embedding: list[float]) -> None:
        """Update the query's embedding vector."""
        self.embedding = embedding
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the query to a dictionary representation."""
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Query":
        """Create a Query instance from a dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        return cls(
            id=data["id"],
            text=data["text"],
            metadata=data["metadata"],
            embedding=data.get("embedding"),
            created_at=created_at
        ) 