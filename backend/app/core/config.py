import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "milvus-db")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", 19530))
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "ollama-llm")
    OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", 11434))

settings = Settings()