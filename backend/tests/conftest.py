import pytest 
import sys
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True)
def mock_chromadb(monkeypatch):
    if not any("integration" in arg for arg in sys.argv):
        monkeypatch.setattr(
            "app.db.chroma_client.ChromaDBClient.add_documents",
            MagicMock()
        )
        monkeypatch.setattr(
            "app.db.chroma_client.ChromaDBClient.query_documents",
            MagicMock(return_value={
                "documents": [["This is a mocked document."]],
                "metadatas": [[{"source": "mocked.pdf", "page": 1}]],
                "ids": [["mocked_id"]]
            })
        )
    yield