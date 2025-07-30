import time
from typing import List, Optional, Dict, Any
from ..entities.document import Document
from ..entities.query import Query
from ..entities.response import Response
from ..repositories.document_repository import DocumentRepository
from ...application.interfaces.llm_interface import LLMInterface
from ...application.interfaces.embedding_interface import EmbeddingInterface
from ...application.dto.chat_dto import ChatRequest, ChatResponse


class RAGService:
    """
    Core RAG (Retrieval-Augmented Generation) service implementing business logic.
    """
    
    def __init__(
        self,
        document_repository: DocumentRepository,
        llm_provider: LLMInterface,
        embedding_provider: EmbeddingInterface
    ):
        self.document_repository = document_repository
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider
    
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request using RAG pipeline.
        
        Args:
            request: The chat request containing query and parameters
            
        Returns:
            ChatResponse: The generated response with context
        """
        start_time = time.time()
        
        try:
            # 1. Create query entity
            query = Query(
                id="",  # Will be auto-generated
                text=request.query,
                metadata={
                    "provider": request.provider,
                    "source_filter": request.file_name,
                    "max_results": request.max_results
                }
            )
            
            # 2. Generate query embedding
            query_embedding = await self.embedding_provider.create_embedding(query.text)
            query.update_embedding(query_embedding)
            
            # 3. Retrieve relevant documents
            metadata_filter = None
            if request.file_name:
                metadata_filter = {"source": request.file_name}
            
            context_documents = await self.document_repository.search_similar_documents(
                query_embedding=query_embedding,
                n_results=request.max_results,
                metadata_filter=metadata_filter
            )
            
            # 4. Generate response using LLM
            context_text = self._build_context_text(context_documents)
            prompt = self._build_prompt(request.query, context_text)
            
            llm_response = await self.llm_provider.generate_response_with_metadata(prompt)
            
            # 5. Create response entity
            response = Response(
                id="",  # Will be auto-generated
                answer=llm_response.get("response", llm_response.get("answer", "")),
                query_id=query.id,
                context_documents=context_documents,
                metadata={
                    "provider": request.provider,
                    "processing_time": time.time() - start_time,
                    **llm_response.get("metadata", {})
                }
            )
            
            # 6. Convert to DTO format
            return ChatResponse(
                answer=response.answer,
                query_id=response.query_id,
                sources=response.sources,
                context_documents=[doc.to_dict() for doc in response.context_documents],
                metadata=response.metadata
            )
            
        except Exception as e:
            # Log error and return error response
            processing_time = time.time() - start_time
            return ChatResponse(
                answer=f"Sorry, I encountered an error: {str(e)}",
                query_id="",
                sources=[],
                context_documents=[],
                metadata={
                    "provider": request.provider,
                    "processing_time": processing_time,
                    "error": str(e)
                }
            )
    
    def _build_context_text(self, documents: List[Document]) -> str:
        """
        Build context text from retrieved documents.
        
        Args:
            documents: List of relevant documents
            
        Returns:
            str: Combined context text
        """
        if not documents:
            return ""
        
        context_parts = []
        for doc in documents:
            context_parts.append(f"Source: {doc.source or 'Unknown'}\nContent: {doc.content}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            query: The user's question
            context: The retrieved context
            
        Returns:
            str: Formatted prompt for the LLM
        """
        if context:
            return f"""Based on the following context, answer the question. If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

Question: {query}

Answer:"""
        else:
            return f"""Answer the following question. If you don't have enough information to provide a complete answer, say so.

Question: {query}

Answer:"""
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of documents to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate embeddings for documents
            texts = [doc.content for doc in documents]
            embeddings = await self.embedding_provider.create_embeddings(texts)
            
            # Update documents with embeddings
            for doc, embedding in zip(documents, embeddings):
                doc.update_embedding(embedding)
            
            # Store in repository
            return await self.document_repository.add_documents(documents)
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics and health information.
        
        Returns:
            Dict containing system stats
        """
        stats = {
            "llm_provider": {
                "name": self.llm_provider.provider_name,
                "model": self.llm_provider.model_name,
                "available": await self.llm_provider.is_available()
            },
            "embedding_provider": {
                "name": self.embedding_provider.provider_name,
                "model": self.embedding_provider.model_name,
                "dimension": self.embedding_provider.embedding_dimension,
                "available": await self.embedding_provider.is_available()
            }
        }
        
        try:
            collection_stats = await self.document_repository.get_collection_stats()
            stats["document_repository"] = collection_stats
        except Exception as e:
            stats["document_repository"] = {"error": str(e)}
        
        return stats 