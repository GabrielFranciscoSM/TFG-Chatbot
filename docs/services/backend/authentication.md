# Authentication & Security

Complete guide to authentication, authorization, and security in the Backend service.

## Overview

The Backend service uses:
- **JWT (JSON Web Tokens)** for stateless authentication
- **bcrypt** for password hashing
- **Role-Based Access Control (RBAC)** for authorization
- **OAuth2 Password Flow** for token issuance

## Authentication Concepts

### JWT (JSON Web Tokens)

JWT is a stateless authentication mechanism. The token contains encoded information that the server can verify without storing session state.

**Structure:**

A JWT consists of three parts separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJnYWJyaWVsIiwicm9sZSI6IlNUVURFTlQiLCJzdWJqZWN0cyI6WyJJTkYwMDEiXSwiZXhwIjoxNzA1MzM0NDQ1fQ.
1bfqH4qK9jHs8Kc_m_qL5pF3nH_mQ8qR2pT5vW7yZ8
```

1. **Header** (base64 encoded)
   ```json
   {
     "alg": "HS256",
     "typ": "JWT"
   }
   ```

2. **Payload** (base64 encoded)
   ```json
   {
     "sub": "gabriel",           // subject (username)
     "role": "STUDENT",          // user role
     "subjects": ["INF001"],     // enrolled subjects
     "exp": 1705334445           // expiration timestamp
   }
   ```

3. **Signature** (HMAC-SHA256)
   ```
   HMACSHA256(
     base64url(header) + "." + base64url(payload),
     secret_key
   )
   ```

### Password Hashing

Passwords are never stored in plain text. The backend uses **bcrypt** for secure hashing:

```
plain:  "secure_password_123"
hashed: "$2b$12$R9h7cIPz0giKl4pBM9mryOVGfzDmVxM5e.c2AZ6.d5bFTlwzFcF9u"
```

**Bcrypt Benefits:**
- Salted: Each hash is unique even for same password
- Slow: Intentionally slow to resist brute force attacks
- Adaptive: Cost factor can be increased as hardware improves

---

## Authentication Flow

### Login Process

```mermaid
flowchart TD
    A["1. User submits credentials<br/>POST /token<br/>username: gabriel<br/>password: secure_password"] --> B["2. Backend validates"]
    
    B --> C["Query MongoDB: find user by username"]
    C --> D["Verify password: bcrypt.verify"]
    D --> E{Password matches?}
    
    E -->|"✓ Valid"| F["3a. Generate JWT token"]
    E -->|"✗ Invalid"| G["3b. Return 401 Unauthorized"]
    
    F --> H["Create payload:<br/>sub: gabriel<br/>role: STUDENT<br/>subjects: INF001<br/>exp: now + 30 min"]
    H --> I["Sign with SECRET_KEY"]
    I --> J["Return token to client"]
    
    J --> K["4. Client stores token<br/>localStorage / sessionStorage / In-memory"]
    K --> L["5. Use token in requests<br/>Authorization: Bearer &lt;token&gt;"]
    
    style G fill:#f66,stroke:#333
    style F fill:#6f6,stroke:#333
```

### Token Lifespan

Tokens have a configurable expiration time (default: 30 minutes):

```python
# From config.py
access_token_expire_minutes: int = 30
```

**After expiration:**
- Token is invalid
- User must login again
- New token is issued

**Extending access without re-login:**
- Implement refresh token flow (not currently implemented)
- Consider for future improvement

---

## Using Tokens

### Token Acquisition

**Endpoint:** `POST /token`

**Request (Form Data):**
```
username: gabriel
password: secure_password_123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Token Usage

Include token in Authorization header for all authenticated requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example with cURL:**
```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer eyJhbGc..."
```

**Example with Fetch:**
```javascript
const response = await fetch("http://localhost:8000/users/me", {
  headers: {
    "Authorization": `Bearer ${access_token}`
  }
});
```

**Example with httpx (Python):**
```python
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8000/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
```

### Token Validation

The backend validates the token on each request:

```python
# From dependencies.py
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 1. Extract token from header
    # 2. Decode JWT signature
    # 3. Verify expiration
    # 4. Extract claims
    # 5. Query user from MongoDB
    # 6. Return UserInDB
```

If token is invalid or expired, request is rejected with `401 Unauthorized`.

---

## Role-Based Access Control (RBAC)

### User Roles

Three roles exist in the system:

| Role | Code | Capabilities |
|------|------|--------------|
| **Student** | `STUDENT` | Take tests, chat with AI, view own subjects |
| **Professor** | `PROFESSOR` | Manage subjects, view student analytics |
| **Admin** | `ADMIN` | Full system access, user management |

