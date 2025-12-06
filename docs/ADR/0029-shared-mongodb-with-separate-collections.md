---
adr: 0029
title: "Shared MongoDB instance with separate collections per service"
date: 2024-12-06
status: Accepted
parent: Architecture Decision Records
nav_order: 29
---

# ADR 0029 — Shared MongoDB instance with separate collections per service

## Status

Accepted

## Context

In a microservices architecture, the ideal pattern is "database per service" where each service owns its data store completely. This provides:

- Strong encapsulation and autonomy
- Independent scaling
- Technology freedom (different DBs for different services)
- No coupling through shared data

However, for this educational chatbot project (TFG), we have practical constraints:

1. **Resource limitations**: Running multiple MongoDB instances increases infrastructure complexity and cost
2. **Development simplicity**: A single MongoDB simplifies local development and CI/CD
3. **Data volume**: The expected data volume doesn't justify separate instances
4. **Operational overhead**: Managing multiple databases adds complexity without proportional benefit

Currently, two services access MongoDB:
- **backend**: Manages `users` and `sessions` collections (auth and session persistence)
- **chatbot**: Manages `guias` collection (teaching guides) and LangGraph checkpoints

## Decision

Use a **single shared MongoDB instance** with **logically separated collections per service**. Each service owns specific collections and no service directly accesses another service's collections.

### Collection Ownership

| Service | Collections | Purpose |
|---------|-------------|---------|
| backend | `users`, `sessions` | Authentication, user management, chat sessions |
| chatbot | `guias`, `checkpoints` | Teaching guide storage, LangGraph state persistence |

### Rules

1. **No cross-service collection access**: Backend must NOT query `guias`; chatbot must NOT query `users`
2. **Service-to-service communication via API**: If backend needs teaching guide data, it calls chatbot's API
3. **Consistent database name**: Both services use `tfg_chatbot` database (configurable via `DB_NAME`/`MONGO_DB`)
4. **Independent connection management**: Each service manages its own `MongoDBClient` instance

### Configuration

```python
# backend/config.py
db_name: str = "tfg_chatbot"

# chatbot/config.py  
mongo_db: str = "tfg_chatbot"
```

## Consequences

### Positive

- **Simpler infrastructure**: One MongoDB container instead of multiple
- **Easier development**: Single connection string, simpler docker-compose
- **Cost effective**: Appropriate for TFG scope and educational context
- **Clear ownership**: Each service knows exactly which collections it owns

### Negative

- **Shared failure domain**: MongoDB downtime affects all services
- **Coordination required**: Schema changes need awareness across teams
- **Not pure microservices**: Violates strict "database per service" principle
- **Potential for drift**: Risk of accidentally accessing wrong collections

### Mitigations

- Document collection ownership clearly (this ADR)
- Code review to prevent cross-collection access
- Consider collection prefixes in future (e.g., `backend_users`, `chatbot_guias`)
- Add integration tests to verify service isolation

## Alternatives considered

### Option A: Separate MongoDB instances per service

**Pros:**
- Pure microservices pattern
- Complete isolation
- Independent scaling

**Cons:**
- Higher resource usage
- More complex infrastructure
- Overkill for current scale

### Option B: Shared database with no ownership rules (rejected)

**Pros:**
- Maximum simplicity

**Cons:**
- Tight coupling
- No clear boundaries
- Maintenance nightmare

### Option C: Shared instance with separate databases (considered)

**Pros:**
- Logical separation at database level
- Same infrastructure simplicity

**Cons:**
- Still shares failure domain
- Marginal benefit over collection separation
- Slightly more complex connection strings

### Option D: Shared instance with collection ownership (chosen)

**Pros:**
- Simple infrastructure
- Clear logical boundaries
- Appropriate for project scope
- Easy to migrate to Option A later if needed

**Cons:**
- Requires discipline to maintain boundaries
- Not pure microservices

## References

- [ADR 0010: Use MongoDB for guia docente](0010-use-mongodb-for-guia-docente.md)
- [Microservices Database Patterns](https://microservices.io/patterns/data/database-per-service.html)
- [Shared Database Anti-pattern](https://microservices.io/patterns/data/shared-database.html)
