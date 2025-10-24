---
adr: 0007
title: "Use vLLM for high-throughput, low-latency inference where applicable"
date: 2025-10-24
status: Accepted
parent: Architecture Decision Records
nav_order: 7
---

# ADR 0007 — Use vLLM for high-throughput, low-latency inference where applicable

## Status

Accepted

## Context

The project may run local or hosted LLM inference for chat and batch tasks. For scenarios requiring high throughput and efficient CPU/GPU utilization, we need an inference stack optimized for serving transformer models at scale.

## Decision

Adopt vLLM (where appropriate) for high-throughput or low-latency inference workloads. Use it in production-like environments or benchmarks; for simpler local development or unsupported models, use fallback runtimes (e.g., Hugging Face transformers, Ollama).

## Consequences

- Pros:
  - vLLM provides efficient batching, scheduling and memory management for transformer inference — improved throughput and latency for many workloads.
  - Integrates with common model formats and supports GPU acceleration.

- Cons / Trade-offs:
  - Additional operational complexity compared to single-process runtimes.
  - Model compatibility and integration work may be required for some checkpoints.

## Alternatives considered

- Hugging Face Transformers: simpler single-process inference — easier for development but less efficient at scale.
- Triton/other custom serving stacks: powerful but adds more infra complexity.

## References

- https://github.com/vllm-project/vllm