### Role in Token

User's role is encoded in JWT:

```json
{
  "sub": "gabriel",
  "role": "STUDENT",
  "exp": 1705334445
}
```

### Authorization Checks

Endpoints check role before processing requests:

```python
# Example: Admin-only endpoint
@router.get("/admin/users")
async def list_all_users(user: UserInDB = Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    # ... rest of logic
```

### Permission Matrix

| Endpoint | STUDENT | PROFESSOR | ADMIN |
|----------|---------|-----------|-------|
| `POST /register` | ✓ | ✓ | ✓ |
| `POST /token` | ✓ | ✓ | ✓ |
| `GET /users/me` | ✓ | ✓ | ✓ |
| `PUT /users/me` | ✓ | ✓ | ✓ |
| `GET /users/{username}` | ✗ | ✓ | ✓ |
| `GET /subjects` | ✓ | ✓ | ✓ |
| `POST /subjects` | ✗ | ✗ | ✓ |
| `GET /subjects/enrolled` | ✓ | ✗ | ✓ |
| `POST /subjects/{id}/enroll` | ✓ | ✗ | ✗ |
| `POST /chat` | ✓ | ✓ | ✓ |
| `GET /sessions` | ✓ | ✓ | ✓ |
| `GET /professor/students` | ✗ | ✓ | ✓ |
| `GET /professor/subjects/{id}/analytics` | ✗ | ✓ | ✓ |
| `GET /admin/users` | ✗ | ✗ | ✓ |
| `POST /admin/users/{id}/role` | ✗ | ✗ | ✓ |

### Resource-Level Authorization

Beyond role checks, the system validates resource ownership:

**Session Access:**
```python
# Users can only access their own sessions
if session["user_id"] != user.username:
    raise HTTPException(status_code=403)
```

**Subject Enrollment:**
```python
# Students can only use subjects they're enrolled in
if user.role == UserRole.STUDENT and subject not in user.subjects:
    raise HTTPException(status_code=403)
```

**Professor's Subjects:**
```python
# Professors can only access their own subjects
subject = subjects_collection.find_one({"_id": subject_id})
if subject["professor_id"] != user.username:
    raise HTTPException(status_code=403)
```

---

## Dependency Injection for Auth

FastAPI's dependency injection simplifies authentication:

### Basic Authentication Dependency

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    users_collection = Depends(get_users_collection)
):
    # Validate token
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    username = payload.get("sub")
    
    # Get user from database
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401)
    
    return UserInDB(**user)
```

### Using in Endpoints

```python
@router.get("/users/me")
async def get_profile(user: UserInDB = Depends(get_current_user)):
    # user is automatically injected and authenticated
    return user

@router.get("/admin/users")
async def admin_list_users(user: UserInDB = Depends(get_current_user)):
    # Check role
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403)
    # ... rest of logic
```

This pattern:
- Extracts token from `Authorization` header
- Validates signature and expiration
- Fetches user from database
- Automatically returns 401 if invalid
- Makes code clean and testable

---

## Security Implementation Details

### Password Hashing

```python
from backend.security import get_password_hash, verify_password

# Hashing on registration
hashed = get_password_hash("secure_password_123")
# Result: "$2b$12$R9h7cIPz0giKl4pBM9mryOVGfzDmVxM5e.c2AZ6..."

# Verification on login
is_valid = verify_password("secure_password_123", hashed_from_db)
# Result: True or False
```

**Bcrypt Configuration:**
```python
import bcrypt

salt = bcrypt.gensalt()  # Default cost factor: 12
hashed = bcrypt.hashpw(password.encode(), salt).decode()
```

Cost factor 12 means:
- ~0.3 seconds to hash a password
- Resistant to GPU-accelerated attacks
- Can be increased as hardware improves

### JWT Signing

```python
from jose import jwt
from backend.config import settings

# Create token
token = jwt.encode(
    payload={"sub": user_id, "role": role_name, "exp": expiration},
    key=settings.secret_key.get_secret_value(),
    algorithm=settings.algorithm  # HS256
)

# Verify token
payload = jwt.decode(
    token,
    key=settings.secret_key.get_secret_value(),
    algorithms=[settings.algorithm]
)
```

**Security notes:**
- `secret_key` must be kept secure (use environment variables)
- `HS256` (HMAC-SHA256) uses symmetric key (server must have secret)
- Alternative: `RS256` uses public key cryptography (more secure for distributed systems)

### Secret Management

Sensitive values use `SecretStr` from Pydantic:

```python
from pydantic import SecretStr

