import os
from typing import List, Optional, Dict, Any
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from ...domain.repositories.document_repository import DocumentRepository
from ...domain.entities.document import Document
from ...core.config import settings


class MilvusDocumentRepository(DocumentRepository):
    """
    Milvus implementation of the DocumentRepository interface.
    """
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, 
                 embedding_function=None):
        """
        Initialize Milvus repository.
        
        Args:
            host: Milvus host
            port: Milvus port
            embedding_function: Function to generate embeddings
        """
        self._embedding_function = embedding_function
        self._collection_name = "rag_documents"
        self._collection = None
        
        # Connect to Milvus
        self._connect_to_milvus(host, port)
        self._init_collection()
    
    def _connect_to_milvus(self, host: Optional[str], port: Optional[int]):
        """Connect to Milvus instance."""
        milvus_uri = os.getenv("MILVUS_URI") or getattr(settings, "MILVUS_URI", None)
        
        if milvus_uri:
            # Local mode (standalone)
            if milvus_uri.startswith("file://"):
                local_path = milvus_uri.replace("file://", "")
                if not os.path.exists(local_path):
                    raise RuntimeError(f"Milvus local directory does not exist: {local_path}")
            try:
                connections.connect(uri=milvus_uri)
            except Exception as e:
                print(f"[ERROR] Failed to connect to Milvus with URI {milvus_uri}: {e}")
                raise
        else:
            # Remote mode (docker compose)
            self._host = host or os.getenv("MILVUS_HOST") or getattr(settings, "MILVUS_HOST", "milvus-db")
            self._port = port or int(os.getenv("MILVUS_PORT") or getattr(settings, "MILVUS_PORT", 19530))
            try:
                connections.connect(host=self._host, port=self._port)
            except Exception as e:
                print(f"[ERROR] Failed to connect to Milvus at {self._host}:{self._port}: {e}")
                raise
    
    def _init_collection(self):
        """Initialize the Milvus collection."""
        try:
            from pymilvus import list_collections
            existing_collections = list_collections()
        except Exception:
            existing_collections = []
        
        if self._collection_name not in existing_collections:
            # Define schema
            id_field = FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=64)
            embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
            text_field = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
            metadata_field = FieldSchema(name="metadata", dtype=DataType.JSON)
            
            schema = CollectionSchema(
                fields=[id_field, embedding_field, text_field, metadata_field], 
                description="RAG documents"
            )
            self._collection = Collection(name=self._collection_name, schema=schema)
        else:
            self._collection = Collection(self._collection_name)
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """Add multiple documents to the repository."""
        if self._collection is None:
            raise RuntimeError("Milvus collection is not initialized.")
        
        if self._embedding_function is None:
            raise RuntimeError("Embedding function is not set.")
        
        try:
            # Prepare data for insertion
            ids = [doc.id for doc in documents]
            texts = [doc.content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Generate embeddings if not already present
            embeddings = []
            for doc in documents:
                if doc.embedding is None:
                    embedding = await self._embedding_function(doc.content)
                    doc.update_embedding(embedding)
                embeddings.append(doc.embedding)
            
            # Insert into Milvus
            entities = [ids, embeddings, texts, metadatas]
            self._collection.insert(entities)
            self._collection.flush()
            
            return True
        except Exception as e:
            print(f"[ERROR] Exception in add_documents: {e}")
            return False
    
    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by its ID."""
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            expr = f'id == "{document_id}"'
            results = self._collection.query(expr=expr, output_fields=["id", "text", "metadata", "embedding"])
            
            if results:
                doc_data = results[0]
                return Document(
                    id=doc_data["id"],
                    content=doc_data["text"],
                    metadata=doc_data["metadata"],
                    embedding=doc_data.get("embedding")
                )
            return None
        except Exception as e:
            print(f"[ERROR] Exception in get_document_by_id: {e}")
            return None
    
    async def get_documents_by_metadata(self, metadata_filter: Dict[str, Any], limit: int = 10) -> List[Document]:
        """Retrieve documents by metadata filter."""
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            # Build filter expression
            expr_parts = []
            for key, value in metadata_filter.items():
                if isinstance(value, str):
                    expr_parts.append(f'{key} == "{value}"')
                else:
                    expr_parts.append(f'{key} == {value}')
            
            expr = " and ".join(expr_parts)
            results = self._collection.query(
                expr=expr, 
                limit=limit, 
                output_fields=["id", "text", "metadata", "embedding"]
            )
            
            documents = []
            for doc_data in results:
                documents.append(Document(
                    id=doc_data["id"],
                    content=doc_data["text"],
                    metadata=doc_data["metadata"],
                    embedding=doc_data.get("embedding")
                ))
            
            return documents
        except Exception as e:
            print(f"[ERROR] Exception in get_documents_by_metadata: {e}")
            return []
    
    async def search_similar_documents(self, query_embedding: List[float], n_results: int = 5,
                                     metadata_filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Search for documents similar to the given embedding."""
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            # Build search parameters
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            
            # Build filter expression if provided
            expr = None
            if metadata_filter:
                expr_parts = []
                for key, value in metadata_filter.items():
                    if isinstance(value, str):
                        expr_parts.append(f'{key} == "{value}"')
                    else:
                        expr_parts.append(f'{key} == {value}')
                expr = " and ".join(expr_parts)
            
            # Perform search
            results = self._collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=n_results,
                expr=expr,
                output_fields=["id", "text", "metadata", "embedding"]
            )
            
            documents = []
            for hit in results[0]:
                doc_data = hit.entity
                documents.append(Document(
                    id=doc_data.get("id"),
                    content=doc_data.get("text"),
                    metadata=doc_data.get("metadata", {}),
                    embedding=doc_data.get("embedding")
                ))
            
            return documents
        except Exception as e:
            print(f"[ERROR] Exception in search_similar_documents: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document by its ID."""
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            expr = f'id == "{document_id}"'
            self._collection.delete(expr)
            return True
        except Exception as e:
            print(f"[ERROR] Exception in delete_document: {e}")
            return False
    
    async def delete_documents_by_metadata(self, metadata_filter: Dict[str, Any]) -> int:
        """Delete documents matching the metadata filter."""
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            # Build filter expression
            expr_parts = []
            for key, value in metadata_filter.items():
                if isinstance(value, str):
                    expr_parts.append(f'{key} == "{value}"')
                else:
                    expr_parts.append(f'{key} == {value}')
            
            expr = " and ".join(expr_parts)
            self._collection.delete(expr)
            return 1  # Milvus doesn't return count, assume 1
        except Exception as e:
            print(f"[ERROR] Exception in delete_documents_by_metadata: {e}")
            return 0
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            stats = self._collection.get_statistics()
            return {
                "collection_name": self._collection_name,
                "row_count": stats.get("row_count", 0),
                "index_status": "built"  # Assuming index is built
            }
        except Exception as e:
            print(f"[ERROR] Exception in get_collection_stats: {e}")
            return {"error": str(e)} 