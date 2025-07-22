# RAGChatbot Developer Guide

This guide is for developers who want to set up, extend, or contribute.

---

## Project Structure

- `backend/` — FastAPI backend, adapters, core logic, database, and services
- `frontend/` — Web UI (if present)
- `data/raw_docs/` — Place for raw documents to be ingested
- `open-webui/` — Optional advanced web UI and related scripts
- `scripts/` — Utility scripts (e.g., data ingestion)

---

## Setup

- Python 3.10+, Docker, Node.js (for frontend)
- Backend:
  ```sh
  pip install -r requirements.txt
  uvicorn backend.app.main:app --reload --port 8001
  ```
- Frontend:
  ```sh
  cd frontend
  npm install
  npm run dev
  ```

---

## Docker

- Start all services:
  ```sh
  docker compose up --build
  ```

---

## API

- Main: `/api/`
- Chat: `/api/chat`
- Ingest: `/api/ingest/upload`
- See `backend/app/api/` for more endpoints.

---

## Tests

- Run:
  ```sh
  pytest backend/tests/
  ```

---

## Add Models or Adapters

- Add new adapters in `backend/app/adapters/`.
- Register them in the main app if needed.

---

## Environment Variables

- Configure via `.env` in the project root.
- See `README.Docker.md` for variable descriptions.

---

## Useful Scripts

- `scripts/ingest_initial_data.py` — Ingests all documents in `data/raw_docs/`.

---

## Contributing

- See `open-webui/docs/CONTRIBUTING.md` for contribution guidelines.

---

## Troubleshooting

- See `TROUBLESHOOTING.md` for common issues and solutions.
