# Backend Configuration Guide

Complete reference for configuring the Backend service.

## Configuration Overview

The Backend service is configured using environment variables through a `.env` file. The configuration is managed by Pydantic `BaseSettings` which provides type-safe, validated settings.

**Configuration File Location:** `.env` in the project root or backend directory

**Configuration Source:** [backend/config.py](../../backend/config.py)

---

## Environment Variables Reference

### Service URLs

These variables specify how the Backend communicates with other services.

#### `CHATBOT_SERVICE_URL`

- **Type:** String
- **Default:** `http://chatbot:8080`
- **Description:** URL to the Chatbot service for forwarding chat requests
- **Example:** `http://localhost:8080` (local development)
- **Docker:** `http://chatbot:8080` (Docker Compose service name)
- **Production:** `https://chatbot.example.com:8080`

#### `RAG_SERVICE_URL`

- **Type:** String
- **Default:** `http://rag_service:8081`
- **Description:** URL to the RAG service (currently proxied through chatbot)
- **Example:** `http://localhost:8081` (local development)
- **Docker:** `http://rag_service:8081` (Docker Compose service name)
- **Note:** Direct calls from backend are not currently implemented

#### `CHATBOT_TIMEOUT`

- **Type:** Float
- **Default:** `120.0`
- **Unit:** Seconds
- **Description:** Timeout for requests to the chatbot service
- **Range:** 10.0 to 300.0 recommended
- **Notes:**
  - LLM requests can be slow (especially with Ollama)
  - Increase if getting frequent timeouts
  - Decrease to fail fast for debugging

### MongoDB Configuration

Configure how the Backend connects to MongoDB.

#### Option 1: MongoDB URI (Recommended)

#### `MONGO_URI`

- **Type:** SecretStr (sensitive)
- **Default:** None (falls back to hostname-based)
- **Description:** Complete MongoDB connection string
- **Examples:**
  ```
  mongodb://localhost:27017
  mongodb://user:password@localhost:27017/admin
  mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
  ```

**When to use:** MongoDB Atlas, external databases, complex setups

#### Option 2: Hostname-Based Configuration

If `MONGO_URI` is not set, these variables are used:

#### `MONGO_HOSTNAME`

- **Type:** String
- **Default:** None
- **Description:** MongoDB server hostname/IP
- **Examples:** `localhost`, `mongo`, `mongodb.example.com`

#### `MONGO_PORT`

- **Type:** String
- **Default:** `27017`
- **Description:** MongoDB server port
- **Standard port:** 27017

#### `MONGO_ROOT_USERNAME`

- **Type:** String
- **Default:** None
- **Description:** MongoDB root username for authentication
- **Required if:** MongoDB requires authentication

#### `MONGO_ROOT_PASSWORD`

- **Type:** SecretStr (sensitive)
- **Default:** None
- **Description:** MongoDB root password for authentication
- **Required if:** `MONGO_ROOT_USERNAME` is set

#### `MONGO_AUTH_DB`

- **Type:** String
- **Default:** None
- **Description:** Database for authentication (often "admin" or "test")
- **Example:** `admin`
- **Note:** Only used if `MONGO_ROOT_USERNAME` is set

#### `DB_NAME`

- **Type:** String
- **Default:** `tfg_chatbot`
- **Description:** Name of the MongoDB database to use
- **Note:** This database will be created if it doesn't exist

### Example MongoDB Configurations

**Local Development (No Auth):**
```env
MONGO_HOSTNAME=localhost
MONGO_PORT=27017
```

**Docker Compose:**
```env
MONGO_HOSTNAME=mongo
MONGO_PORT=27017
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=rootpassword
DB_NAME=tfg_chatbot
```

**MongoDB Atlas (Cloud):**
```env
MONGO_URI=mongodb+srv://user:password@cluster0.mongodb.net/tfg_chatbot?retryWrites=true&w=majority
```

**Docker with Authentication:**
```env
MONGO_URI=mongodb://root:rootpassword@mongo:27017/tfg_chatbot?authSource=admin
```

### Authentication Configuration

JWT and password security settings.

#### `SECRET_KEY`

- **Type:** SecretStr (sensitive)
- **Default:** `dev-only-secret-key-change-in-production`
- **Description:** Secret key for signing JWT tokens
- **Requirements:**
  - Minimum 32 characters (recommended)
  - Random and unpredictable
  - Never hardcoded in production
  - Never committed to git
- **How to Generate:**
  ```python
  import secrets
  secrets.token_urlsafe(32)
  # Output: "AbCdEfGhIjKlMnOpQrStUvWxYz123456789"
  ```
- **⚠️ CRITICAL:** Changing this invalidates all existing tokens

**Development:**
```env
SECRET_KEY=dev-only-secret-key-change-in-production
```

**Production (Example):**
```env
SECRET_KEY=xK9pL2mN5qR8sT1vW4xY7zB0cD3eF6gH9jK2lM5nO8pQ1rS4tU7vW0xY3zB6c
```

#### `ALGORITHM`

