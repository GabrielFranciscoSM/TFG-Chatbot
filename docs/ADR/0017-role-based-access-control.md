---
layout: default
title: "Implement Role-Based Access Control (RBAC)"
date: 2025-11-23
parent: Architecture Decision Records
nav_order: 17
---

# ADR 0017 — Implement Role-Based Access Control (RBAC)

## Status

Accepted

## Context

The application has different types of users with distinct needs:
- **Students**: Consumers of the chatbot, limited to their enrolled subjects.
- **Professors**: Managers of subjects and enrollments.
- **Admins**: Global management.

We need a mechanism to restrict access to endpoints and data (specific subject chatbots) based on the user's role and enrollment status.

## Decision

Implement an **RBAC (Role-Based Access Control)** system along with resource-based access control (Subjects).

1. **Roles**: Three hierarchical roles are defined via an Enum: `STUDENT`, `PROFESSOR`, `ADMIN`.
2. **Enrollment**: The user model will include a list of allowed `subjects`.
3. **Validation**:
   - The `/chat` endpoint will verify that the user has the appropriate role OR is enrolled in the requested subject.
   - Management endpoints (`/admin/*`) will require `PROFESSOR` or `ADMIN` roles.
4. **Token**: Roles and subjects will be included in the JWT token claims for fast authorization decisions.

## Consequences

- Pros:
  - Granular security.
  - Prevention of unauthorized access to chatbots of other subjects.
  - Flexibility to add new roles in the future.
- Cons / Trade-offs:
  - Increases the complexity of endpoint logic.
  - Requires state management (enrollments) in the database.

## Alternatives considered

- Simple boolean flags (`is_admin`): discarded as it doesn't scale well for the "Professor" vs "Student" distinction.
- Attribute-Based Access Control (ABAC): considered too complex for the current requirements.

## References

- https://fastapi.tiangolo.com/tutorial/security/
