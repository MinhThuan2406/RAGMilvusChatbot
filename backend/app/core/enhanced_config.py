import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from enum import Enum


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LLMProvider(str, Enum):
    """LLM provider types."""
    OLLAMA = "ollama"
    OPENAI = "openai"


class EnhancedConfig(BaseSettings):
    """
    Enhanced configuration with environment-specific settings and validation.
    """
    
    # Environment
    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    
    # API Keys (secrets)
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    NGROK_AUTHTOKEN: Optional[str] = Field(
        default=None,
        description="Ngrok authentication token"
    )
    SECRETS_ENCRYPTION_KEY: Optional[str] = Field(
        default=None,
        description="Encryption key for secrets"
    )
    
    # Milvus Configuration
    MILVUS_HOST: str = Field(
        default="milvus-db",
        description="Milvus database host"
    )
    MILVUS_PORT: int = Field(
        default=19530,
        description="Milvus database port"
    )
    MILVUS_URI: Optional[str] = Field(
        default=None,
        description="Milvus URI for local mode"
    )
    
    # Ollama Configuration
    OLLAMA_HOST: str = Field(
        default="ollama-llm",
        description="Ollama service host"
    )
    OLLAMA_PORT: int = Field(
        default=11434,
        description="Ollama service port"
    )
    OLLAMA_API_BASE_URL: str = Field(
        default="http://ollama-llm:11434/api",
        description="Ollama API base URL"
    )
    
    # Service Ports
    RAG_API_PORT: int = Field(
        default=8001,
        description="RAG API service port"
    )
    CHATBOT_UI_PORT: int = Field(
        default=3000,
        description="Chatbot UI service port"
    )
    
    # LLM Configuration
    LLM_PROVIDER: LLMProvider = Field(
        default=LLMProvider.OLLAMA,
        description="Default LLM provider"
    )
    LLM_MODEL: str = Field(
        default="llama2",
        description="Default LLM model"
    )
    LLM_TIMEOUT: int = Field(
        default=60,
        description="LLM request timeout in seconds"
    )
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = Field(
        default="openai",
        description="Default embedding provider"
    )
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002",
        description="Default embedding model"
    )
    
    # CORS Configuration
    CORS_ALLOW_ORIGIN: str = Field(
        default="http://localhost:3000",
        description="CORS allowed origin"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="CORS allow credentials"
    )
    
    # Ngrok Configuration
    NGROK_REGION: str = Field(
        default="ap",
        description="Ngrok region"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="structured",
        description="Log format (structured or simple)"
    )
    LOG_FILE: Optional[str] = Field(
        default=None,
        description="Log file path"
    )
    
    # Resilience Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(
        default=5,
        description="Circuit breaker failure threshold"
    )
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: float = Field(
        default=60.0,
        description="Circuit breaker recovery timeout"
    )
    RETRY_MAX_ATTEMPTS: int = Field(
        default=3,
        description="Maximum retry attempts"
    )
    RETRY_BASE_DELAY: float = Field(
        default=1.0,
        description="Retry base delay"
    )
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = Field(
        default=10,
        description="Maximum concurrent requests"
    )
    REQUEST_TIMEOUT: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    # Security Configuration
    ENABLE_RATE_LIMITING: bool = Field(
        default=False,
        description="Enable rate limiting"
    )
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit requests per minute"
    )
    
    # Feature Flags
    ENABLE_CACHING: bool = Field(
        default=False,
        description="Enable response caching"
    )
    ENABLE_METRICS: bool = Field(
        default=False,
        description="Enable metrics collection"
    )
    ENABLE_TRACING: bool = Field(
        default=False,
        description="Enable distributed tracing"
    )
    
    # Python Path
    PYTHONPATH: str = Field(
        default="./backend",
        description="Python path"
    )
    
    @validator('ENVIRONMENT', pre=True)
    def validate_environment(cls, v):
        """Validate environment setting."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator('LLM_PROVIDER', pre=True)
    def validate_llm_provider(cls, v):
        """Validate LLM provider setting."""
        if isinstance(v, str):
            return LLMProvider(v.lower())
        return v
    
    @validator('OPENAI_API_KEY')
    def validate_openai_key(cls, v, values):
        """Validate OpenAI API key when OpenAI is the provider."""
        if values.get('LLM_PROVIDER') == LLMProvider.OPENAI and not v:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is openai")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == Environment.TESTING
    
    def get_milvus_connection_string(self) -> str:
        """Get Milvus connection string."""
        if self.MILVUS_URI:
            return self.MILVUS_URI
        return f"{self.MILVUS_HOST}:{self.MILVUS_PORT}"
    
    def get_ollama_url(self) -> str:
        """Get Ollama service URL."""
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins list."""
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGIN.split(",")]
    
    def get_secrets_dict(self) -> Dict[str, Any]:
        """Get dictionary of sensitive configuration values."""
        return {
            "OPENAI_API_KEY": self.OPENAI_API_KEY,
            "NGROK_AUTHTOKEN": self.NGROK_AUTHTOKEN
        }
    
    def get_public_config(self) -> Dict[str, Any]:
        """Get public configuration (without secrets)."""
        return {
            "environment": self.ENVIRONMENT.value,
            "llm_provider": self.LLM_PROVIDER.value,
            "llm_model": self.LLM_MODEL,
            "embedding_provider": self.EMBEDDING_PROVIDER,
            "embedding_model": self.EMBEDDING_MODEL,
            "milvus_host": self.MILVUS_HOST,
            "milvus_port": self.MILVUS_PORT,
            "ollama_host": self.OLLAMA_HOST,
            "ollama_port": self.OLLAMA_PORT,
            "rag_api_port": self.RAG_API_PORT,
            "chatbot_ui_port": self.CHATBOT_UI_PORT,
            "log_level": self.LOG_LEVEL,
            "enable_caching": self.ENABLE_CACHING,
            "enable_metrics": self.ENABLE_METRICS,
            "enable_tracing": self.ENABLE_TRACING,
            "enable_rate_limiting": self.ENABLE_RATE_LIMITING
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
config = EnhancedConfig() 