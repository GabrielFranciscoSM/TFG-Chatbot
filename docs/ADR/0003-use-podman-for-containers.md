---
adr: 0003
title: "Use Podman for containerization in development/CI"
date: 2025-10-24
status: Accepted
parent: Architecture Decision Records
nav_order: 3
---

# ADR 0003 — Use Podman for containerization in development/CI

## Status

Accepted

## Context

The project targets Linux-first development environments. The team prefers a daemonless container engine with good rootless support and tight integration with systemd and OCI standards. Some CI systems used by the team support Podman well and the team wants consistent local/CI workflows.

## Decision

Use Podman as the recommended container runtime for local development and CI workflows (Docker compatibility via Podman CLI and build tools where needed).

## Consequences

- Pros:
  - Daemonless and strong rootless support improves security for local dev.
  - Compatibility with Docker CLI for many workflows; supports OCI images.
  - Good integration with systemd and Podman Compose for dev/test scenarios.

- Cons / Trade-offs:
  - Slight differences vs Docker (on some CI images or 3rd-party tools); may require small onboarding notes for contributors used to Docker Desktop.
  - On non-Linux platforms or certain hosted runners, Podman may require workarounds or fall back to Docker.

## Alternatives considered

- Docker (Docker Engine / Docker Desktop): ubiquitous and widely supported; simpler for contributors on macOS/Windows with Docker Desktop.
- BuildKit/nerdctl + containerd: modern stack but higher setup complexity for local contributors.

## Mitigations

- Add notes to repository README describing the recommended Podman commands and how to fall back to Docker where necessary.
- Provide a `docker-compose` and `podman-compose` compatible configuration where possible (project already includes `docker-compose.yml`).

## References

- https://podman.io/
