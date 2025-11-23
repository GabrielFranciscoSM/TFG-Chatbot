---
layout: default
title: "Custom Authentication Implementation"
date: 2025-11-23
parent: Architecture Decision Records
nav_order: 19
---

# ADR 0019 — Custom Authentication Implementation

## Status

Accepted

## Context

The system requires user management. We could use an external IdP (Identity Provider) like Auth0, Firebase Auth, or Keycloak, or implement it ourselves.

## Decision

We will implement a **Custom Authentication System** using FastAPI and standard cryptography libraries (`passlib`, `bcrypt`).

## Consequences

- Pros:
  - **Total Control**: We need granular control over user data (academic roles, enrolled subjects) which might be complex to map in third-party claims.
  - **Cost and Dependencies**: We avoid licensing costs or dependencies on external cloud services for an academic/local environment.
  - **Deployment Simplicity**: The system remains self-contained (Docker); depending on an external Keycloak would add significant resource overhead (RAM/CPU) unnecessary for the expected user volume.
- Cons / Trade-offs:
  - **Security Responsibility**: We are responsible for securing password storage and handling auth flows correctly (mitigated by using standard libraries like `bcrypt` and `OAuth2PasswordBearer`).
  - **Maintenance**: We have to maintain the login/register logic.

## Alternatives considered

- **Auth0 / Firebase**: discarded to avoid cloud dependencies and potential costs.
- **Keycloak**: discarded due to high resource consumption (Java-based) for a simple academic project.

## References

- https://fastapi.tiangolo.com/tutorial/security/
