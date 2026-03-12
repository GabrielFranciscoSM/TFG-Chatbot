# Backend Database Guide

Complete reference for the Backend's MongoDB database schema, collections, and operations.

## Database Overview

The Backend service uses **MongoDB** as its primary data store. MongoDB is a document-oriented NoSQL database that stores data in JSON-like documents.

- **Database Name:** `tfg_chatbot` (configurable)
- **Connection:** MongoDB server (local, Docker, or Atlas)
- **Driver:** PyMongo
- **Collections:** users, sessions, subjects

---

## Database Architecture

```mermaid
flowchart TB
    subgraph MongoDB["MongoDB Server"]
        subgraph DB["tfg_chatbot (database)"]
            users[(users collection)]
            sessions[(sessions collection)]
            subjects[(subjects collection)]
        end
    end
    
    users --> U[User documents]
    sessions --> S[Session documents]
    subjects --> Sub[Subject documents]
```

### Connecting to MongoDB

**From Python:**
```python
from backend.db.mongo import get_db

db = get_db()
users = db["users"]
sessions = db["sessions"]
subjects = db["subjects"]
```

**From MongoDB CLI:**
```bash
# Local
mongosh mongodb://localhost:27017/tfg_chatbot

# Docker
docker exec tfg-mongo mongosh -u root -p rootpassword --authenticationDatabase admin

# Atlas
mongosh "mongodb+srv://user:password@cluster.mongodb.net/tfg_chatbot"
```

**From MongoDB Compass (GUI):**
1. Download MongoDB Compass
2. Connection String: `mongodb://localhost:27017`
3. Connect
4. Select `tfg_chatbot` database

---

## Collections Schema

### 1. users Collection

Stores user account information and profiles.

#### Document Structure

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "username": "gabriel",
  "email": "gabriel@example.com",
  "full_name": "Gabriel Francisco",
  "hashed_password": "$2b$12$R9h7cIPz0giKl4pBM9mryOVGfzDmVxM5e.c2AZ6.d5bFTlwzFcF9u",
  "role": "STUDENT",
  "subjects": ["INF001", "MAT002"],
  "preferences": {
    "theme": "dark",
    "notifications": true,
    "language": "es"
  },
  "created_at": ISODate("2024-01-15T10:30:45.123Z"),
  "updated_at": ISODate("2024-01-16T14:20:10.456Z"),
  "last_login": ISODate("2024-01-16T14:15:00.000Z")
}
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB unique identifier |
| `username` | String | Yes | Username for login (unique) |
| `email` | String | Yes | Email address (unique) |
| `full_name` | String | Yes | User's full name |
| `hashed_password` | String | Yes | bcrypt hashed password |
| `role` | String | Yes | User role: STUDENT, PROFESSOR, ADMIN |
| `subjects` | Array[String] | Yes (empty OK) | List of subject IDs enrolled in/teaching |
| `preferences` | Object | No | User preferences (theme, notifications, etc.) |
| `created_at` | Date | Yes | Account creation timestamp |
| `updated_at` | Date | Yes | Last profile update timestamp |
| `last_login` | Date | No | Last login timestamp |

#### Indexes

**Unique Indexes (ensure uniqueness):**
```javascript
db.users.createIndex({"username": 1}, {unique: true})
db.users.createIndex({"email": 1}, {unique: true})
```

**Query Indexes (speed up lookups):**
```javascript
db.users.createIndex({"role": 1})
db.users.createIndex({"created_at": -1})
```

#### Query Examples

**Find user by username:**
```python
user = db.users.find_one({"username": "gabriel"})
```

**Find all students:**
```python
students = list(db.users.find({"role": "STUDENT"}))
```

**Find users created in last 7 days:**
```python
from datetime import datetime, timedelta
week_ago = datetime.now(UTC) - timedelta(days=7)
users = list(db.users.find({"created_at": {"$gte": week_ago}}))
```

**Update user profile:**
```python
db.users.update_one(
    {"username": "gabriel"},
    {"$set": {
        "full_name": "Gabriel Francisco García",
        "updated_at": datetime.now(UTC)
    }}
)
```

**Enroll student in subject:**
```python
db.users.update_one(
    {"username": "gabriel"},
    {"$addToSet": {"subjects": "INF001"}}  # Add if not present
)
```

---

### 2. sessions Collection

Stores chat session information and metadata.

#### Document Structure

