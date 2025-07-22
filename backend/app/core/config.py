import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    CHROMA_HOST: str = "vector-db"
    CHROMA_PORT: int = 8000
    OLLAMA_HOST: str = "ollama-llm"
    OLLAMA_PORT: int = 11434

settings = Settings()