---
adr: 0004
title: "Use SQLite for graph memory storage"
date: 2025-10-24
status: Accepted
parent: Architecture Decision Records
nav_order: 4
---

# ADR 0004 — Use SQLite for graph memory storage

## Status

Accepted

## Context

The application maintains a graph-like memory for sessions, nodes and relationships used by retrieval and conversational context. We need a small, portable, low-ops persistent storage that is easy to use locally and in CI for development, testing and for lightweight production use.

## Decision

Use SQLite as the default storage engine for the graph memory (on-disk .db files). Provide adapter layers so the storage implementation can be swapped in future if higher-scale needs arise.

## Consequences

- Pros:
  - Zero-ops and built-in to Python (via sqlite3) — easy to set up and portable across environments.
  - ACID guarantees and adequate performance for small to medium datasets and for development/CI.
  - Easy to snapshot, version and include in local testing workflows.
  - Good integration with langchain

- Cons / Trade-offs:
  - Not horizontally scalable for high-concurrency writes; may require migration to a client-server DB (Postgres) when scale/durability demands increase.
  - Requires careful handling in multi-process or networked deployments; use connection pooling or migrate to a server DB for concurrent write-heavy workloads.

## Alternatives considered

- PostgreSQL: production-grade, scalable and robust, but heavier to manage for local dev and CI.
- In-memory stores (Redis/graph DB): faster but not persistent across restarts and require more infra.

## Mitigations

- Implement an abstraction (storage adapter) for graph memory so migrating to Postgres or a graph DB later is straightforward.
- Document when to migrate (concurrency limits, dataset size, latency requirements).

## References

- https://www.sqlite.org/
