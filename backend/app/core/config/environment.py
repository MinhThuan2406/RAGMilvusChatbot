import os
from typing import Dict, Any
from pathlib import Path


class EnvironmentConfig:
    """Environment-specific configuration management."""
    
    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.config_dir = Path(__file__).parent / "environments"
    
    def load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        config_file = self.config_dir / f"{self.environment}.env"
        
        if config_file.exists():
            return self._load_env_file(config_file)
        else:
            return self._get_default_config()
    
    def _load_env_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from .env file."""
        config = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for environment."""
        defaults = {
            "development": {
                "LOG_LEVEL": "DEBUG",
                "LOG_FORMAT": "structured",
                "ENABLE_METRICS": "false",
                "ENABLE_TRACING": "false",
                "ENABLE_CACHING": "false",
                "ENABLE_RATE_LIMITING": "false",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "3",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "30.0",
                "RETRY_MAX_ATTEMPTS": "2",
                "REQUEST_TIMEOUT": "30"
            },
            "staging": {
                "LOG_LEVEL": "INFO",
                "LOG_FORMAT": "structured",
                "ENABLE_METRICS": "true",
                "ENABLE_TRACING": "true",
                "ENABLE_CACHING": "true",
                "ENABLE_RATE_LIMITING": "true",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "5",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "60.0",
                "RETRY_MAX_ATTEMPTS": "3",
                "REQUEST_TIMEOUT": "60"
            },
            "production": {
                "LOG_LEVEL": "WARNING",
                "LOG_FORMAT": "structured",
                "ENABLE_METRICS": "true",
                "ENABLE_TRACING": "true",
                "ENABLE_CACHING": "true",
                "ENABLE_RATE_LIMITING": "true",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "5",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "120.0",
                "RETRY_MAX_ATTEMPTS": "3",
                "REQUEST_TIMEOUT": "90"
            },
            "testing": {
                "LOG_LEVEL": "DEBUG",
                "LOG_FORMAT": "simple",
                "ENABLE_METRICS": "false",
                "ENABLE_TRACING": "false",
                "ENABLE_CACHING": "false",
                "ENABLE_RATE_LIMITING": "false",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "1",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "5.0",
                "RETRY_MAX_ATTEMPTS": "1",
                "REQUEST_TIMEOUT": "10"
            }
        }
        
        return defaults.get(self.environment, defaults["development"])
    
    def create_environment_files(self):
        """Create environment-specific .env files."""
        self.config_dir.mkdir(exist_ok=True)
        
        environments = {
            "development": {
                "ENVIRONMENT": "development",
                "LOG_LEVEL": "DEBUG",
                "ENABLE_METRICS": "false",
                "ENABLE_TRACING": "false",
                "ENABLE_CACHING": "false",
                "ENABLE_RATE_LIMITING": "false",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "3",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "30.0",
                "RETRY_MAX_ATTEMPTS": "2",
                "REQUEST_TIMEOUT": "30"
            },
            "staging": {
                "ENVIRONMENT": "staging",
                "LOG_LEVEL": "INFO",
                "ENABLE_METRICS": "true",
                "ENABLE_TRACING": "true",
                "ENABLE_CACHING": "true",
                "ENABLE_RATE_LIMITING": "true",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "5",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "60.0",
                "RETRY_MAX_ATTEMPTS": "3",
                "REQUEST_TIMEOUT": "60"
            },
            "production": {
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "WARNING",
                "ENABLE_METRICS": "true",
                "ENABLE_TRACING": "true",
                "ENABLE_CACHING": "true",
                "ENABLE_RATE_LIMITING": "true",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "5",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "120.0",
                "RETRY_MAX_ATTEMPTS": "3",
                "REQUEST_TIMEOUT": "90"
            },
            "testing": {
                "ENVIRONMENT": "testing",
                "LOG_LEVEL": "DEBUG",
                "ENABLE_METRICS": "false",
                "ENABLE_TRACING": "false",
                "ENABLE_CACHING": "false",
                "ENABLE_RATE_LIMITING": "false",
                "CIRCUIT_BREAKER_FAILURE_THRESHOLD": "1",
                "CIRCUIT_BREAKER_RECOVERY_TIMEOUT": "5.0",
                "RETRY_MAX_ATTEMPTS": "1",
                "REQUEST_TIMEOUT": "10"
            }
        }
        
        for env_name, config in environments.items():
            file_path = self.config_dir / f"{env_name}.env"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {env_name.upper()} Environment Configuration\n")
                f.write(f"# Generated automatically - DO NOT EDIT MANUALLY\n\n")
                
                for key, value in config.items():
                    f.write(f"{key}={value}\n")
            
            print(f"Created {file_path}")
    
    def get_secrets_config(self) -> Dict[str, Any]:
        """Get secrets configuration for current environment."""
        secrets_config = {
            "development": {
                "secrets_file": ".env.secrets.dev",
                "use_vault": False,
                "encrypt_secrets": False
            },
            "staging": {
                "secrets_file": ".env.secrets.staging",
                "use_vault": True,
                "encrypt_secrets": True
            },
            "production": {
                "secrets_file": ".env.secrets.prod",
                "use_vault": True,
                "encrypt_secrets": True
            },
            "testing": {
                "secrets_file": ".env.secrets.test",
                "use_vault": False,
                "encrypt_secrets": False
            }
        }
        
        return secrets_config.get(self.environment, secrets_config["development"])


# Global environment config instance
env_config = EnvironmentConfig() 