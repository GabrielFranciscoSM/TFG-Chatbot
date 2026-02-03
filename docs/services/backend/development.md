# Backend Development Guide

Complete guide for developing the Backend service locally.

## Prerequisites

- **Python:** 3.13+
- **uv:** Package manager (https://docs.astral.sh/uv/getting-started/)
- **MongoDB:** Local instance or Docker
- **Git:** Version control

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/GabrielFranciscoSM/TFG-Chatbot.git
cd TFG-Chatbot
```

### 2. Create Python Virtual Environment

Using `uv` (recommended):

```bash
uv venv                    # Create virtual environment
source .venv/bin/activate  # Activate (Linux/Mac)
# or
.venv\Scripts\activate     # Activate (Windows)
```

### 3. Install Dependencies

```bash
cd backend
uv sync                    # Install all dependencies
```

This installs:
- FastAPI, Uvicorn (web framework)
- PyMongo (MongoDB driver)
- python-jose (JWT)
- bcrypt (password hashing)
- pytest (testing)
- and more...

### 4. Create `.env` File

```bash
# In backend/ directory
cat > .env << EOF
# Service URLs
CHATBOT_SERVICE_URL=http://localhost:8080
RAG_SERVICE_URL=http://localhost:8081

# MongoDB
MONGO_HOSTNAME=localhost
MONGO_PORT=27017
DB_NAME=tfg_chatbot

# JWT
SECRET_KEY=dev-only-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=DEBUG
EOF
```

### 5. Start MongoDB

**Option A: Local Installation**

```bash
# macOS with Homebrew
brew install mongodb-community
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
net start MongoDB
```

**Option B: Docker**

```bash
# Use Docker Compose from project root
cd ..
docker compose up mongo -d

# Verify
docker compose exec mongo mongosh
```

## Running the Backend

### Start Development Server

```bash
cd backend
uv run python -m backend
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Access API

- **REST API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### Interactive Testing

Swagger UI at http://localhost:8000/docs provides:
- All endpoints listed
- Try-it-out feature for testing
- Request/response models
- Authentication form

## Development Workflow

### Making Changes

1. **Edit code** in `backend/` directory
2. **Save file** → Uvicorn auto-reloads
3. **Test in Swagger UI** or via tests
4. **Check logs** for errors

### File Structure

```
backend/
├── __main__.py        # Entry point
├── api.py             # FastAPI app setup
├── config.py          # Configuration
├── security.py        # Auth utilities
├── dependencies.py    # FastAPI dependencies
├── routers/           # Endpoints
│   ├── auth.py
│   ├── users.py
│   ├── subjects.py
│   ├── chat.py
│   ├── sessions.py
│   ├── professor.py
│   └── admin.py
├── models/            # Pydantic models
│   ├── admin.py
│   ├── common.py
│   └── professor.py
├── db/                # Database
│   └── mongo.py
└── tests/             # Tests
    ├── conftest.py
    ├── unit/
    └── integration/
```

### Adding a New Endpoint

1. **Create router function** in `routers/`:

```python
# routers/my_feature.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/my-feature", tags=["my-feature"])

@router.get("/")
async def get_my_feature(user = Depends(get_current_user)):
    return {"message": "Hello"}
```

2. **Add models** in `models/`:

```python
# models/my_feature.py
from pydantic import BaseModel

class MyFeatureResponse(BaseModel):
    message: str
```

3. **Register router** in `api.py`:

```python
from backend.routers import my_feature

app.include_router(my_feature.router)
```

4. **Write tests** in `tests/`:

```python
# tests/unit/test_my_feature.py
def test_get_my_feature(client, auth_token):
    response = client.get(
        "/my-feature/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

## Testing

### Running Tests

```bash
cd backend

# All tests
uv run pytest tests/ -v

# Unit tests only
uv run pytest tests/unit/ -v

# Specific test file
uv run pytest tests/unit/test_auth.py -v

# Specific test function
uv run pytest tests/unit/test_auth.py::test_register -v

# With coverage
uv run pytest tests/ --cov=backend --cov-report=html
```

### Test Markers

```bash
# Unit tests (fast, no external dependencies)
uv run pytest tests/ -m unit -v

# Integration tests (slow, use mongomock)
uv run pytest tests/ -m integration -v

# Infrastructure tests (need Docker)
uv run pytest tests/ -m container -v
```

### Writing Tests

**Example Unit Test:**

```python
# tests/unit/test_auth.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.unit
def test_register_success(client: TestClient):
    """Test successful user registration."""
    response = client.post("/register", json={
        "username": "gabriel",
        "email": "gabriel@example.com",
        "password": "secure_password_123",
        "full_name": "Gabriel Francisco",
        "role": "STUDENT"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "gabriel"
    assert "password" not in data

@pytest.mark.unit
def test_register_duplicate_username(client: TestClient):
    """Test registration with existing username."""
    # Assume user already exists (via fixture)
    response = client.post("/register", json={
        "username": "gabriel",  # Already exists
        "email": "different@example.com",
        "password": "secure_password_123",
        "full_name": "Another User",
        "role": "STUDENT"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
```

### Test Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def test_user():
    """Standard test user credentials."""
    return {
        "username": "gabriel",
        "email": "gabriel@example.com",
        "password": "secure_password_123"
    }

@pytest.fixture
def test_admin():
    """Test admin user."""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin_password_123",
        "role": "ADMIN"
    }

@pytest.fixture
def auth_token(client, test_user):
    """Get JWT token for test user."""
    response = client.post("/token", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    return response.json()["access_token"]
```

### Mocking MongoDB

The tests use `mongomock` to simulate MongoDB without external dependency:

```python
# conftest.py
@pytest.fixture
def mongodb():
    """In-memory MongoDB mock."""
    client = mongomock.MongoClient()
    db = client["tfg_chatbot"]
    yield db
    client.close()
```

## Debugging

### Using Print Statements

```python
@router.get("/debug")
async def debug_endpoint():
    print("DEBUG: This will appear in console")
    return {"status": "ok"}
```

### Using Python Debugger

**In VS Code:**

1. Add breakpoint (click line number)
2. Run with debugger:
   ```bash
   uv run python -m debugpy --listen 5678 -m backend
   ```
3. Attach VS Code debugger

**In Terminal:**

```python
import pdb; pdb.set_trace()
```

### Viewing Logs

Enable debug logging in `.env`:

```
LOG_LEVEL=DEBUG
```

All requests and responses will be logged with:
- Timestamp
- Request method and path
- Status code
- Response time
- Correlation ID

### MongoDB Queries

Check what queries are being executed:

```python
from backend.db.mongo import get_db

db = get_db()

# Enable command monitoring
from pymongo import monitoring

def command_started(event):
    print(f"Query: {event.command}")

monitoring.register(command_started)
```

## Performance Testing

### Load Testing with Apache Bench

```bash
# Single request
ab -n 100 -c 10 http://localhost:8000/health

# With authentication
ab -n 100 -c 10 -H "Authorization: Bearer <token>" \
  http://localhost:8000/users/me
```

### Using Locust

```bash
# Install
uv pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

## Code Quality

### Linting with Ruff

```bash
cd backend

# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix
```

### Code Formatting with Black

```bash
# Format code
uv run black .

# Check formatting
uv run black . --check
```

### Import Sorting with isort

```bash
# Sort imports
uv run isort .

# Check imports
uv run isort . --check
```

### Pre-commit Hooks

```bash
# Install pre-commit
uv pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Database Operations

### Seed Development Data

```bash
cd ..
uv run python scripts/seed_users.py

# Creates test users:
# - gabriel (STUDENT)
# - prof_ana (PROFESSOR)
# - admin (ADMIN)
```

### Query MongoDB CLI

```bash
mongosh mongodb://localhost:27017/tfg_chatbot

> db.users.find()
> db.users.find_one({"username": "gabriel"})
> db.subjects.countDocuments()
```

### Reset Database

```bash
# Delete all data (keep indexes)
mongosh << EOF
use tfg_chatbot
db.users.deleteMany({})
db.sessions.deleteMany({})
db.subjects.deleteMany({})
EOF

# Or use Python
from backend.db.mongo import get_db
db = get_db()
db.users.delete_many({})
db.sessions.delete_many({})
db.subjects.delete_many({})
```

## Docker Development

### Build Local Image

```bash
cd backend
docker build -t tfg-backend:dev .
```

### Run in Docker

```bash
docker run -p 8000:8000 \
  --env-file .env \
  --network host \
  tfg-backend:dev
```

### Docker Compose (Full Stack)

```bash
cd ..
docker compose up -d

# View logs
docker compose logs -f backend

# Rebuild after changes
docker compose build backend
docker compose up -d backend
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Cause:** Dependencies not installed

**Solution:**
```bash
cd backend
uv sync
```

### Issue: "Cannot connect to MongoDB"

**Cause:** MongoDB not running

**Solution:**
```bash
# Check if running
mongo --version

# Start if installed
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux

# Or use Docker
docker compose up mongo -d
```

### Issue: "Port 8000 already in use"

**Cause:** Another application using port 8000

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Or use different port
uv run python -m backend --port 8001
```

### Issue: JWT Token Expired

**Cause:** Token lifetime exceeded

**Solution:**
```bash
# Increase token lifetime in .env
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Or login again to get new token
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=gabriel&password=secure_password_123"
```

### Issue: Slow API Responses

**Cause:** Missing database indexes

**Solution:**
```python
# Check and create indexes
from backend.db.mongo import get_db
db = get_db()

# Create indexes
db.users.create_index("username")
db.users.create_index("email")
db.sessions.create_index("user_id")
```

## VS Code Setup

### Extensions

1. **Python** (ms-python.python)
2. **Pylance** (ms-python.vscode-pylance)
3. **REST Client** (humao.rest-client)
4. **Thunder Client** (rangav.vscode-thunder-client)
5. **MongoDB** (mongodb.mongodb-vscode)

### Settings (`.vscode/settings.json`)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "python.linting.ruffEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": ".venv/bin/pytest"
}
```

### Debug Configuration (`.vscode/launch.json`)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "backend",
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

## Useful Commands

```bash
# Navigate to backend
cd backend

# Install/sync dependencies
uv sync

# Run development server
uv run python -m backend

# Run tests with coverage
uv run pytest tests/ --cov=backend --cov-report=html

# Check code quality
uv run ruff check . && uv run black . --check

# Format code
uv run ruff check . --fix && uv run black .

# Clear cache
find . -type d -name __pycache__ -exec rm -r {} +
rm -rf .pytest_cache

# Generate requirements.txt
uv pip freeze > requirements.txt
```

## Next Steps

1. **Explore existing code:** Read `routers/*.py` to understand patterns
2. **Run tests:** `uv run pytest tests/ -v`
3. **Try endpoints:** Visit http://localhost:8000/docs
4. **Make a change:** Edit a router and test your change
5. **Write a test:** Create a new test in `tests/`
6. **Submit PR:** Push branch and create pull request

## Related Documentation

- [Architecture](./architecture.md) - System design
- [API Endpoints](./api-endpoints.md) - All endpoints
- [Configuration](./configuration.md) - Environment setup
- [Database](./database.md) - MongoDB schema
- [Authentication](./authentication.md) - JWT and security
