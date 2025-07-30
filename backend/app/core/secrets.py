import os
import base64
import json
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .exceptions import ConfigurationException


class SecretsManager:
    """Secure secrets management with encryption."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize secrets manager.
        
        Args:
            encryption_key: Optional encryption key. If not provided, will use environment variable or generate one.
        """
        self.encryption_key = encryption_key or os.getenv("SECRETS_ENCRYPTION_KEY")
        # Look for .env.secrets in the backend directory
        self.secrets_file = Path(__file__).parent.parent.parent / ".env.secrets"
        self._fernet = None
        
        if self.encryption_key:
            self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with the provided key."""
        try:
            # Generate a key from the password
            salt = b'rag_chatbot_salt'  # In production, use a random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            self._fernet = Fernet(key)
        except Exception as e:
            raise ConfigurationException(
                f"Failed to initialize encryption: {str(e)}",
                config_key="SECRETS_ENCRYPTION_KEY"
            )
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret value."""
        if not self._fernet:
            return secret  # Return as-is if encryption is not enabled
        
        try:
            encrypted = self._fernet.encrypt(secret.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise ConfigurationException(
                f"Failed to encrypt secret: {str(e)}",
                config_key="encryption"
            )
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt a secret value."""
        if not self._fernet:
            return encrypted_secret  # Return as-is if encryption is not enabled
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_secret.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ConfigurationException(
                f"Failed to decrypt secret: {str(e)}",
                config_key="decryption"
            )
    
    def store_secrets(self, secrets: Dict[str, str], environment: str = "development"):
        """Store secrets securely."""
        secrets_data = {
            "environment": environment,
            "secrets": {}
        }
        
        for key, value in secrets.items():
            encrypted_value = self.encrypt_secret(value)
            secrets_data["secrets"][key] = encrypted_value
        
        # Store in file
        with open(self.secrets_file, 'w') as f:
            json.dump(secrets_data, f, indent=2)
        
        print(f"Stored {len(secrets)} secrets for {environment} environment")
    
    def load_secrets(self, environment: str = "development") -> Dict[str, str]:
        """Load secrets for the specified environment."""
        if not self.secrets_file.exists():
            return {}
        
        try:
            with open(self.secrets_file, 'r') as f:
                data = json.load(f)
            
            if data.get("environment") != environment:
                print(f"Warning: Secrets file is for {data.get('environment')} environment, but loading for {environment}")
            
            secrets = {}
            for key, encrypted_value in data.get("secrets", {}).items():
                decrypted_value = self.decrypt_secret(encrypted_value)
                secrets[key] = decrypted_value
            
            return secrets
        except Exception as e:
            raise ConfigurationException(
                f"Failed to load secrets: {str(e)}",
                config_key="secrets_file"
            )
    
    def get_secret(self, key: str, environment: str = "development") -> Optional[str]:
        """Get a specific secret."""
        secrets = self.load_secrets(environment)
        return secrets.get(key)
    
    def set_secret(self, key: str, value: str, environment: str = "development"):
        """Set a specific secret."""
        secrets = self.load_secrets(environment)
        secrets[key] = value
        self.store_secrets(secrets, environment)
    
    def list_secrets(self, environment: str = "development") -> Dict[str, str]:
        """List all secrets (keys only, not values)."""
        secrets = self.load_secrets(environment)
        return {key: "[ENCRYPTED]" for key in secrets.keys()}
    
    def remove_secret(self, key: str, environment: str = "development"):
        """Remove a specific secret."""
        secrets = self.load_secrets(environment)
        if key in secrets:
            del secrets[key]
            self.store_secrets(secrets, environment)
            print(f"Removed secret: {key}")
        else:
            print(f"Secret not found: {key}")
    
    def validate_secrets(self, required_secrets: list, environment: str = "development") -> bool:
        """Validate that all required secrets are present."""
        secrets = self.load_secrets(environment)
        missing_secrets = []
        
        for secret in required_secrets:
            if secret not in secrets or not secrets[secret]:
                missing_secrets.append(secret)
        
        if missing_secrets:
            print(f"Missing required secrets for {environment}: {missing_secrets}")
            return False
        
        return True


class EnvironmentSecretsManager:
    """Environment-specific secrets management."""
    
    def __init__(self):
        self.managers = {}
        self._initialize_managers()
    
    def _initialize_managers(self):
        """Initialize secrets managers for different environments."""
        environments = ["development", "staging", "production", "testing"]
        fallback_key = os.getenv("SECRETS_ENCRYPTION_KEY")
        for env in environments:
            env_key = os.getenv(f"SECRETS_ENCRYPTION_KEY_{env.upper()}") or fallback_key
            self.managers[env] = SecretsManager(env_key)
    
    def get_manager(self, environment: str = "development") -> SecretsManager:
        """Get secrets manager for specific environment."""
        return self.managers.get(environment, self.managers["development"])
    
    def setup_development_secrets(self):
        """Setup development environment secrets."""
        dev_manager = self.get_manager("development")
        
        # Example secrets for development
        secrets = {
            "OPENAI_API_KEY": "your-openai-api-key-here",
            "NGROK_AUTHTOKEN": "your-ngrok-token-here",
            "DATABASE_PASSWORD": "dev-password",
            "REDIS_PASSWORD": "dev-redis-password"
        }
        
        dev_manager.store_secrets(secrets, "development")
        print("Development secrets setup complete")
    
    def setup_production_secrets(self):
        """Setup production environment secrets."""
        prod_manager = self.get_manager("production")
        
        # Production secrets should be set via environment variables or secure input
        print("Production secrets should be set via secure methods")
        print("Use set_secret() method to add secrets individually")
    
    def validate_environment_secrets(self, environment: str = "development"):
        """Validate secrets for specific environment."""
        manager = self.get_manager(environment)
        
        required_secrets = {
            "development": ["OPENAI_API_KEY"],
            "staging": ["OPENAI_API_KEY", "DATABASE_PASSWORD"],
            "production": ["OPENAI_API_KEY", "DATABASE_PASSWORD", "REDIS_PASSWORD"],
            "testing": ["OPENAI_API_KEY"]
        }
        
        required = required_secrets.get(environment, [])
        return manager.validate_secrets(required, environment)


# Global secrets manager instance
secrets_manager = EnvironmentSecretsManager()


def get_secret(key: str, environment: str = "development") -> Optional[str]:
    """Get a secret for the specified environment."""
    return secrets_manager.get_manager(environment).get_secret(key, environment)


def set_secret(key: str, value: str, environment: str = "development"):
    """Set a secret for the specified environment."""
    secrets_manager.get_manager(environment).set_secret(key, value, environment)


def validate_secrets(environment: str = "development") -> bool:
    """Validate secrets for the specified environment."""
    return secrets_manager.validate_environment_secrets(environment) 