---
adr: 0002
title: "Use LangChain / LangGraph for orchestration of LLM+tool flows"
date: 2025-10-24
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 2
---

# ADR 0002 — Use LangChain / LangGraph for orchestration of LLM+tool flows

## Status

Accepted

## Context

The project integrates language models, retrieval, prompt templates, and tool orchestration (RAG, chain-of-thought, tool calls). We need a composable orchestration layer that simplifies building prompt flows, caching, and connecting retrievers and tools.

## Decision

Adopt LangChain (and where appropriate, LangGraph or similar graph-based orchestrators) as the primary orchestration library for connecting LLMs, retrievers, and tools.

## Consequences

- Pros:
  - Rich set of primitives for building chains, agents, retrievers, and memory components.
  - Many integrations (vectorstores, embeddings, toolkits) that reduce glue code.
  - Actively developed and widely used pattern in the LLM ecosystem.

- Cons / Trade-offs:
  - Library-level churn: LangChain evolves quickly, which may require occasional refactors on major version changes.
  - Potential for over-abstraction; care needed to keep orchestrations transparent and debuggable.

## Alternatives considered

- Build a custom orchestration library: offers full control but requires significant implementation and maintenance effort.
- Use minimal glue code (requests + custom wrappers): simpler but duplicates many features (caching, prompt templates, chains).

## Notes

Where a graph-oriented approach (LangGraph) makes flows clearer or reusable, prefer that pattern; otherwise use LangChain core constructs.

## References

- https://langchain.com/
- LangGraph (where applicable)
