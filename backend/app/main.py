
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from .core.config import settings

if "PYTEST_CURRENT_TEST" not in os.environ:
    from .api import chat, ingest
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
    yield

app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for Retrieval-Augmented Generation Chatbot",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"], # Avoid using "*" in production for security reasons
    allow_origins=[
        "http://localhost:3000",  # local dev
        "https://your-production-domain.com"  # production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if "PYTEST_CURRENT_TEST" not in os.environ:
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingest"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the RAG Chatbot API!"}

# Example of how to use settings