```javascript
{
  "_id": "session-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "gabriel",
  "title": "Questions about algorithms",
  "subject": "INF001",
  "created_at": ISODate("2024-01-15T10:30:45.123Z"),
  "last_active": ISODate("2024-01-15T11:45:30.456Z"),
  "thread_id": "thread-abc123def456",
  "message_count": 5,
  "model_used": "gemini-1.5-pro",
  "is_test_session": false
}
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | String | Yes | Session UUID (client-generated) |
| `user_id` | String | Yes | Username of session owner |
| `title` | String | Yes | Human-readable session title |
| `subject` | String | Yes | Subject ID for the session |
| `created_at` | Date | Yes | Session creation timestamp |
| `last_active` | Date | Yes | Last activity timestamp (updated on each message) |
| `thread_id` | String | No | LangGraph thread ID for checkpointing |
| `message_count` | Int | No | Number of messages in session |
| `model_used` | String | No | LLM model used (for analytics) |
| `is_test_session` | Boolean | No | Whether this is a test session |

#### Indexes

**Query Indexes:**
```javascript
db.sessions.createIndex({"user_id": 1})
db.sessions.createIndex({"user_id": 1, "created_at": -1})
db.sessions.createIndex({"subject": 1})
db.sessions.createIndex({"thread_id": 1})
db.sessions.createIndex({"last_active": -1})
```

**TTL Index (auto-delete old sessions after 90 days):**
```javascript
db.sessions.createIndex(
  {"last_active": 1},
  {expireAfterSeconds: 7776000}  // 90 days
)
```

#### Query Examples

**Get user's sessions:**
```python
sessions = list(db.sessions.find({"user_id": "gabriel"}).sort("last_active", -1))
```

**Get recent sessions for a subject:**
```python
sessions = list(db.sessions.find({
    "subject": "INF001",
    "last_active": {"$gte": week_ago}
}).sort("last_active", -1))
```

**Update session after message:**
```python
from datetime import datetime, UTC

db.sessions.update_one(
    {"_id": session_id},
    {"$set": {
        "last_active": datetime.now(UTC),
        "title": "New title"
    },
    "$inc": {"message_count": 1}}
)
```

**Find test sessions:**
```python
test_sessions = list(db.sessions.find({"is_test_session": True}))
```

---

### 3. subjects Collection

Stores academic subject information.

#### Document Structure

```javascript
{
  "_id": "INF001",
  "name": "Algorithms",
  "description": "Course on algorithm design and analysis",
  "professor_id": "prof_ana",
  "students": ["gabriel", "maria", "juan"],
  "guide": "# Teaching Guide\n## Topics\n...",
  "guide_url": "https://ugr.es/guia/INF001",
  "credits": 6,
  "semester": 2,
  "academic_year": "2023-2024",
  "created_at": ISODate("2024-01-01T00:00:00.000Z"),
  "updated_at": ISODate("2024-01-15T10:30:00.000Z")
}
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | String | Yes | Subject code (unique) |
| `name` | String | Yes | Subject name |
| `description` | String | Yes | Subject description |
| `professor_id` | String | Yes | Username of teaching professor |
| `students` | Array[String] | Yes (empty OK) | List of enrolled student usernames |
| `guide` | String | No | Teaching guide content (markdown) |
| `guide_url` | String | No | External URL to official guide |
| `credits` | Int | No | ECTS credits |
| `semester` | Int | No | Which semester (1-8) |
| `academic_year` | String | No | Academic year (e.g., "2023-2024") |
| `created_at` | Date | Yes | Subject creation timestamp |
| `updated_at` | Date | Yes | Last update timestamp |

#### Indexes

**Query Indexes:**
```javascript
db.subjects.createIndex({"professor_id": 1})
db.subjects.createIndex({"students": 1})
db.subjects.createIndex({"semester": 1})
```

#### Query Examples

**Get all subjects for a professor:**
```python
subjects = list(db.subjects.find({"professor_id": "prof_ana"}))
```

**Get all subjects a student is enrolled in:**
```python
subjects = list(db.subjects.find({"students": "gabriel"}))
```

**Find subjects by semester:**
```python
subjects = list(db.subjects.find({"semester": 2}))
```

**Enroll student in subject:**
```python
db.subjects.update_one(
    {"_id": "INF001"},
    {"$addToSet": {"students": "gabriel"}}  # Add if not present
)
```

**Update teaching guide:**
```python
db.subjects.update_one(
    {"_id": "INF001"},
    {"$set": {
        "guide": "# Updated Guide\n...",
        "updated_at": datetime.now(UTC)
    }}
)
```

---

## Database Operations

### Creating Collections

Collections are created automatically on first insert. To create explicitly:

```python
from backend.db.mongo import get_db

db = get_db()
db.create_collection("users")
db.create_collection("sessions")
db.create_collection("subjects")
```

### Setting Up Indexes

**Run once during deployment:**

```python
def setup_indexes(db):
    # users collection
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    db.users.create_index([("created_at", -1)])
    
    # sessions collection
    db.sessions.create_index("user_id")
    db.sessions.create_index([("user_id", 1), ("created_at", -1)])
    db.sessions.create_index("subject")
    db.sessions.create_index("thread_id")
    # TTL index: auto-delete after 90 days
    db.sessions.create_index(
        "last_active",
        expireAfterSeconds=7776000
    )
    
    # subjects collection
    db.subjects.create_index("professor_id")
    db.subjects.create_index("students")
```

### Dropping Collections

```python
db.users.drop()
db.sessions.drop()
db.subjects.drop()
```

### Clearing Collections (Keep Indexes)

```python
db.users.delete_many({})
db.sessions.delete_many({})
db.subjects.delete_many({})
```

