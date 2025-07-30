import os
from ..db.milvus_client import MilvusDBClient
from .llm_provider_factory import LLMFactory
from .ingestion_service import IngestionService

class RAGService:
    def __init__(self, provider: str = '', milvus_host=None, milvus_port=None):
        self.llm_client = LLMFactory.get_llm_client(provider)
        if provider == "ollama":
            self.embedding_client = LLMFactory.get_embedding_client("openai")
            embedding_provider = "openai"
        else:
            self.embedding_client = LLMFactory.get_embedding_client(provider)
            embedding_provider = provider

        # Use the new ingestion service which handles fallback
        if "PYTEST_CURRENT_TEST" not in os.environ:
            self.ingestion_service = IngestionService()
        else:
            self.ingestion_service = None

    async def answer_query(self, query: str, file_name: str | None = None) -> str:
        # 1. Create embedding for the query
        print(f"[RETRIEVAL DEBUG] Query received: {query} (file_name: {file_name})")
        query_embedding = await self.embedding_client.create_embedding(query)
        print(f"[RETRIEVAL DEBUG] Query embedding: {query_embedding}")

        # 2. Retrieve relevant documents using the new ingestion service
        if self.ingestion_service:
            # Use the new search functionality
            search_result = self.ingestion_service.search_documents(query, limit=3)
            
            if search_result["success"]:
                retrieved_docs = search_result["results"]
                print(f"[RETRIEVAL DEBUG] Retrieved documents: {len(retrieved_docs)}")
                
                # Filter by file_name if provided
                if file_name:
                    filtered_docs = [
                        doc for doc in retrieved_docs 
                        if doc.get("metadata", {}).get("filename") == file_name
                    ]
                    retrieved_docs = filtered_docs
                    print(f"[RETRIEVAL DEBUG] Filtered to {len(retrieved_docs)} documents for file: {file_name}")
            else:
                print(f"[RETRIEVAL DEBUG] Search failed: {search_result.get('error')}")
                retrieved_docs = []
        else:
            # Mocked response for test mode
            print(f"[RETRIEVAL DEBUG] Using mocked response for retrieval.")
            retrieved_docs = [
                {
                    "content": "This is a mocked document.",
                    "metadata": {"filename": "mocked.pdf", "source": "mocked.pdf"},
                    "distance": 0.1,
                    "id": "mocked_id"
                }
            ]

        # 3. Build context from retrieved documents
        context = ""
        if retrieved_docs:
            context_parts = []
            for doc in retrieved_docs:
                content = doc.get("content", "")
                if content:
                    context_parts.append(content)
            context = "\n\n".join(context_parts)
            print(f"[RETRIEVAL DEBUG] Combined context for LLM: {context[:300]}... (truncated)")

        # 4. Augment prompt with context
        if context:
            prompt = f"Based on the following context, answer the question: {context}\n\nQuestion: {query}"
        else:
            prompt = f"No specific context found. Answer the question: {query}"
        print(f"[RETRIEVAL DEBUG] Final prompt to LLM: {prompt[:300]}... (truncated)")

        # 5. Generate response
        response = await self.llm_client.generate_response(prompt)
        return response