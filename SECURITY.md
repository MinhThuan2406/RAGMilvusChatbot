# Security Guidelines

## 🔒 Confidential Information

This repository contains sensitive configuration and data that should **NEVER** be committed to version control.

### Files Excluded from Git

#### Environment Files
- `backend/.env.secrets` - Contains encrypted API keys and tokens
- `backend/.env.backup` - Contains encryption keys
- Any `.env*` files

#### Database and Data Directories
- `data/backend/` - Milvus database files
- `data/chroma_db/` - ChromaDB vector database
- `data/raw_docs/` - Raw document storage
- `data/store_docs/` - Processed document storage

#### Test Files with Secrets
- `test_secret_decrypt.py` - Debug files that might expose secrets
- `test_container_debug.py`
- `test_container_ingestion.py`
- `test_embedding_debug.py`
- `test_ingestion_api.py`
- `test_ingestion.py`
- `test_milvus_connection.py`

#### Model Files
- `miscellaneous/tf_model.h5` - Trained model files

## 🔐 Secrets Management

### Setup Required Secrets
1. Create `backend/.env.secrets` with your API keys:
```json
{
  "environment": "development",
  "secrets": {
    "OPENAI_API_KEY": "your-encrypted-key-here",
    "NGROK_AUTHTOKEN": "your-encrypted-token-here"
  }
}
```

2. Set encryption key in environment:
```bash
export SECRETS_ENCRYPTION_KEY="your-encryption-key"
```

### Using the Secrets Manager
```python
from backend.app.core.secrets import get_secret

api_key = get_secret("OPENAI_API_KEY", "development")
```

## 🚨 Security Checklist Before Committing

- [ ] No `.env*` files are being committed
- [ ] No database files in `data/` directory are being committed
- [ ] No API keys or tokens are hardcoded in source code
- [ ] Test files with secrets are excluded
- [ ] Model files are excluded if they contain sensitive data

## 🔧 Development Setup

1. **Clone the repository**
2. **Create your secrets file**: `backend/.env.secrets`
3. **Set encryption key**: `export SECRETS_ENCRYPTION_KEY="your-key"`
4. **Run setup scripts**: `python backend/scripts/setup_secrets.py`

## 📝 Environment Variables

Required environment variables:
- `SECRETS_ENCRYPTION_KEY` - For decrypting secrets
- `OPENAI_API_KEY` - OpenAI API access (stored in secrets)
- `NGROK_AUTHTOKEN` - Ngrok authentication (stored in secrets)

## 🛡️ Security Best Practices

1. **Never commit secrets directly**
2. **Use the secrets manager for all sensitive data**
3. **Encrypt all API keys and tokens**
4. **Keep database files local only**
5. **Use environment-specific configurations**
6. **Regular security audits of committed files**

## 🚨 Emergency Contacts

If you accidentally commit sensitive information:
1. **Immediately revoke exposed credentials**
2. **Create new API keys/tokens**
3. **Update secrets file with new credentials**
4. **Consider repository history cleanup if necessary** 