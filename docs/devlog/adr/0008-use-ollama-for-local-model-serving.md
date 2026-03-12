---
adr: 0008
title: "Use Ollama for local model serving embeddings model (RAG)"
date: 2025-10-24
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 8
---

# ADR 0008 — Use Ollama for local embedding model serving (RAG)

## Status

Accepted

## Context

This project uses a Retrieval-Augmented Generation (RAG) pipeline that depends on producing vector embeddings for documents and queries, indexing them in a vector store, and performing similarity search to retrieve relevant context for downstream LLM prompts.

For day-to-day development, reproducible local testing, and privacy-sensitive work, the team wants a straightforward way to run embedding-capable models locally and expose a stable API for the ingestion and query pipelines.

Ollama provides an easy-to-install local model-serving runtime (CLI + HTTP interface) that can host embedding-capable models and present a consistent endpoint for generating embeddings during development and small experiments.

## Decision

Recommend using Ollama as the default local-serving runtime for embedding models used by the RAG pipeline during development and testing. Ollama will be used to:

- Host local embedding-capable model checkpoints used during development.
- Provide a consistent HTTP/CLI endpoint for the ingestion process and local integration tests.

Production embedding serving (for scale, throughput or managed SLAs) should use dedicated runtimes or hosted embedding services (vLLM where applicable, a managed cloud embedding API, or a dedicated embedding microservice backed by GPUs/accelerators).

## Consequences

- Pros:
  - Low friction for developers: quick local setup and consistent API for embeddings.
  - Reproducible local runs for ingestion tests and RAG experiments without relying on external APIs.
  - Helps preserve data privacy by avoiding sending sensitive documents to third-party embedding services during development.

- Cons / Trade-offs:
  - Ollama is primarily intended as a local/dev runtime and is not a full production embedding service for high-throughput workloads.
  - Not all embedding model checkpoints may be readily available or supported; some models may require conversion or packaging.
  - Embedding throughput will depend on local hardware; CI and production should use scaled runtimes when needed.
  - API differences compared to cloud embedding providers may require adapters to keep client code portable.

## Alternatives considered

- Run embedding models directly using Hugging Face Transformers / sentence-transformers locally: offers maximum control but increases setup complexity and environment variability across developers.
- Use cloud embedding APIs (OpenAI, Cohere, Anthropic): scalable and easy to integrate, but adds cost and sends data offsite (privacy/cost trade-offs).
- Use vLLM, Triton, or other high-performance serving stacks for embeddings in production: better throughput and latency but more operational overhead.

## Mitigations / Recommendations

- Add a small `docs/ADR/README.md` (or extend existing docs) with recommended Ollama commands to run the chosen embedding model and example client calls (curl/Python) used by the ingestion pipeline.
- Implement an adapter layer for embedding requests and responses so code can switch between Ollama, cloud APIs, or other local runtimes with minimal changes.
- Provide CI fallbacks: for lightweight CI runners, use a small embedding model or a mocked embedding endpoint to keep tests fast and deterministic.

## References

- https://ollama.ai/
