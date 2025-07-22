from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from typing import Any
if "PYTEST_CURRENT_TEST" not in os.environ:
    from ..services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService() 

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str
    provider: str | None = None  
    file_name: str | None = None  

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str

@router.post("/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest) -> ChatResponse:
    """
    Endpoint to interact with the chatbot.
    """
    import traceback
    try:
        provider = request.provider if request.provider is not None else "ollama"
        rag_service = RAGService(provider=provider)
        if not hasattr(rag_service, "answer_query") or not callable(getattr(rag_service, "answer_query", None)):
            raise HTTPException(status_code=500, detail="RAGService does not have an 'answer_query' method.")
        response: str = await rag_service.answer_query(request.query, file_name=request.file_name)
        return ChatResponse(answer=response)
    except Exception as e:
        print("Exception in chat_with_bot:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{e}\n{traceback.format_exc()}")