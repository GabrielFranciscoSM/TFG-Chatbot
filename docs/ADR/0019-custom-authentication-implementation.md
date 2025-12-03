---
layout: default
title: "Custom Authentication Implementation"
date: 2025-11-23
parent: Architecture Decision Records
nav_order: 19
---

# ADR 0019 — Custom Authentication Implementation

## Status

Accepted (Updated 2025-12-03)

## Context

The system requires user management. We could use an external IdP (Identity Provider) like Auth0, Firebase Auth, or Keycloak, or implement it ourselves.

## Decision

We will implement a **Custom Authentication System** using FastAPI and `bcrypt` for password hashing.

**Update (2025-12-03)**: Initially we used `passlib` as a wrapper around `bcrypt`, but `passlib` is no longer maintained (last release in 2020) and has compatibility issues with modern `bcrypt` versions (4.1+). We now use `bcrypt` directly.

## Consequences

- Pros:
  - **Total Control**: We need granular control over user data (academic roles, enrolled subjects) which might be complex to map in third-party claims.
  - **Cost and Dependencies**: We avoid licensing costs or dependencies on external cloud services for an academic/local environment.
  - **Deployment Simplicity**: The system remains self-contained (Docker); depending on an external Keycloak would add significant resource overhead (RAM/CPU) unnecessary for the expected user volume.
  - **Direct bcrypt**: Using `bcrypt` directly eliminates the unmaintained `passlib` dependency and ensures compatibility with modern Python versions.
- Cons / Trade-offs:
  - **Security Responsibility**: We are responsible for securing password storage and handling auth flows correctly (mitigated by using `bcrypt` directly and `OAuth2PasswordBearer`).
  - **Maintenance**: We have to maintain the login/register logic.

## Alternatives considered

- **Auth0 / Firebase**: discarded to avoid cloud dependencies and potential costs.
- **Keycloak**: discarded due to high resource consumption (Java-based) for a simple academic project.
- **passlib**: initially used but removed due to abandonment and incompatibility with bcrypt 4.1+.

## References

- https://fastapi.tiangolo.com/tutorial/security/
- https://github.com/pyca/bcrypt
