from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ...application.use_cases.chat_use_case import ChatUseCase
from ...application.dto.chat_dto import ChatRequestDTO, ChatResponseDTO


class ChatController:
    """
    Controller for handling chat-related HTTP requests.
    """
    
    def __init__(self, chat_use_case: ChatUseCase):
        self.chat_use_case = chat_use_case
    
    async def chat(self, request: ChatRequestDTO) -> ChatResponseDTO:
        """
        Handle chat request.
        
        Args:
            request: The chat request DTO
            
        Returns:
            ChatResponseDTO: The chat response DTO
        """
        try:
            return await self.chat_use_case.execute(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dict containing system statistics
        """
        try:
            return await self.chat_use_case.get_system_stats()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")


# Factory function for dependency injection
def create_chat_controller(chat_use_case: ChatUseCase) -> ChatController:
    """Create a chat controller instance."""
    return ChatController(chat_use_case) 