class Settings(BaseSettings):
    secret_key: SecretStr = SecretStr("default-only-for-dev")
    mongo_root_password: SecretStr | None = None
```

**Benefits:**
- Excludes from string representations
- Prevents accidental logging of secrets
- Type-safe secret handling

**Usage:**
```python
actual_secret = settings.secret_key.get_secret_value()
```

---

## Common Security Issues & Solutions

### Issue: Token Exposure in Logs

**Problem:**
```python
logger.info(f"User token: {token}")  # ❌ Token visible in logs
```

**Solution:**
```python
logger.info(f"User authenticated successfully")  # ✓ No token in logs
```

### Issue: Hardcoded Secret Key

**Problem:**
```python
secret_key = "my-secret-key"  # ❌ In source code
```

**Solution:**
```python
SECRET_KEY=your-secret-key-here
# In .env, never committed to git
```

### Issue: Missing HTTPS

**Problem:**
```
Authorization: Bearer <token>
# Sent over unencrypted HTTP - token visible to anyone
```

**Solution:**
Always use HTTPS in production to encrypt transmission.

### Issue: Token in URL

**Problem:**
```
GET /api/users?token=eyJ0eXAiOi...  # ❌ Visible in logs, history
```

**Solution:**
```
GET /api/users
Authorization: Bearer eyJ0eXAiOi...  # ✓ In header, encrypted over HTTPS
```

### Issue: No Token Expiration

**Problem:**
```python
token_lifetime = None  # ❌ Token never expires
```

**Solution:**
```python
access_token_expire_minutes: int = 30  # ✓ Tokens expire
```

---

## Testing Authentication

### Testing Login

```python
import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient, test_user):
    response = client.post("/token", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client: TestClient, test_user):
    response = client.post("/token", data={
        "username": test_user["username"],
        "password": "wrong_password"
    })
    assert response.status_code == 401
```

### Testing Protected Endpoints

```python
def test_get_profile_with_token(client: TestClient, test_user, auth_token):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]

def test_get_profile_without_token(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401
```

### Testing Authorization

```python
def test_admin_endpoint_student_denied(client: TestClient, student_token):
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403

def test_admin_endpoint_admin_allowed(client: TestClient, admin_token):
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
```

---

## Configuration

See [configuration.md](./configuration.md) for environment variables:

- `SECRET_KEY` - JWT signing key
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token lifetime

**Example `.env`:**
```
SECRET_KEY=my-super-secret-key-min-32-chars-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Best Practices

1. **Use HTTPS in Production**
   - Always encrypt token transmission
   - Use TLS/SSL certificates

2. **Keep Secrets Secure**
   - Never commit `.env` to git
   - Use environment variables
   - Rotate secrets periodically

3. **Validate Inputs**
   - Use Pydantic for type validation
   - Never trust user input

4. **Monitor Authentication**
   - Log failed login attempts
   - Alert on repeated failures
   - Track token usage

5. **Implement Token Refresh** (Future)
   - Short-lived access tokens (15 min)
   - Long-lived refresh tokens (7 days)
   - Allows revoking compromised tokens

6. **Use HTTPS Headers**
   - `Strict-Transport-Security`
   - `X-Content-Type-Options`
   - `X-Frame-Options`

7. **Rate Limit Auth Endpoints**
   - Prevent brute force attacks
   - 5-10 requests per minute per IP

8. **Implement 2FA** (Future)
   - Additional security layer
   - SMS or authenticator app

---

## Troubleshooting

### "Not authenticated" Error

**Cause:** Missing or invalid token

**Solution:**
1. Ensure token is in `Authorization: Bearer <token>` header
2. Verify token hasn't expired
3. Login again to get fresh token

### "Incorrect username or password"

**Cause:** Wrong credentials

**Solution:**
1. Verify username spelling
2. Reset password if forgotten
3. Check caps lock

### "Admin access required"

**Cause:** User doesn't have admin role

**Solution:**
1. Admin needs to promote user: `POST /admin/users/{username}/role`
2. Only admins can create other admins

### Token Validation Fails

**Cause:** Token was tampered with or secret key changed

**Solution:**
1. Users must re-login
2. Don't change `SECRET_KEY` in production (invalidates all tokens)
3. Use token refresh flow if available

---

## Related Documentation

- [API Endpoints](./api-endpoints.md) - All available endpoints
- [Configuration](./configuration.md) - Environment variables
- [Development](./development.md) - Testing setup
