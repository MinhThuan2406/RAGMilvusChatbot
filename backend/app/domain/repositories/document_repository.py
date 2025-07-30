from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.document import Document


class DocumentRepository(ABC):
    """
    Abstract repository interface for document storage operations.
    """
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> bool:
        """
        Add multiple documents to the repository.
        
        Args:
            documents: List of documents to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by its ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            Document if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_documents_by_metadata(self, metadata_filter: Dict[str, Any], limit: int = 10) -> List[Document]:
        """
        Retrieve documents by metadata filter.
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            limit: Maximum number of documents to return
            
        Returns:
            List of matching documents
        """
        pass
    
    @abstractmethod
    async def search_similar_documents(self, query_embedding: List[float], n_results: int = 5, 
                                     metadata_filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Search for documents similar to the given embedding.
        
        Args:
            query_embedding: The query embedding vector
            n_results: Number of similar documents to return
            metadata_filter: Optional metadata filter
            
        Returns:
            List of similar documents ordered by similarity
        """
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            document_id: The document ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_documents_by_metadata(self, metadata_filter: Dict[str, Any]) -> int:
        """
        Delete documents matching the metadata filter.
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            
        Returns:
            int: Number of documents deleted
        """
        pass
    
    @abstractmethod
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the document collection.
        
        Returns:
            Dictionary containing collection statistics
        """
        pass 