- **Type:** String
- **Default:** `HS256`
- **Description:** JWT signing algorithm
- **Options:**
  - `HS256` - HMAC-SHA256 (current, symmetric key)
  - `RS256` - RSA-SHA256 (asymmetric, for distributed systems)
  - `ES256` - ECDSA-SHA256 (elliptic curve)
- **Note:** Only `HS256` currently supported

```env
ALGORITHM=HS256
```

#### `ACCESS_TOKEN_EXPIRE_MINUTES`

- **Type:** Integer
- **Default:** `30`
- **Unit:** Minutes
- **Description:** How long JWT tokens are valid after issuance
- **Range:** 1 to 1440 (1 day)
- **Recommendations:**
  - Short-lived (15-30 min) for better security
  - Longer (60-120 min) for better UX
  - Very short (5-10 min) for high-security apps

**Development (longer for testing):**
```env
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

**Production (shorter for security):**
```env
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

### Logging Configuration

#### `LOG_LEVEL`

- **Type:** String
- **Default:** `INFO`
- **Options:**
  - `DEBUG` - Most verbose, includes all debug info
  - `INFO` - Standard, recommended for production
  - `WARNING` - Only warnings and errors
  - `ERROR` - Only errors
  - `CRITICAL` - Only critical errors
- **Development:** DEBUG
- **Production:** INFO or WARNING

```env
LOG_LEVEL=INFO
```

---

## Complete Example `.env` File

```bash
# ============================================================================
# BACKEND SERVICE CONFIGURATION
# ============================================================================

# Service URLs
CHATBOT_SERVICE_URL=http://chatbot:8080
RAG_SERVICE_URL=http://rag_service:8081
CHATBOT_TIMEOUT=120.0

# MongoDB Configuration (Option 1: URI)
# MONGO_URI=mongodb://localhost:27017

# MongoDB Configuration (Option 2: Hostname-based)
MONGO_HOSTNAME=mongo
MONGO_PORT=27017
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=rootpassword
MONGO_AUTH_DB=admin
DB_NAME=tfg_chatbot

# JWT & Authentication
SECRET_KEY=xK9pL2mN5qR8sT1vW4xY7zB0cD3eF6gH9jK2lM5nO8pQ1rS4tU7vW0xY3zB6c
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

---

## Configuration by Environment

### Development (Local)

**.env.local** or **.env**:
```bash
# Use localhost for all services
CHATBOT_SERVICE_URL=http://localhost:8080
RAG_SERVICE_URL=http://localhost:8081

# Local MongoDB without auth
MONGO_HOSTNAME=localhost
MONGO_PORT=27017
DB_NAME=tfg_chatbot

# Loose security for development
SECRET_KEY=dev-only-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=120
LOG_LEVEL=DEBUG
```

**Run:**
```bash
cd backend
uv sync
uv run python -m backend
```

### Docker Compose

**.env** (in project root):
```bash
# Use Docker service names
CHATBOT_SERVICE_URL=http://chatbot:8080
RAG_SERVICE_URL=http://rag_service:8081

# MongoDB in Docker with auth
MONGO_HOSTNAME=mongo
MONGO_PORT=27017
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=rootpassword
MONGO_AUTH_DB=admin
DB_NAME=tfg_chatbot

# Secure settings
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
```

**Run:**
```bash
docker compose up -d
```

### Production

**.env** (on production server, never in git):
```bash
# Production service URLs (with HTTPS)
CHATBOT_SERVICE_URL=https://chatbot.example.com:8080
RAG_SERVICE_URL=https://rag.example.com:8081

# Production MongoDB (Atlas or managed service)
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/tfg_chatbot?retryWrites=true&w=majority

# Strict security
SECRET_KEY=<generate-unique-secure-key>
ACCESS_TOKEN_EXPIRE_MINUTES=15
LOG_LEVEL=WARNING

# Optional: Additional security headers
SECURE_HTTPS=true
CORS_ORIGINS=https://app.example.com
```

---

## Loading Configuration

The configuration is loaded from `.env` file in this order:

1. **Project Root**: `/home/gabriel/clase/TFG/TFG-Chatbot/.env`
2. **Backend Directory**: `/home/gabriel/clase/TFG/TFG-Chatbot/backend/.env`
3. **Environment Variables**: System environment variables override file values

**Priority (highest to lowest):**

```mermaid
flowchart TB
    A[System Environment Variables] --> B[Backend/.env]
    B --> C[Project Root/.env]
    C --> D[Default values in config.py]
    
    style A fill:#f9f,stroke:#333
    style D fill:#ddd,stroke:#333
```

### Accessing Settings in Code

```python
from backend.config import settings

