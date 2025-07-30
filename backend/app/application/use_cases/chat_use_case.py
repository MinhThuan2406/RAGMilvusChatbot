from typing import Optional
from ...domain.services.rag_service import RAGService
from ..dto.chat_dto import ChatRequest, ChatResponse, ChatRequestDTO, ChatResponseDTO


class ChatUseCase:
    """
    Use case for handling chat functionality.
    """
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
    
    async def execute(self, request_dto: ChatRequestDTO) -> ChatResponseDTO:
        """
        Execute the chat use case.
        
        Args:
            request_dto: The chat request DTO
            
        Returns:
            ChatResponseDTO: The chat response DTO
        """
        # Convert DTO to internal request
        request = ChatRequest(
            query=request_dto.query,
            provider=request_dto.provider or "ollama",
            file_name=request_dto.file_name,
            max_results=request_dto.max_results or 5
        )
        
        # Process the request
        response = await self.rag_service.process_chat_request(request)
        
        # Convert to DTO and return
        return response.to_dto()
    
    async def get_system_stats(self) -> dict:
        """
        Get system statistics.
        
        Returns:
            dict: System statistics
        """
        return await self.rag_service.get_system_stats() 