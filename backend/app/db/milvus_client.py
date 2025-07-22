from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from typing import List, Optional, Any, Dict
from ..core.config import settings

class MilvusDBClient:
    def get_documents_by_metadata(self, metadata: Dict[str, Any], limit: int = 1) -> Any:
        """
        Query documents by metadata fields (e.g., source filename).
        """
        expr = " and ".join([f"{k} == '{v}'" for k, v in metadata.items()])
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            results = self._collection.query(expr=expr, limit=limit, output_fields=["id", "text", "metadata"])
            return results
        except Exception as e:
            print(f"[ERROR] Exception in get_documents_by_metadata: {e}")
            return None

    def get_documents_by_ids(self, ids: List[str]) -> Any:
        """
        Query documents by their IDs.
        """
        expr = f"id in [{', '.join([repr(i) for i in ids])}]"
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            results = self._collection.query(expr=expr, output_fields=["id", "text", "metadata"])
            found_ids = [doc['id'] for doc in results] if results else []
            return {"ids": found_ids, "docs": results}
        except Exception as e:
            print(f"[ERROR] Exception in get_documents_by_ids: {e}")
            return {"ids": [], "docs": []}
    """
    Client for interacting with Milvus vector database.
    Handles connection, collection management, and document operations.
    """
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, embedding_function=None) -> None:
        self._host = host or getattr(settings, "MILVUS_HOST", "localhost")
        self._port = port or getattr(settings, "MILVUS_PORT", "19530")
        self._embedding_function = embedding_function
        self._collection_name = "rag_documents"
        self._collection = None
        connections.connect(host=self._host, port=self._port)
        self._init_collection()

    def _init_collection(self):
        # Define schema if not exists
        try:
            from pymilvus import list_collections
            existing_collections = list_collections()
        except Exception:
            existing_collections = []
        if self._collection_name not in existing_collections:
            id_field = FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=64)
            embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)  # Adjust dim as needed
            text_field = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
            metadata_field = FieldSchema(name="metadata", dtype=DataType.JSON)
            schema = CollectionSchema(fields=[id_field, embedding_field, text_field, metadata_field], description="RAG documents")
            self._collection = Collection(name=self._collection_name, schema=schema)
        else:
            self._collection = Collection(self._collection_name)

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> bool:
        if self._collection is None:
            raise RuntimeError("Milvus collection is not initialized.")
        if self._embedding_function is None:
            raise RuntimeError("Embedding function is not set.")
        try:
            embeddings = self._embedding_function(documents)
            entities = [ids, embeddings, documents, metadatas]
            self._collection.insert(entities)
            return True
        except Exception as e:
            print(f"[ERROR] Exception in add_documents: {e}")
            return False

    def query_documents(self, query_texts: List[str], n_results: int = 5, **kwargs) -> Any:
        if self._collection is None:
            raise RuntimeError("Milvus collection is not initialized.")
        if self._embedding_function is None:
            raise RuntimeError("Embedding function is not set.")
        try:
            query_embeddings = self._embedding_function(query_texts)
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = self._collection.search(query_embeddings, "embedding", search_params, limit=n_results, output_fields=["id", "text", "metadata"])
            return results
        except Exception as e:
            print(f"[ERROR] Exception in query_documents: {e}")
            return None

__all__ = ["MilvusDBClient"]
