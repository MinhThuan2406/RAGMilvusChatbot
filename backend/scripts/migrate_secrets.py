#!/usr/bin/env python3
"""
Migration script to securely move secrets from .env to the new secrets management system.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.secrets import set_secret, secrets_manager


def load_current_env():
    """Load current environment variables from .env file."""
    # Check in current directory first
    env_file = Path(".env")
    if not env_file.exists():
        # Check in parent directory (root of project)
        env_file = Path("..") / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        return True
    return False


def extract_secrets_from_env():
    """Extract secrets from current environment variables."""
    secrets = {}
    
    # API Keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your-openai-api-key-here":
        secrets["OPENAI_API_KEY"] = openai_key
    
    ngrok_token = os.getenv("NGROK_AUTHTOKEN")
    if ngrok_token and ngrok_token != "your-ngrok-token-here":
        secrets["NGROK_AUTHTOKEN"] = ngrok_token
    
    # Database passwords (if any)
    db_password = os.getenv("DATABASE_PASSWORD")
    if db_password:
        secrets["DATABASE_PASSWORD"] = db_password
    
    redis_password = os.getenv("REDIS_PASSWORD")
    if redis_password:
        secrets["REDIS_PASSWORD"] = redis_password
    
    return secrets


def migrate_secrets_to_secure_storage():
    """Migrate secrets from .env to secure storage."""
    print("🔐 Migrating secrets to secure storage...")
    
    # Load current environment
    if not load_current_env():
        print("❌ No .env file found")
        return False
    
    # Extract secrets
    secrets = extract_secrets_from_env()
    
    if not secrets:
        print("⚠️  No secrets found in .env file")
        return True
    
    print(f"📋 Found {len(secrets)} secrets to migrate:")
    for key in secrets.keys():
        print(f"  - {key}")
    
    # Confirm migration
    response = input("\nDo you want to migrate these secrets to secure storage? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled")
        return False
    
    # Migrate secrets
    environment = os.getenv("ENVIRONMENT", "development")
    
    for key, value in secrets.items():
        set_secret(key, value, environment)
        print(f"  ✅ Migrated {key}")
    
    print(f"\n✅ Successfully migrated {len(secrets)} secrets to {environment} environment")
    return True


def create_secure_env_template():
    """Create a secure .env template without sensitive data."""
    print("\n📝 Creating secure .env template...")
    
    template_content = """# RAG Chatbot Environment Configuration
# This file contains non-sensitive configuration
# Sensitive data is stored in secure secrets management

# Environment (development, staging, production, testing)
ENVIRONMENT=development

# Milvus Configuration
MILVUS_HOST=milvus-db
MILVUS_PORT=19530
MILVUS_URI=

# Ollama Configuration
OLLAMA_HOST=ollama-llm
OLLAMA_PORT=11434
OLLAMA_API_BASE_URL=http://ollama-llm:11434/api

# Service Ports
RAG_API_PORT=8001
CHATBOT_UI_PORT=3000

# LLM Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama2
LLM_TIMEOUT=60

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-ada-002

# CORS Configuration
CORS_ALLOW_ORIGIN=http://localhost:3000
CORS_ALLOW_CREDENTIALS=true

# Ngrok Configuration
NGROK_REGION=ap

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=structured
LOG_FILE=

# Resilience Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60.0
RETRY_MAX_ATTEMPTS=3
RETRY_BASE_DELAY=1.0

# Performance Configuration
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30

# Security Configuration
ENABLE_RATE_LIMITING=false
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Feature Flags
ENABLE_CACHING=false
ENABLE_METRICS=false
ENABLE_TRACING=false

# Python Path
PYTHONPATH=./backend

# NOTE: API keys and other secrets are now managed through the secrets system
# Use the secrets management API to set/get sensitive data
"""
    
    # Create backup of current .env (check both locations)
    current_env = Path(".env")
    if not current_env.exists():
        current_env = Path("..") / ".env"
    
    if current_env.exists():
        backup_path = current_env.parent / ".env.backup"
        current_env.rename(backup_path)
        print(f"  📦 Created backup: {backup_path}")
    
    # Create new secure .env in root directory
    new_env_path = Path("..") / ".env"
    with open(new_env_path, "w") as f:
        f.write(template_content)
    
    print("  ✅ Created secure .env template")
    return True


def setup_encryption_key():
    """Setup encryption key for secrets."""
    print("\n🔑 Setting up encryption key...")
    
    # Check if encryption key already exists
    encryption_key = os.getenv("SECRETS_ENCRYPTION_KEY")
    if encryption_key:
        print("  ✅ Encryption key already configured")
        return True
    
    # Generate encryption key
    import secrets
    new_key = secrets.token_urlsafe(32)
    
    print(f"  🔐 Generated new encryption key")
    print(f"  📝 Add this to your .env file:")
    print(f"     SECRETS_ENCRYPTION_KEY={new_key}")
    
    # Ask if user wants to add it automatically
    response = input("\nDo you want to add the encryption key to .env? (y/N): ")
    if response.lower() == 'y':
        with open(".env", "a") as f:
            f.write(f"\n# Secrets Encryption Key\nSECRETS_ENCRYPTION_KEY={new_key}\n")
        print("  ✅ Added encryption key to .env")
        return True
    
    return False


def main():
    """Main migration function."""
    print("🚀 RAG Chatbot Secrets Migration")
    print("=" * 50)
    
    try:
        # Setup encryption key
        setup_encryption_key()
        
        # Migrate secrets
        if migrate_secrets_to_secure_storage():
            # Create secure template
            create_secure_env_template()
            
            print("\n✅ Migration completed successfully!")
            print("\n📋 Next steps:")
            print("  1. Restart your application to use the new configuration")
            print("  2. Use the secrets management API to manage sensitive data")
            print("  3. Run the validation script to verify setup")
            print("  4. Consider removing the .env.backup file after verification")
            
        else:
            print("\n❌ Migration failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 