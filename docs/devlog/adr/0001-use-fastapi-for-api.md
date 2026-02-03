---
layout: default
title: "Use FastAPI for the project API"
date: 2025-10-24
parent: Architecture Decision Records
nav_order: 1
---

# ADR 0001 — Use FastAPI for the project API

## Status

Accepted

## Context

The project needs a modern, fast, and developer-friendly HTTP API framework to expose endpoints (chat, embeddings, admin, health) and integrate model/logic layers. The team values quick iteration, type safety, automatic OpenAPI docs, and async I/O for concurrency.

## Decision

We will use FastAPI as the primary web framework for the project's API layer.

## Consequences

- Pros:
  - Excellent async support and performance for I/O-bound workloads.
  - Automatic generation of OpenAPI and interactive docs (Redoc/Swagger).
  - First-class Pydantic integration for request/response validation and typed models.
  - Large community and ecosystem, many extensions and deployment examples.

- Cons / Trade-offs:
  - Slight learning curve for developers unfamiliar with async/await in Python.
  - If parts of the codebase need heavy CPU-bound work, additional worker processes or offloading strategies will be required.

## Alternatives considered

- Flask (with Flask-RESTX): simpler but lacks built-in async, slower to get typed request/response validation and OpenAPI generation.
- Django REST Framework: heavier, more batteries-included — too large for a lightweight service primarily serving model/AI endpoints.

## References

- https://fastapi.tiangolo.com/
- Pydantic docs
