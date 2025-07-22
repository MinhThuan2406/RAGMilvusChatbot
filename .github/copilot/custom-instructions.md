# GitHub Copilot Custom Instructions for RAGChatbot

## Project Context

- This repository is a modular, containerized Retrieval-Augmented Generation (RAG) chatbot system.
- It uses FastAPI for the backend, Milvus for vector storage, Ollama and OpenAI as LLM providers, and Streamlit/OpenWebUI for the frontend.
- All services are orchestrated with Docker Compose and support both local and cloud deployments.
- Codebase is Python 3.11+ (some containers use 3.13), with async/await patterns and type hints.

---

## Coding Standards

- **Use type hints** for all function signatures.
- **Prefer async functions** for I/O, API, and DB operations.
- **Add docstrings** to all public functions, classes, and endpoints.
- **Follow PEP8** for formatting and naming (snake_case for functions/variables, PascalCase for classes).
- **Use f-strings** for string interpolation.
- **Handle exceptions** gracefully and log errors with context.
- **Write modular, testable code** (single responsibility, clear separation of concerns).

---

## Project-Specific Guidelines

- **Backend API**: Use FastAPI routers, pydantic models, and async endpoints.
- **Vector DB**: Use Milvus via pymilvus client; do not assume a web UI exists.
- **LLM Providers**: Use adapters for Ollama and OpenAI; fallback to OpenAI for embeddings if Ollama is selected.
- **Environment Variables**: All config (API keys, hosts, ports) must be loaded from environment variables or `.env`.
- **Docker**: All new services or scripts should be containerizable and use environment variables for config.
- **Testing**: Use `pytest` for all tests. Mock external services in unit tests; use real services in integration tests.
- **CI/CD**: Ensure code passes linting (`flake8`), tests, and Docker builds (see `.github/workflows/ci.yml`).

---

## Examples

### Example: Async FastAPI Endpoint
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/chat/")
async def chat_with_bot(request: ChatRequest) -> ChatResponse:
    """
    Endpoint to interact with the chatbot.
    """
    # ...implementation...
```

### Example: Adapter with Type Hints and Docstring
```python
class OllamaAdapter(AbstractLLMClient, AbstractEmbeddingClient):
    """
    Adapter for interacting with the Ollama LLM and embedding API.
    """
    async def generate_response(self, prompt: str, context: str | None = None) -> str:
        """
        Generate a response from the LLM given a prompt and optional context.
        """
        # ...implementation...
```

### Example: Environment Variable Usage
```python
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```


## What to Avoid

- **Do not hardcode API keys, hosts, or ports**.
- **Do not use synchronous I/O for network or DB operations**.
- **Do not skip type hints or docstrings**.
- **Do not add UI code to backend modules**.

## References

- **service_links.txt**.
- **README.md** and **README.Docker.md** for project overview and Docker usage.
- **ci.yml** for CI/CD standards.