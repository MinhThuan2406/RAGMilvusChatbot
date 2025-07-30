from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, IndexType
from typing import List, Optional, Any, Dict
from ..core.config import settings
import os

class MilvusDBClient:
    def get_documents_by_metadata(self, metadata: Dict[str, Any], limit: int = 1) -> Any:
        """
        Query documents by metadata fields (e.g., source filename).
        """
        self._ensure_connected()
        # Build expression for JSON metadata field
        expr_parts = []
        for key, value in metadata.items():
            if isinstance(value, str):
                expr_parts.append(f'JSON_CONTAINS(metadata, \'{{"{key}": "{value}"}}\')')
            else:
                expr_parts.append(f'JSON_CONTAINS(metadata, \'{{"{key}": {value}}}\')')
        
        expr = " and ".join(expr_parts) if expr_parts else ""
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            # Load collection before querying
            self._collection.load()
            
            results = self._collection.query(expr=expr, limit=limit, output_fields=["id", "text", "metadata"])
            return results
        except Exception as e:
            print(f"[ERROR] Exception in get_documents_by_metadata: {e}")
            return None

    def get_documents_by_ids(self, ids: List[str]) -> Any:
        """
        Query documents by their IDs.
        """
        self._ensure_connected()
        expr = f"id in [{', '.join([repr(i) for i in ids])}]"
        try:
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            # Load collection before querying
            self._collection.load()
            
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
        """
        Initialize Milvus client. Supports both remote (host/port) and local (uri) connection.
        Uses lazy initialization to avoid connection issues during startup.
        """
        self._embedding_function = embedding_function
        self._collection_name = "rag_documents"
        self._collection = None
        self._connected = False
        
        # Store connection parameters for lazy initialization
        milvus_uri = os.getenv("MILVUS_URI") or getattr(settings, "MILVUS_URI", None)
        if milvus_uri:
            # Local mode (standalone)
            self._connection_mode = "uri"
            self._connection_params = {"uri": milvus_uri}
        else:
            # Remote mode (docker compose)
            self._connection_mode = "host_port"
            self._host = host or os.getenv("MILVUS_HOST") or getattr(settings, "MILVUS_HOST", "milvus-db")
            self._port = port or int(os.getenv("MILVUS_PORT") or getattr(settings, "MILVUS_PORT", 19530))
            self._connection_params = {"host": self._host, "port": self._port}

    def _ensure_connected(self):
        """Ensure connection to Milvus is established."""
        if self._connected:
            return
            
        try:
            if self._connection_mode == "uri":
                # Local mode (standalone)
                uri = self._connection_params["uri"]
                if uri.startswith("file://"):
                    local_path = uri.replace("file://", "")
                    if not os.path.exists(local_path):
                        raise RuntimeError(f"Milvus local directory does not exist: {local_path}")
                connections.connect(uri=uri)
            else:
                # Remote mode (docker compose) - try multiple connection methods
                host = self._connection_params["host"]
                port = self._connection_params["port"]
                
                print(f"[DEBUG] Attempting to connect to Milvus at {host}:{port}")
                
                # Method 1: Basic connection with timeout
                try:
                    connections.connect(
                        alias="default",
                        host=host,
                        port=port,
                        timeout=30
                    )
                    print(f"[DEBUG] Successfully connected using basic connection")
                except Exception as e1:
                    print(f"[DEBUG] Basic connection failed: {e1}")
                    
                    # Method 2: Try with explicit user/password (empty for no auth)
                    try:
                        connections.connect(
                            alias="default",
                            host=host,
                            port=port,
                            user="",
                            password="",
                            timeout=30
                        )
                        print(f"[DEBUG] Successfully connected using auth connection")
                    except Exception as e2:
                        print(f"[DEBUG] Auth connection failed: {e2}")
                        
                        # Method 3: Try with different alias
                        try:
                            connections.connect(
                                alias="milvus_connection",
                                host=host,
                                port=port,
                                timeout=30
                            )
                            print(f"[DEBUG] Successfully connected using custom alias")
                        except Exception as e3:
                            print(f"[DEBUG] Custom alias connection failed: {e3}")
                            raise e3
            
            self._connected = True
            self._init_collection()
        except Exception as e:
            print(f"[ERROR] Failed to connect to Milvus: {e}")
            raise

    def _init_collection(self):
        """Initialize the Milvus collection with proper index creation."""
        try:
            from pymilvus import list_collections
            existing_collections = list_collections()
        except Exception as e:
            print(f"[WARNING] Could not list collections: {e}")
            existing_collections = []
            
        if self._collection_name not in existing_collections:
            print(f"[INFO] Creating new collection: {self._collection_name}")
            # Define schema for new collection
            id_field = FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=64)
            embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)  # Adjust dim as needed
            text_field = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
            metadata_field = FieldSchema(name="metadata", dtype=DataType.JSON)
            schema = CollectionSchema(fields=[id_field, embedding_field, text_field, metadata_field], description="RAG documents")
            self._collection = Collection(name=self._collection_name, schema=schema)
            
            # Create index for the embedding field
            print(f"[INFO] Creating index for collection: {self._collection_name}")
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            self._collection.create_index(field_name="embedding", index_params=index_params)
            print(f"[INFO] Index created successfully for collection: {self._collection_name}")
        else:
            print(f"[INFO] Using existing collection: {self._collection_name}")
            self._collection = Collection(self._collection_name)
            
            # Check if index exists, if not create it
            try:
                # Try to get index info
                index_info = self._collection.index()
                print(f"[DEBUG] Current index info: {index_info}")
                
                # Check if there's an index on the embedding field
                has_embedding_index = False
                if index_info:
                    for index in index_info:
                        if 'field_name' in index and index['field_name'] == 'embedding':
                            has_embedding_index = True
                            break
                
                if not has_embedding_index:
                    print(f"[INFO] No index found for embedding field in collection {self._collection_name}, creating one...")
                    index_params = {
                        "metric_type": "L2",
                        "index_type": "IVF_FLAT",
                        "params": {"nlist": 128}
                    }
                    self._collection.create_index(field_name="embedding", index_params=index_params)
                    print(f"[INFO] Index created successfully for existing collection: {self._collection_name}")
                else:
                    print(f"[INFO] Index already exists for collection: {self._collection_name}")
            except Exception as e:
                print(f"[WARNING] Could not check/create index: {e}")
                # If we can't check the index, try to create one anyway
                try:
                    print(f"[INFO] Attempting to create index for collection {self._collection_name}...")
                    index_params = {
                        "metric_type": "L2",
                        "index_type": "IVF_FLAT",
                        "params": {"nlist": 128}
                    }
                    self._collection.create_index(field_name="embedding", index_params=index_params)
                    print(f"[INFO] Index created successfully for collection: {self._collection_name}")
                except Exception as create_e:
                    print(f"[ERROR] Failed to create index: {create_e}")
                    # If index creation fails, we might need to drop and recreate the collection
                    print(f"[INFO] Attempting to drop and recreate collection {self._collection_name}...")
                    try:
                        from pymilvus import utility
                        utility.drop_collection(self._collection_name)
                        print(f"[INFO] Dropped collection {self._collection_name}")
                        
                        # Recreate collection
                        id_field = FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=64)
                        embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
                        text_field = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
                        metadata_field = FieldSchema(name="metadata", dtype=DataType.JSON)
                        schema = CollectionSchema(fields=[id_field, embedding_field, text_field, metadata_field], description="RAG documents")
                        self._collection = Collection(name=self._collection_name, schema=schema)
                        
                        # Create index
                        self._collection.create_index(field_name="embedding", index_params=index_params)
                        print(f"[INFO] Successfully recreated collection {self._collection_name} with index")
                    except Exception as recreate_e:
                        print(f"[ERROR] Failed to recreate collection: {recreate_e}")
                        raise

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> bool:
        """
        Add documents to the collection.
        """
        try:
            self._ensure_connected()
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            # Prepare data for insertion
            data = {
                "id": ids,
                "text": documents,
                "metadata": [str(meta) for meta in metadatas]  # Convert metadata to string for JSON storage
            }
            
            # Insert data
            self._collection.insert(data)
            self._collection.flush()
            
            print(f"[INFO] Successfully inserted {len(documents)} documents into Milvus")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to insert documents into Milvus: {e}")
            return False

    def insert_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]], ids: List[str]) -> bool:
        """
        Insert documents with embeddings into Milvus.
        This method is called by the ingestion service.
        """
        try:
            self._ensure_connected()
            if self._collection is None:
                raise RuntimeError("Milvus collection is not initialized.")
            
            # Prepare data for insertion
            texts = [doc.get("content", "") for doc in documents]
            metadatas = []
            for doc in documents:
                metadata = {
                    "source": doc.get("source", ""),
                    "filename": doc.get("filename", ""),
                    "file_type": doc.get("file_type", ""),
                    "chunk_id": doc.get("chunk_id", ""),
                    "timestamp": doc.get("timestamp", "")
                }
                metadatas.append(metadata)
            
            data = {
                "id": ids,
                "text": texts,
                "embedding": embeddings,
                "metadata": [str(meta) for meta in metadatas]
            }
            
            # Insert data
            self._collection.insert(data)
            self._collection.flush()
            
            print(f"[INFO] Successfully inserted {len(documents)} documents into Milvus")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to insert documents into Milvus: {e}")
            return False

    def query_documents(self, query_texts: List[str], n_results: int = 5, **kwargs) -> Any:
        self._ensure_connected()
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
