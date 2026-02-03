# Backend API Endpoints Reference

Complete reference for all Backend service endpoints with request/response examples.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via `/token` endpoint after login.

---

## Authentication Endpoints

### POST /register

Create a new user account.

**Request Body:**
```json
{
  "username": "gabriel",
  "email": "gabriel@example.com",
  "password": "secure_password_123",
  "full_name": "Gabriel Francisco",
  "role": "STUDENT"
}
```

**Response (201):**
```json
{
  "username": "gabriel",
  "email": "gabriel@example.com",
  "full_name": "Gabriel Francisco",
  "role": "STUDENT",
  "subjects": []
}
```

**Errors:**
- `400`: Username or email already registered
- `422`: Invalid request body

---

### POST /token

Login and receive JWT access token.

**Request Body (Form Data):**
```
username: gabriel
password: secure_password_123
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Token Claims:**
```json
{
  "sub": "gabriel",
  "role": "STUDENT",
  "subjects": ["INF001", "MAT002"],
  "exp": 1705334445
}
```

**Errors:**
- `401`: Incorrect username or password
- `422`: Missing form fields

---

## User Endpoints

### GET /users/me

Get authenticated user's profile.

**Required:** JWT Authentication

**Response (200):**
```json
{
  "username": "gabriel",
  "email": "gabriel@example.com",
  "full_name": "Gabriel Francisco",
  "role": "STUDENT",
  "subjects": ["INF001", "MAT002"],
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

**Errors:**
- `401`: Not authenticated

---

### PUT /users/me

Update authenticated user's profile.

**Required:** JWT Authentication

**Request Body:**
```json
{
  "full_name": "Gabriel Francisco García",
  "email": "gabriel.new@example.com",
  "preferences": {
    "theme": "light",
    "notifications": false
  }
}
```

**Response (200):**
```json
{
  "username": "gabriel",
  "email": "gabriel.new@example.com",
  "full_name": "Gabriel Francisco García",
  "role": "STUDENT",
  "subjects": ["INF001", "MAT002"],
  "preferences": {
    "theme": "light",
    "notifications": false
  }
}
```

**Errors:**
- `401`: Not authenticated
- `400`: Email already in use
- `422`: Invalid request body

---

### GET /users/{username}

Get another user's profile (Professor/Admin only).

**Required:** JWT Authentication (Professor or Admin role)

**Path Parameters:**
```
username: gabriel
```

**Response (200):**
```json
{
  "username": "gabriel",
  "email": "gabriel@example.com",
  "full_name": "Gabriel Francisco",
  "role": "STUDENT",
  "subjects": ["INF001"]
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions
- `404`: User not found

---

## Subject Endpoints

### GET /subjects

List all subjects.

**Required:** JWT Authentication

**Query Parameters:**
```
professor_id: prof_ana (optional)
page: 1 (optional)
limit: 20 (optional)
```

**Response (200):**
```json
[
  {
    "_id": "INF001",
    "name": "Algorithms",
    "description": "Course on algorithm design and analysis",
    "professor_id": "prof_ana",
    "student_count": 45
  },
  {
    "_id": "MAT002",
    "name": "Linear Algebra",
    "description": "Vector spaces, matrices, and eigenvalues",
    "professor_id": "prof_juan",
    "student_count": 38
  }
]
```

**Errors:**
- `401`: Not authenticated

---

### POST /subjects

Create a new subject (Admin only).

**Required:** JWT Authentication (Admin role)

**Request Body:**
```json
{
  "subject_id": "INF001",
  "name": "Algorithms",
  "description": "Course on algorithm design and analysis",
  "professor_id": "prof_ana"
}
```

**Response (201):**
```json
{
  "_id": "INF001",
  "name": "Algorithms",
  "description": "Course on algorithm design and analysis",
  "professor_id": "prof_ana",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions (not admin)
- `400`: Subject already exists
- `422`: Invalid request body

---

### PUT /subjects/{subject_id}

Update subject details (Admin/Professor only).

**Required:** JWT Authentication (Admin or subject's Professor)

**Path Parameters:**
```
subject_id: INF001
```

**Request Body:**
```json
{
  "name": "Algorithms and Data Structures",
  "description": "Updated course description",
  "guide": "# Teaching Guide\n..."
}
```

**Response (200):**
```json
{
  "_id": "INF001",
  "name": "Algorithms and Data Structures",
  "description": "Updated course description",
  "professor_id": "prof_ana",
  "guide": "# Teaching Guide\n..."
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions
- `404`: Subject not found
- `422`: Invalid request body

---

### DELETE /subjects/{subject_id}

Delete a subject (Admin only).

**Required:** JWT Authentication (Admin role)

**Path Parameters:**
```
subject_id: INF001
```

**Response (204):** No content

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions
- `404`: Subject not found

---

### GET /subjects/enrolled

List subjects the authenticated student is enrolled in.

**Required:** JWT Authentication

**Response (200):**
```json
[
  {
    "_id": "INF001",
    "name": "Algorithms",
    "description": "Course on algorithm design",
    "professor_id": "prof_ana",
    "guide": "# Teaching Guide\n..."
  },
  {
    "_id": "MAT002",
    "name": "Linear Algebra",
    "description": "Vector spaces and matrices",
    "professor_id": "prof_juan",
    "guide": "# Teaching Guide\n..."
  }
]
```

**Errors:**
- `401`: Not authenticated

---

### POST /subjects/{subject_id}/enroll

Enroll authenticated student in a subject.

**Required:** JWT Authentication (Student role)

**Path Parameters:**
```
subject_id: INF001
```

**Response (200):**
```json
{
  "message": "Successfully enrolled in INF001",
  "subject": {
    "_id": "INF001",
    "name": "Algorithms",
    "professor_id": "prof_ana"
  }
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Student already enrolled
- `404`: Subject not found
- `400`: Student role required

---

## Chat Endpoints

### POST /chat

Send a message to the chatbot service.

**Required:** JWT Authentication

**Request Body:**
```json
{
  "id": "session-uuid-123",
  "asignatura": "INF001",
  "content": "What is the time complexity of quicksort?",
  "messages": [
    {
      "role": "user",
      "content": "Previous message..."
    },
    {
      "role": "assistant",
      "content": "Previous response..."
    }
  ]
}
```

**Response (200):** 
Depends on the chatbot service response. Typically:
```json
{
  "response": "The average time complexity of quicksort is O(n log n)...",
  "session_id": "session-uuid-123",
  "asignatura": "INF001"
}
```

**Notes:**
- Session is auto-created if it doesn't exist
- Session ownership is validated
- Subject enrollment is validated for students
- Request is proxied to chatbot service
- Timeout: 120 seconds

**Errors:**
- `401`: Not authenticated
- `403`: Not enrolled in subject or session doesn't belong to user
- `422`: Missing session ID
- `503`: Chatbot service unavailable
- `504`: Request timeout

---

## Sessions Endpoints

### GET /sessions

List user's chat sessions.

**Required:** JWT Authentication

**Query Parameters:**
```
subject: INF001 (optional)
limit: 20 (optional)
skip: 0 (optional)
```

**Response (200):**
```json
[
  {
    "_id": "session-uuid-123",
    "title": "Questions about algorithms",
    "subject": "INF001",
    "created_at": "2024-01-15T10:30:00Z",
    "last_active": "2024-01-15T11:45:00Z",
    "message_count": 5
  },
  {
    "_id": "session-uuid-456",
    "title": "Linear algebra basics",
    "subject": "MAT002",
    "created_at": "2024-01-14T14:20:00Z",
    "last_active": "2024-01-14T14:35:00Z",
    "message_count": 3
  }
]
```

**Errors:**
- `401`: Not authenticated

---

### GET /sessions/{session_id}

Get detailed session information including chat history.

**Required:** JWT Authentication

**Path Parameters:**
```
session_id: session-uuid-123
```

**Response (200):**
```json
{
  "_id": "session-uuid-123",
  "user_id": "gabriel",
  "title": "Questions about algorithms",
  "subject": "INF001",
  "created_at": "2024-01-15T10:30:00Z",
  "last_active": "2024-01-15T11:45:00Z",
  "messages": [
    {
      "role": "user",
      "content": "What is quicksort?"
    },
    {
      "role": "assistant",
      "content": "Quicksort is a divide-and-conquer sorting algorithm..."
    }
  ]
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Session doesn't belong to user
- `404`: Session not found

---

### DELETE /sessions/{session_id}

Delete a chat session.

**Required:** JWT Authentication

**Path Parameters:**
```
session_id: session-uuid-123
```

**Response (204):** No content

**Errors:**
- `401`: Not authenticated
- `403`: Session doesn't belong to user
- `404`: Session not found

---

### POST /sessions/{session_id}/resume_chat

Resume a test session with user's answer.

**Required:** JWT Authentication

**Path Parameters:**
```
session_id: session-uuid-123
```

**Request Body:**
```json
{
  "answer": "The answer is option B",
  "current_question_index": 2
}
```

**Response (200):**
Depends on test progression. Typically returns next question or test results.

**Errors:**
- `401`: Not authenticated
- `403`: Session doesn't belong to user
- `404`: Session not found
- `400`: Invalid answer format

---

## Professor Endpoints

### GET /professor/students

List all students (enrolled in professor's subjects).

**Required:** JWT Authentication (Professor role)

**Query Parameters:**
```
subject_id: INF001 (optional)
limit: 20 (optional)
skip: 0 (optional)
```

**Response (200):**
```json
[
  {
    "username": "gabriel",
    "full_name": "Gabriel Francisco",
    "email": "gabriel@example.com",
    "enrolled_subjects": ["INF001", "MAT002"]
  },
  {
    "username": "maria",
    "full_name": "Maria García",
    "email": "maria@example.com",
    "enrolled_subjects": ["INF001"]
  }
]
```

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions (not professor)

---

### GET /professor/subjects/{subject_id}/analytics

Get analytics and statistics for a subject.

**Required:** JWT Authentication (Professor teaching this subject or Admin)

**Path Parameters:**
```
subject_id: INF001
```

**Response (200):**
```json
{
  "subject_id": "INF001",
  "name": "Algorithms",
  "total_students": 45,
  "active_students": 32,
  "average_test_score": 78.5,
  "student_progress": [
    {
      "username": "gabriel",
      "test_count": 5,
      "average_score": 82,
      "last_activity": "2024-01-15T11:45:00Z"
    },
    {
      "username": "maria",
      "test_count": 3,
      "average_score": 75,
      "last_activity": "2024-01-14T10:20:00Z"
    }
  ]
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Not this subject's professor
- `404`: Subject not found

---

## Admin Endpoints

### GET /admin/users

List all system users.

**Required:** JWT Authentication (Admin role)

**Query Parameters:**
```
role: STUDENT (optional)
limit: 50 (optional)
skip: 0 (optional)
```

**Response (200):**
```json
[
  {
    "username": "gabriel",
    "email": "gabriel@example.com",
    "full_name": "Gabriel Francisco",
    "role": "STUDENT",
    "subjects": ["INF001", "MAT002"],
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "username": "prof_ana",
    "email": "ana@example.com",
    "full_name": "Ana García",
    "role": "PROFESSOR",
    "subjects": ["INF001"],
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions (not admin)

---

### POST /admin/users/{username}/role

Change a user's role.

**Required:** JWT Authentication (Admin role)

**Path Parameters:**
```
username: gabriel
```

**Request Body:**
```json
{
  "role": "PROFESSOR"
}
```

**Response (200):**
```json
{
  "username": "gabriel",
  "role": "PROFESSOR",
  "message": "User role updated"
}
```

**Errors:**
- `401`: Not authenticated
- `403`: Insufficient permissions
- `404`: User not found
- `400`: Invalid role

---

## System Endpoints

### GET /health

Health check endpoint.

**Response (200):**
```json
{
  "status": "ok"
}
```

No authentication required. Always available.

---

### GET /system/info

Get system information including LLM configuration.

**Response (200):**
```json
{
  "version": "0.1.0",
  "llm_provider": "gemini",
  "llm_model": "gemini-1.5-pro",
  "status": "ok"
}
```

**Notes:**
- Proxies to chatbot service `/system/info` endpoint
- Returns fallback if chatbot unavailable

No authentication required.

---

### GET /metrics

Prometheus metrics endpoint.

**Response (200):** Prometheus format metrics

Includes:
- HTTP request counts
- Request latency distribution
- HTTP status code distribution

No authentication required.

---

## Error Responses

All errors follow this format:

**400 Bad Request:**
```json
{
  "detail": "Error description"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Not authorized to access this resource"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Chatbot service unavailable: [error details]"
}
```

---

## Rate Limiting

Currently not implemented. Consider adding for production:
- Auth endpoints: 5 requests per minute per IP
- General endpoints: 60 requests per minute per user
- Chat endpoint: 10 requests per minute per user

---

## CORS

The backend allows requests from:
- `http://localhost:5173` (Vite development server)
- `http://localhost:3000` (Production container)

Cross-Origin-Resource-Sharing is enabled for:
- All HTTP methods
- All headers
- Credentials (cookies, auth headers)

---

## Using with cURL

**Login:**
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=gabriel&password=secure_password_123"
```

**Get Profile:**
```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

**Send Chat Message:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "session-uuid",
    "asignatura": "INF001",
    "content": "What is an algorithm?"
  }'
```

---

## Using with Python

```python
import httpx

# Login
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8000/token",
        data={"username": "gabriel", "password": "password"}
    )
    token = response.json()["access_token"]

# Get profile
    response = await client.get(
        "http://localhost:8000/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    user = response.json()
```

---

## Using with JavaScript/Fetch

```javascript
// Login
const response = await fetch("http://localhost:8000/token", {
  method: "POST",
  headers: {"Content-Type": "application/x-www-form-urlencoded"},
  body: "username=gabriel&password=password"
});
const {access_token} = await response.json();

// Get profile
const userResponse = await fetch("http://localhost:8000/users/me", {
  headers: {"Authorization": `Bearer ${access_token}`}
});
const user = await userResponse.json();
```

---

## Interactive Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide interactive API exploration and testing.
