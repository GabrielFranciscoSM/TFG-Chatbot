---
layout: default
title: "Use JWT for Stateless Authentication"
date: 2025-11-23
parent: Architecture Decision Records
nav_order: 18
---

# ADR 0018 — Use JWT for Stateless Authentication

## Status

Accepted

## Context

We need a mechanism to maintain user identity between HTTP requests. The choice is typically between Server-side Sessions (stateful) and Signed Tokens (stateless).

## Decision

We will use **JWT (JSON Web Tokens)** for authentication.

## Consequences

- Pros:
  - **Stateless**: We don't need to query the database or a cache (Redis) on every request to validate the session, reducing latency.
  - **Scalability**: Facilitates horizontal scaling of microservices (the Gateway and Chatbot could validate the token independently if they shared the key).
  - **Simplicity**: Easy to consume from mobile clients or SPAs.
- Cons / Trade-offs:
  - **Revocation**: Harder to invalidate tokens immediately (e.g., on logout) without a blacklist or short expiration times.
  - **Payload Size**: Tokens can get large if we store too many claims (like a long list of subjects).

## Alternatives considered

- Server-side Sessions (Cookies + Redis): discarded to avoid adding a Redis dependency and to keep the API stateless.

## References

- https://jwt.io/introduction
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
