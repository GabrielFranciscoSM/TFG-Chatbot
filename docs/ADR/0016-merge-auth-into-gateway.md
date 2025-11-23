---
layout: default
title: "Merge Auth Service into Gateway"
date: 2025-11-23
parent: Architecture Decision Records
nav_order: 16
---

# ADR 0016 — Merge Auth Service into Gateway

## Status

Accepted

## Context

Initially, a granular microservices architecture was proposed, separating the authentication logic (`auth_service`) from the entry point (`gateway` or `backend`).
However, during implementation, it was observed that:
1. There was high dependency and code duplication (user models, token validation, shared secrets) between both services.
2. Network latency increased unnecessarily for simple validation operations.
3. The complexity of deployment and orchestration (Docker) did not outweigh the benefits of separation at this stage of the project.

## Decision

We decided to **merge the authentication service into the backend service (Gateway)**.

The `backend` service is now responsible for:
- Request routing.
- User management (Registration, Login).
- Issuance and validation of JWT tokens.
- Orchestration of calls to the AI service (`chatbot`).

The `chatbot` service remains independent to isolate the heavy inference load and LangChain logic.

## Consequences

- Pros:
  - Simplified deployment (one less container).
  - Elimination of internal HTTP calls for auth validation.
  - More cohesive code that is easier to debug.
- Cons / Trade-offs:
  - The backend becomes more monolithic.
  - If the authentication load grows disproportionately, it could affect routing performance (though unlikely in the current scope).

## Alternatives considered

- Keeping `auth_service` separate: discarded due to unnecessary complexity and latency for the current scale.
- Using an external Identity Provider (Auth0/Keycloak): discarded to keep the project self-contained and avoid external dependencies/costs (see ADR 0018).

## References

- https://microservices.io/patterns/apigateway.html
