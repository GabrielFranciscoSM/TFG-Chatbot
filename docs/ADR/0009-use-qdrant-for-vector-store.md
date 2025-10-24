---
adr: 0009
title: "Use Qdrant for vector storage and similarity search"
date: 2025-10-24
status: Accepted
parent: Architecture Decision Records
nav_order: 9
---

# ADR 0009 — Use Qdrant for vector storage and similarity search

## Status

Accepted

## Context

The project implements a Retrieval-Augmented Generation (RAG) pipeline that requires:

- indexing document embeddings into a vector store,
- efficient similarity search (nearest neighbours) with payload/metadata filtering,
- persistence, snapshots and reasonable operational ergonomics for development and production.

The repository already contains a concrete implementation that uses the `qdrant_client` and a `VectorStoreService` under `rag_service/embeddings/store.py`.

## Decision

We will use Qdrant as the primary vector database for storing embeddings and performing similarity search.

Qdrant will be the default vector store used by the project's ingestion, indexing and search components. Code will depend on a small adapter/service layer (already present) so the storage backend can be replaced later if needed.

## Consequences

- Pros
  - Purpose-built vector DB with efficient similarity search and vector indexes.
  - Rich payload support and filtering capabilities (useful for metadata-based retrieval and multi-tenant use cases).
  - Offers persistence, backups and management tooling; can run locally (single node) or as a managed/clustered deployment.
  - Strong Python client (`qdrant-client`) and reasonable developer ergonomics; integrates nicely with LangChain-style workflows.

- Cons / Trade-offs
  - Operational overhead compared to purely local embeddings + file-based indexes (e.g., Chroma ephemeral stores or local FAISS indexes).
  - Hosting cost and complexity if scaled to clustered deployments.
  - Migration effort if switching to other vector stores (schema and payload mapping required).

## Alternatives considered

- ChromaDB: simple to embed in-app and easy for local dev — but historically less feature-rich for filtering and clustering at scale.
- Milvus: production-grade vector DB with scale and performance — more operational complexity.
- FAISS (local): high-performance nearest-neighbour search offline or embedded, but lacks built-in persistence/metadata filtering and networked serving.
- Pinecone (managed): fully managed and scalable but is a hosted service (costs and data egress/privacy considerations).

## Operational notes and recommendations

- Local development: support running a single-node Qdrant instance via `docker-compose` / Podman Compose. Provide example compose service (port, volume mount for persistence) in repository docs or CI scripts.
- Resource sizing: embedding dimensionality and collection size drive memory and CPU/GPU needs. Benchmark with realistic datasets and set appropriate machine sizes for production.
- Backups and snapshots: schedule regular snapshots and/or export collections for disaster recovery. Document backup/restore commands and location of persisted data volumes.
- Metrics & monitoring: collect latency, QPS, collection size, index build times and resource usage. Export Prometheus metrics where available and add alerts for high error rates or resource exhaustion.
- Security & networking: restrict Qdrant access to internal network; enable TLS and authentication for production deployments if available.

## Migration path

- Keep the `VectorStoreService` adapter small and well-documented. When a migration is required, implement the new backend behind the same adapter interface and provide a migration script to copy/snapshot data (e.g., export vectors and metadata, reindex into the new system).

## References

- Qdrant: https://qdrant.tech/
- qdrant-client: https://github.com/qdrant/qdrant_client
