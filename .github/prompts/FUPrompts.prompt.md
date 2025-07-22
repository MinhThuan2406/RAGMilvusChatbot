---
mode: edit
---

Define the task to achieve, including specific requirements, constraints, and success criteria.

---

**Task**:  
Describe the specific feature, bugfix, or improvement to be implemented in the RAGChatbot project. Reference relevant modules (e.g., `backend/app/services/ingestion_service.py`, `frontend/`, etc.).

**Requirements**:  
- List technical or architectural requirements (e.g., must use FastAPI, integrate with ChromaDB, follow adapter pattern).
- Specify any coding conventions or patterns to follow (see `DEVELOPER_GUIDE.md`).
- Note any workflow constraints (e.g., must work with Docker Compose, use `.env` config).

**Success Criteria**:  
- The implementation should pass all relevant tests (`pytest backend/tests/`).
- The new/modified feature should integrate cleanly with existing services and APIs.
- Code should be modular, documented, and follow project conventions.

**Dependencies**:  
- List any related files, services, or environment variables that must be considered or updated.

---

**Example**:

Task:  
Add support for ingesting `.md` (Markdown) files in the document ingestion pipeline.

Requirements:  
- Extend `DocumentProcessor` in `backend/app/services/ingestion_service.py` to detect and process `.md` files.
- Extract text content, chunk appropriately, and store embeddings in ChromaDB.
- Update tests in `backend/tests/` to cover Markdown ingestion.

Success Criteria:  
- Markdown files placed in `data/raw_docs/` are ingested and searchable via `/api/chat`.
- All tests pass.
- Code follows project conventions.

Dependencies:  
- `backend/app/services/ingestion_service.py`
- `backend/tests/`
- ChromaDB container

---

Use this template to define clear, actionable follow-up prompts for the RAGChatbot project.