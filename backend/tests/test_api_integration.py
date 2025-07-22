import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_endpoint_real_integration():
    """
    Integration test: This will hit the real ChromaDB and LLM endpoints.
    Make sure ChromaDB and LLM services are running and accessible.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/api/chat/", json={"query": "Integration test: What is this project about?"})
        print("Response status:", response.status_code)
        print("Response content:", response.text)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)