# Access any setting
print(settings.chatbot_service_url)  # http://chatbot:8080
print(settings.secret_key.get_secret_value())  # Secret key value
print(settings.access_token_expire_minutes)  # 30
```

---

## MongoDB Connection Strings

### String Format

```
mongodb://[username[:password]@]host[:port][/[database][?options]]
```

### Examples

**Local (No Auth):**
```
mongodb://localhost:27017
```

**Local (With Auth):**
```
mongodb://root:password@localhost:27017/?authSource=admin
```

**Docker Service:**
```
mongodb://mongo:27017
```

**Docker Service (With Auth):**
```
mongodb://root:password@mongo:27017/?authSource=admin
```

**MongoDB Atlas (Cloud):**
```
mongodb+srv://user:password@cluster0.mongodb.net/database?retryWrites=true&w=majority
```

**Connection Pooling:**
```
mongodb://localhost:27017/?maxPoolSize=50&minPoolSize=10
```

---

## Common Configuration Mistakes

### ❌ Mistake 1: Hardcoding Secret Key

```python
# In config.py - WRONG!
secret_key: str = "my-secret-key"
```

**Fix:**
```python
# In config.py
secret_key: SecretStr = SecretStr("dev-only...")

# In .env
SECRET_KEY=actual-secure-key-from-environment
```

### ❌ Mistake 2: MongoDB Connection Fails

**Error:** "Cannot connect to MongoDB"

**Cause:** Wrong hostname or port

**Debug:**
```bash
# Test connection
mongosh mongodb://localhost:27017

# Check configured values
echo $MONGO_HOSTNAME  # Should be set
echo $MONGO_PORT      # Should be 27017
```

**Fix:**
- Ensure MongoDB is running: `docker compose up mongo`
- Check hostname (localhost vs. mongo service name)
- Verify port (default 27017)

### ❌ Mistake 3: Token Expires Too Quickly

**Error:** "Token expired" shortly after login

**Cause:** `ACCESS_TOKEN_EXPIRE_MINUTES` too low

**Fix:**
```env
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Or higher for testing
```

### ❌ Mistake 4: Chatbot Service Not Found

**Error:** "503 Service Unavailable: Chatbot service unavailable"

**Cause:** Wrong `CHATBOT_SERVICE_URL`

**Debug:**
```bash
# Test connection
curl http://localhost:8080/health

# Check configured URL
echo $CHATBOT_SERVICE_URL
```

**Fix:**
- Ensure chatbot service is running
- Use correct hostname (localhost vs. service name)
- Check port (default 8080)

---

## Validation

The configuration is validated on startup:

```python
from pydantic import ValidationError
from backend.config import Settings

try:
    settings = Settings()
except ValidationError as e:
    print(f"Configuration error: {e}")
```

**Common validation errors:**
- Invalid `ACCESS_TOKEN_EXPIRE_MINUTES` (must be int)
- Invalid `CHATBOT_TIMEOUT` (must be float)
- Missing required variables

---

## Security Best Practices

1. **Never Commit .env to Git**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   .env.*.local
   ```

2. **Rotate Secrets Regularly**
   - Change `SECRET_KEY` every 3-6 months
   - All existing tokens will be invalidated
   - Use token refresh mechanism (future)

3. **Use Different Secrets Per Environment**
   - Development: Simple secret (it's okay if leaked)
   - Production: Complex, randomly generated secret
   - Staging: Different from production

4. **Secure .env File Permissions**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

5. **Use Environment Variable Management**
   - HashiCorp Vault for production
   - AWS Secrets Manager
   - GitHub Secrets for CI/CD

6. **Audit Configuration Changes**
   - Track SECRET_KEY rotations
   - Monitor timeout changes
   - Log when services are reconfigured

---

## Debugging Configuration

### Check Current Configuration

```python
# Interactive debugging
from backend.config import settings

print(f"Chatbot URL: {settings.chatbot_service_url}")
print(f"MongoDB URI: {settings.get_mongo_uri()}")
print(f"Token expires: {settings.access_token_expire_minutes} minutes")
```

### Enable Debug Logging

```env
LOG_LEVEL=DEBUG
```

### Test MongoDB Connection

```python
from backend.db.mongo import get_db

db = get_db()
print(db.client.server_info())  # Will fail if connection fails
```

### Test Service Connectivity

```bash
# Test chatbot service
curl http://localhost:8080/health

# Test RAG service
curl http://localhost:8081/health
```

---

## Migration Between Environments

### Moving from Development to Docker Compose

**Before:**
```env
CHATBOT_SERVICE_URL=http://localhost:8080
MONGO_HOSTNAME=localhost
```

**After:**
```env
CHATBOT_SERVICE_URL=http://chatbot:8080
MONGO_HOSTNAME=mongo
```

**Key changes:**
- `localhost` → service name (mongo, chatbot, rag_service)
- Port numbers may stay the same (internal to Docker Compose)

### Moving from Docker Compose to Production

**Before:**
```env
MONGO_HOSTNAME=mongo
SECRET_KEY=dev-only-secret-key-change-in-production
```

**After:**
```env
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/tfg_chatbot
SECRET_KEY=<generate-new-secure-key>
```

**Key changes:**
- Use MongoDB Atlas or managed service
- Generate new, strong SECRET_KEY
- Use HTTPS URLs for services
- Enable logging and monitoring

---

## Related Documentation

- [Development Guide](./development.md) - Setting up development environment
- [Deployment Guide](./deployment.md) - Deploying to production
- [Architecture](./architecture.md) - System design and components
