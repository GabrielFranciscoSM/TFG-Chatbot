---
layout: default
title: "ADR 0010 — Use MongoDB to store 'guía docente' JSON for the agent tool"
date: 2025-10-25
parent: Architecture Decision Records
nav_order: 10
---

# ADR 0010 — Use MongoDB to store 'guía docente' JSON for the agent tool

## Status

Accepted

## Context

The project includes an agent tool that scrapes or ingests "guía docente" documents and produces structured JSON output. This JSON is semi-structured: the top-level shape is stable (metadata, sections, textual fields), but fields and nested structures vary between guides and across institutions.

We need a persistence layer that supports:

- Storing and retrieving full JSON documents produced by the agent.
- Efficient querying by metadata (e.g., course code, year, author) and by some nested fields.
- Flexible schema to accommodate variations without frequent migrations.
- Reasonable read/write performance for agent workflows and downstream API access.
- Operational simplicity for development and deployment (can run locally in dev and in containerized infra in production).

## Decision

We will use MongoDB as the primary persistent store for the "guía docente" JSON documents.

Full documents (the agent output) will be stored as BSON/JSON documents in a dedicated collection. Important metadata fields will be stored as top-level indexed fields to enable fast lookups. We will keep the original JSON intact for reproducibility and add a small metadata wrapper (ingest timestamp, source, version, checksum).

## Rationale

- Document model: MongoDB's document-oriented storage maps naturally to the agent's JSON output without an object-relational impedance mismatch.
- Schema flexibility: documents can evolve (extra fields, optional sections) without DB schema migrations.
- Querying: MongoDB supports rich queries on nested fields and arrays and provides indexing on nested keys, enabling efficient lookups and filters.
- Ecosystem: mature Python drivers (pymongo, motor for async) and good community support.
- Operational options: can run locally in Docker during development, self-host in production, or use managed services (Atlas) if desired.

## Consequences

Pros:

- Fast development: store and iterate on JSON outputs without mapping to relational schemas.
- Good support for nested queries and indexes on metadata and frequently queried nested fields.
- Simple retention/versioning model by storing full documents with ingest metadata.

Cons / Trade-offs:

- Operational overhead: running and operating MongoDB (backups, monitoring) adds maintenance compared to file-based storage.
- Consistency model: MongoDB is eventually consistent across distributed replicas unless configured differently; design must account for write/replica lag where relevant.
- If complex relational queries across many documents are required later, joins and relational semantics are less convenient than a relational DB.

## Alternatives considered

- PostgreSQL with JSONB
  - Pros: strong ACID guarantees, powerful indexing for JSONB, familiar relational features.
  - Cons: mapping semi-structured data to relational workflows can be more rigid; also requires planning of composite indexes on JSON paths.

- SQLite / filesystem (store JSON files on disk)
  - Pros: extremely simple to operate; no DB server.
  - Cons: poor querying capabilities across many documents, concurrency limits, and harder to scale.

- Vector DB (e.g., Qdrant) for embedding-based retrieval
  - Pros: if semantic search is the main access pattern, a vector DB helps.
  - Cons: non-overlapping concerns — vector DB complements, but does not replace a primary JSON store for canonical documents and metadata queries.

## Migration and data model versioning

We will store a small `schema_version` and `ingest_version` fields in each document. When the agent output format evolves, the application/agent will include an upgrade path that converts older documents as needed or records compatibility info. Full-document backups will be retained before running mass upgrades.

## Operational notes

- Indexes: create indexes on commonly queried metadata (e.g., course_id, academic_year, source) and on any nested fields used frequently by queries.
- Backups: schedule regular backups and include restore testing in CI or runbooks.
- Security: require authentication, use TLS in production, and enforce least-privilege database users for the agent and API.
- Resource planning: monitor disk usage, index sizes, and plan for sharding only if scale requires it.

## Acceptance criteria

1. Agent can persist a sample set of `guía docente` JSON documents and retrieve them by ID.
2. Queries by top-level metadata (course code, year) return results with acceptable latency for API use.
3. Indexed nested-field queries used by the agent or UI perform within acceptable bounds (measured on representative dataset).
4. Backup and restore procedure documented and verified on a small dataset.

## References

- MongoDB official docs: https://docs.mongodb.com/
- Pymongo: https://pymongo.readthedocs.io/

## Authors

Gabriel Francisco
