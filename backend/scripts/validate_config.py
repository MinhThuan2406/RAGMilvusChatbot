#!/usr/bin/env python3
"""
Configuration validation script for RAG Chatbot.
Validates environment setup, secrets, and configuration.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.enhanced_config import config, Environment, LLMProvider
from app.core.secrets import validate_secrets, get_secret
# from app.core.environment import env_config  # Commented out for now


def validate_environment_config():
    """Validate environment configuration."""
    print("🔍 Validating Environment Configuration...")
    
    # Check environment setting
    print(f"  Environment: {config.ENVIRONMENT.value}")
    
    # Check LLM provider
    print(f"  LLM Provider: {config.LLM_PROVIDER.value}")
    print(f"  LLM Model: {config.LLM_MODEL}")
    
    # Check embedding provider
    print(f"  Embedding Provider: {config.EMBEDDING_PROVIDER}")
    print(f"  Embedding Model: {config.EMBEDDING_MODEL}")
    
    # Check service configurations
    print(f"  Milvus Host: {config.MILVUS_HOST}")
    print(f"  Milvus Port: {config.MILVUS_PORT}")
    print(f"  Ollama Host: {config.OLLAMA_HOST}")
    print(f"  Ollama Port: {config.OLLAMA_PORT}")
    
    # Check feature flags
    print(f"  Enable Metrics: {config.ENABLE_METRICS}")
    print(f"  Enable Tracing: {config.ENABLE_TRACING}")
    print(f"  Enable Caching: {config.ENABLE_CACHING}")
    print(f"  Enable Rate Limiting: {config.ENABLE_RATE_LIMITING}")
    
    # Check resilience settings
    print(f"  Circuit Breaker Failure Threshold: {config.CIRCUIT_BREAKER_FAILURE_THRESHOLD}")
    print(f"  Circuit Breaker Recovery Timeout: {config.CIRCUIT_BREAKER_RECOVERY_TIMEOUT}")
    print(f"  Retry Max Attempts: {config.RETRY_MAX_ATTEMPTS}")
    print(f"  Request Timeout: {config.REQUEST_TIMEOUT}")
    
    return True


def validate_secrets_config():
    """Validate secrets configuration."""
    print("\n🔐 Validating Secrets Configuration...")
    
    environment = config.ENVIRONMENT.value
    
    # Check if secrets validation passes
    if validate_secrets(environment):
        print(f"  ✅ Secrets validation passed for {environment} environment")
        
        # List available secrets
        from app.core.secrets import secrets_manager
        manager = secrets_manager.get_manager(environment)
        secrets = manager.list_secrets(environment)
        
        if secrets:
            print(f"  📋 Available secrets: {list(secrets.keys())}")
        else:
            print("  ⚠️  No secrets found")
        
        return True
    else:
        print(f"  ❌ Secrets validation failed for {environment} environment")
        return False


def validate_api_keys():
    """Validate API keys are properly configured."""
    print("\n🔑 Validating API Keys...")
    
    environment = config.ENVIRONMENT.value
    
    # Check OpenAI API key
    openai_key = get_secret("OPENAI_API_KEY", environment)
    if openai_key and openai_key != "your-openai-api-key-here":
        print("  ✅ OpenAI API key is configured")
    else:
        print("  ⚠️  OpenAI API key not configured or using placeholder")
    
    # Check Ngrok token
    ngrok_token = get_secret("NGROK_AUTHTOKEN", environment)
    if ngrok_token and ngrok_token != "your-ngrok-token-here":
        print("  ✅ Ngrok authentication token is configured")
    else:
        print("  ⚠️  Ngrok authentication token not configured or using placeholder")
    
    return True


def validate_service_connectivity():
    """Validate service connectivity."""
    print("\n🌐 Validating Service Connectivity...")
    
    import httpx
    import asyncio
    
    async def check_service(url: str, name: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"  ✅ {name} is accessible")
                    return True
                else:
                    print(f"  ⚠️  {name} returned status {response.status_code}")
                    return False
        except Exception as e:
            print(f"  ❌ {name} is not accessible: {str(e)}")
            return False
    
    # Check Ollama service
    ollama_url = config.get_ollama_url()
    try:
        result = asyncio.run(check_service(f"{ollama_url}/api/tags", "Ollama"))
    except Exception as e:
        print(f"  ❌ Ollama service check failed: {str(e)}")
    
    return True


def validate_file_structure():
    """Validate required file structure."""
    print("\n📁 Validating File Structure...")
    
    required_dirs = [
        "data/raw_docs",
        "data/store_docs",
        "backend/app",
        "backend/tests"
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path} exists")
        else:
            print(f"  ❌ {dir_path} missing")
    
    required_files = [
        ".env",
        "compose.yml",
        "requirements.txt",
        "backend/app/main.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path} exists")
        else:
            print(f"  ❌ {file_path} missing")
    
    return True


def generate_config_report():
    """Generate a comprehensive configuration report."""
    print("\n📊 Configuration Report")
    print("=" * 50)
    
    # Environment info
    print(f"Environment: {config.ENVIRONMENT.value}")
    print(f"LLM Provider: {config.LLM_PROVIDER.value}")
    print(f"Embedding Provider: {config.EMBEDDING_PROVIDER}")
    
    # Public configuration
    public_config = config.get_public_config()
    print("\nPublic Configuration:")
    for key, value in public_config.items():
        print(f"  {key}: {value}")
    
    # Secrets info (keys only)
    environment = config.ENVIRONMENT.value
    from app.core.secrets import secrets_manager
    manager = secrets_manager.get_manager(environment)
    secrets = manager.list_secrets(environment)
    
    if secrets:
        print(f"\nConfigured Secrets ({len(secrets)}):")
        for secret_name in secrets.keys():
            print(f"  - {secret_name}")
    else:
        print("\nNo secrets configured")
    
    print("\n" + "=" * 50)


def main():
    """Main validation function."""
    print("🚀 RAG Chatbot Configuration Validation")
    print("=" * 50)
    
    try:
        # Run all validations
        validate_environment_config()
        validate_secrets_config()
        validate_api_keys()
        validate_service_connectivity()
        validate_file_structure()
        
        # Generate report
        generate_config_report()
        
        print("\n✅ Configuration validation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 