---

## Data Backup & Recovery

### Backup

**Using mongodump:**
```bash
# Backup entire database
mongodump --uri "mongodb://localhost:27017" --db tfg_chatbot --out ./backup

# Docker backup
docker exec tfg-mongo mongodump --db tfg_chatbot --out /backup
docker cp tfg-mongo:/backup ./local-backup
```

**Using MongoDB Compass:**
1. Right-click collection → Export collection
2. Select format (JSON, CSV)
3. Save to file

### Restore

**Using mongorestore:**
```bash
# Restore from backup
mongorestore --uri "mongodb://localhost:27017" ./backup

# Docker restore
docker cp ./local-backup tfg-mongo:/backup
docker exec tfg-mongo mongorestore /backup --db tfg_chatbot
```

---

## Data Validation

### Pydantic Models (Application Layer)

Validation happens in application before database write:

```python
from pydantic import EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., max_length=100)
    role: UserRole = UserRole.STUDENT
```

### MongoDB Schema Validation (Optional)

Define schema at database level:

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email", "hashed_password", "role"],
      properties: {
        username: { bsonType: "string" },
        email: { bsonType: "string" },
        hashed_password: { bsonType: "string" },
        role: { enum: ["STUDENT", "PROFESSOR", "ADMIN"] },
        subjects: { bsonType: "array", items: { bsonType: "string" } }
      }
    }
  }
})
```

---

## Query Patterns

### Aggregation Pipeline

Complex queries using aggregation:

```python
# Students per subject
pipeline = [
    {"$match": {"_id": "INF001"}},
    {"$project": {
        "student_count": {"$size": "$students"}
    }}
]
result = list(db.subjects.aggregate(pipeline))
```

### Text Search

Full-text search on subject guide:

```javascript
// Create text index
db.subjects.createIndex({"guide": "text", "name": "text"})

// Search
db.subjects.find({
  $text: {$search: "algorithms"}
})
```

---

## Database Performance

### Monitoring Queries

```python
# Enable profiling
db.set_profiling_level(1)  # 0=off, 1=slow queries, 2=all

# View profiling data
db.system.profile.find().pretty()

# Get query stats
db.subjects.aggregate([
    {$collStats: {latencyStats: {}}}
])
```

### Index Analysis

```javascript
// Get index info
db.users.getIndexes()

// Get index stats
db.users.aggregate([
  {$indexStats: {}}
])
```

### Connection Pooling

Configure in connection string:

```
mongodb://localhost:27017/?maxPoolSize=50&minPoolSize=10
```

---

## Data Migration

### Adding a New Field

```python
# Add field to all documents
db.users.update_many(
    {},
    {"$set": {"new_field": default_value}}
)
```

### Renaming a Field

```python
# Rename across collection
db.users.update_many(
    {},
    {"$rename": {"old_field": "new_field"}}
)
```

### Changing Data Type

```python
# Convert string to array
db.subjects.update_many(
    {"categories": {"$type": "string"}},
    [{"$set": {"categories": ["$categories"]}}]
)
```

---

## Common Issues

### Issue: "Duplicate Key Error"

**Cause:** Unique index violation

**Solution:**
```python
# Check existing unique indexes
db.users.getIndexes()

# Remove duplicate
db.users.delete_one({"_id": duplicate_id})
```

### Issue: "Document Too Large"

**Cause:** Document exceeds 16MB limit

**Solution:**
- Move large fields to separate collection
- Store file references instead of content
- Archive old sessions

### Issue: "Connection Refused"

**Cause:** MongoDB not running

**Solution:**
```bash
# Start MongoDB
docker compose up mongo

# Check connection
mongosh --eval "db.adminCommand('ping')"
```

### Issue: Slow Queries

**Cause:** Missing indexes

**Solution:**
```javascript
// Check query plan
db.users.find({"role": "STUDENT"}).explain("executionStats")

// Create index if COLLSCAN shown
db.users.createIndex({"role": 1})
```

---

## Best Practices

1. **Always Create Indexes**
   - Index fields used in queries
   - Compound indexes for multi-field queries
   - TTL indexes for cleanup

2. **Use Unique Indexes**
   - username, email in users collection
   - Prevents duplicates at database level

3. **Backup Regularly**
   - Daily backups for production
   - Test restore procedures
   - Store backups offsite

4. **Monitor Query Performance**
   - Enable profiling in production
   - Alert on slow queries (>100ms)
   - Regularly optimize indexes

5. **Validate Data**
   - Use Pydantic models
   - Schema validation at DB level
   - Check integrity regularly

6. **Archive Old Data**
   - TTL indexes for sessions (90 days)
   - Archive old sessions to separate DB
   - Keep backups of archived data

7. **Handle Errors Gracefully**
   - Catch connection errors
   - Retry logic for transient failures
   - Log all database errors

---

## Related Documentation

- [Configuration](./configuration.md) - MongoDB connection settings
- [Development](./development.md) - Testing with MongoDB
- [Architecture](./architecture.md) - Data model overview
