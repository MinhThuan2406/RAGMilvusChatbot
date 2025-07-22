# Copilot Instructions for RAGChatbot

## Project Overview
- **RAGChatbot** is a modular, containerized Retrieval-Augmented Generation (RAG) chatbot stack.
- **Major components:**
  - `backend/app/`: FastAPI backend (API, ingestion, adapters, core logic, DB, services)
  - `frontend/`: Streamlit or Open WebUI frontend (user chat interface)
  - `data/raw_docs/`: Directory for user-uploaded documents to be ingested
  - `scripts/`: Utility scripts (e.g., `ingest_initial_data.py` for bulk ingestion)
  - **Vector DB:** ChromaDB (stores embeddings)
  - **LLM Provider:** Ollama (local LLM inference)
  - **Orchestration:** Docker Compose

## Key Workflows
- **Start all services:**
  - `docker compose up --build`
- **Run backend locally:**
  - `pip install -r requirements.txt`
  - `uvicorn backend.app.main:app --reload --port 8001`
- **Run tests:**
  - `pytest backend/tests/`
- **Bulk ingest documents:**
  - Place files in `data/raw_docs/`
  - Run `python scripts/ingest_initial_data.py`
- **Environment config:**
  - All main config via `.env` in project root (see `README.Docker.md` for details)

## Patterns & Conventions
- **API endpoints:**
  - `/api/chat` (chat), `/api/ingest/upload` (document upload)
  - See `backend/app/api/` for endpoint implementations
- **Adapters:**
  - Add new LLM/vector DB adapters in `backend/app/adapters/`
  - Register new adapters in the main app if needed
- **Ingestion:**
  - Ingestion logic in `backend/app/services/ingestion_service.py` (handles file type detection, text extraction, chunking, embedding, and DB storage)
- **File cleanup:**
  - Background task in `backend/app/services/file_cleanup.py` deletes old files from `data/raw_docs/`
- **Testing:**
  - Tests in `backend/tests/` use pytest

## Integration & External Dependencies
- **ChromaDB** (vector DB): runs as a container, see `compose.yml`
- **Ollama** (LLM): runs as a container, see `compose.yml`
- **OpenAI API key** required for embeddings (set in `.env`)
- **Ngrok**: for remote access, see `README.Docker.md`

## Troubleshooting
- See `TROUBLESHOOTING.md` for common issues (CORS, ports, Ngrok, etc.)
- Logs: `docker compose logs -f`

## Examples
- To add a new document type, extend `DocumentProcessor` in `ingestion_service.py`
- To add a new LLM, implement an adapter in `adapters/` and update the provider factory

---
For more, see `README.md`, `DEVELOPER_GUIDE.md`, and `README.Docker.md`.
