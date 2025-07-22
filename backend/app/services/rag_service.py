import os
from ..db.milvus_client import MilvusDBClient
from .llm_provider_factory import LLMFactory
from app.services.ingestion_service import AsyncEmbeddingFunction

class RAGService:
    def __init__(self, provider: str = '', milvus_host=None, milvus_port=None):
        self.llm_client = LLMFactory.get_llm_client(provider)
        if provider == "ollama":
            self.embedding_client = LLMFactory.get_embedding_client("openai")
            embedding_provider = "openai"
        else:
            self.embedding_client = LLMFactory.get_embedding_client(provider)
            embedding_provider = provider

        embedding_function = AsyncEmbeddingFunction(self.embedding_client, name=embedding_provider)
        if "PYTEST_CURRENT_TEST" not in os.environ:
            self.vector_db_client = MilvusDBClient(
                host=milvus_host,
                port=milvus_port,
                embedding_function=embedding_function
            )
        else:
            self.vector_db_client = None

    async def answer_query(self, query: str, file_name: str | None = None) -> str:
        # 1. Create embedding for the query (Ollama)
        print(f"[RETRIEVAL DEBUG] Query received: {query} (file_name: {file_name})")
        query_embedding = await self.embedding_client.create_embedding(query)
        print(f"[RETRIEVAL DEBUG] Query embedding: {query_embedding}")

        # 2. Retrieve relevant documents, filtered by file_name if provided
        filter_metadata = None
        if file_name:
            filter_metadata = {"source": file_name}

        if self.vector_db_client:
            # Try to filter by file_name if provided, else fallback
            # Only use filtering if the method supports it; otherwise, fallback
            import inspect
            sig = inspect.signature(self.vector_db_client.query_documents)
            filter_param = None
            for candidate in ["where", "filters", "metadata_filter"]:
                if candidate in sig.parameters:
                    filter_param = candidate
                    break
            if filter_metadata and filter_param:
                kwargs = {filter_param: filter_metadata}
                print(f"[RETRIEVAL DEBUG] Querying vector DB with filter: {kwargs}")
                retrieved_docs = self.vector_db_client.query_documents(query_texts=[query], n_results=3, **kwargs)
            else:
                print(f"[RETRIEVAL DEBUG] Querying vector DB without filter.")
                retrieved_docs = self.vector_db_client.query_documents(query_texts=[query], n_results=3)
        else:
            # Mocked response for test mode
            print(f"[RETRIEVAL DEBUG] Using mocked response for retrieval.")
            retrieved_docs = {"documents": [["This is a mocked document."]], "metadatas": [[{"source": "mocked.pdf", "page": 1}]], "ids": [["mocked_id"]]}

        context = ""
        documents = retrieved_docs.get('documents') if retrieved_docs else None
        print(f"[RETRIEVAL DEBUG] Retrieved documents: {documents}")
        if documents:
            context = "\n".join([doc for sublist in documents if sublist for doc in sublist])
            print(f"[RETRIEVAL DEBUG] Combined context for LLM: {context[:300]}... (truncated)")

        # 3. Augment prompt with context
        if context:
            prompt = f"Based on the following context, answer the question: {context}\n\nQuestion: {query}"
        else:
            prompt = f"No specific context found. Answer the question: {query}"
        print(f"[RETRIEVAL DEBUG] Final prompt to LLM: {prompt[:300]}... (truncated)")

        # 4. Generate response (Ollama)
        response = await self.llm_client.generate_response(prompt)
        return response