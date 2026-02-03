---
adr: 0005
title: "Use Pydantic for data models and validation"
date: 2025-10-24
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 5
---

# ADR 0005 — Use Pydantic for data models and validation

## Status

Accepted

## Context

The codebase passes structured data between API layer, business logic and persistence. We want runtime validation, clear type hints, and easy (de)serialization for JSON and storage.

## Decision

Standardize on Pydantic (v1 or v2 as appropriate) for typed data models, validation and serialization across API payloads, internal DTOs and persistence mapping.

## Consequences

- Pros:
  - Strong runtime validation combined with Python typing improves developer confidence and reduces bugs.
  - Integration with FastAPI (automatic request/response parsing) and compatibility with many libraries.
  - Easy JSON (de)serialization and export to storage-friendly dicts.

- Cons / Trade-offs:
  - Pydantic v2 introduced breaking changes relative to v1; the team must agree on a major version and follow migration guidance.
  - Some runtime overhead for validation (acceptable for typical API workloads).

## Alternatives considered

- dataclasses + manual validation: lighter weight but requires more boilerplate and less runtime safety.
- attrs: flexible and performant, but less direct FastAPI integration than Pydantic.

## References

- https://pydantic-docs.helpmanual.io/
