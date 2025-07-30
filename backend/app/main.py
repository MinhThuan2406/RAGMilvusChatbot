
from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import time
from contextlib import asynccontextmanager
from .core.config import settings
from .core.container import container
from .core.logging import setup_logging
from .core.metrics import metrics_collector, system_metrics_collector
from .core.tracing import tracing_manager
from .core.alerting import alert_manager
from .presentation.controllers.chat_controller import ChatController
from .presentation.middleware.error_handler import ErrorHandlerMiddleware, RequestLoggingMiddleware
from .application.dto.chat_dto import ChatRequestDTO, ChatResponseDTO

# Setup logging
setup_logging(level="INFO", format_type="structured")

if "PYTEST_CURRENT_TEST" not in os.environ:
    from .services.file_cleanup import delete_old_files_task

@asynccontextmanager
async def lifespan(app):
    if "PYTEST_CURRENT_TEST" not in os.environ:
        from threading import Thread
        import time
        def run_cleanup():
            while True:
                delete_old_files_task("/app/data/raw_docs", max_age_hours=24)
                time.sleep(3600)  
        Thread(target=run_cleanup, daemon=True).start()
        
        # Start monitoring components
        system_metrics_collector.start()
        tracing_manager.instrument_fastapi(app)
        
        # Start alert checking in background
        async def check_alerts_periodically():
            while True:
                try:
                    await alert_manager.check_rules()
                except Exception as e:
                    print(f"Error checking alerts: {e}")
                await asyncio.sleep(60)  # Check every minute
        
        import asyncio
        asyncio.create_task(check_alerts_periodically())
    
    yield
    
    # Cleanup
    if "PYTEST_CURRENT_TEST" not in os.environ:
        system_metrics_collector.stop()
        tracing_manager.shutdown()

app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for Retrieval-Augmented Generation Chatbot",
    version="0.1.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGIN", "http://localhost:3000").split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
)


def get_chat_controller(provider: str = "ollama") -> ChatController:
    """Dependency to get chat controller."""
    return container.get_chat_controller(provider)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the RAG Chatbot API!"}


@app.post("/api/chat/", response_model=ChatResponseDTO)
async def chat_with_bot(
    request: ChatRequestDTO,
    chat_controller: ChatController = Depends(get_chat_controller)
) -> ChatResponseDTO:
    """
    Endpoint to interact with the chatbot.
    """
    return await chat_controller.chat(request)


@app.get("/api/stats/")
async def get_system_stats(
    chat_controller: ChatController = Depends(get_chat_controller)
):
    """
    Get system statistics and health information.
    """
    return await chat_controller.get_system_stats()


@app.get("/api/health/")
async def health_check():
    """
    Health check endpoint.
    """
    from .core.circuit_breaker import circuit_breaker_manager
    
    # Get circuit breaker status
    circuit_breakers = await circuit_breaker_manager.get_all_status()
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "circuit_breakers": circuit_breakers
    }


@app.get("/api/circuit-breakers/")
async def get_circuit_breaker_status():
    """
    Get circuit breaker status for all services.
    """
    from .core.circuit_breaker import circuit_breaker_manager
    
    return await circuit_breaker_manager.get_all_status()


# Keep the old API endpoints for backward compatibility
if "PYTEST_CURRENT_TEST" not in os.environ:
    from .api import chat, ingest
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingest"])
    
    # Add monitoring endpoints
    from .presentation.api.monitoring import router as monitoring_router
    app.include_router(monitoring_router)
