---
adr: 0003
title: "Use Docker for containerization in development/CI"
date: 2025-10-24
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 3
---

# ADR 0003 — Use Docker for containerization in development/CI

## Status

Accepted (Supersedes original Podman decision)

## Context

The project requires a reliable container runtime for local development, testing, and CI workflows. Docker is the industry standard with excellent cross-platform support, extensive documentation, and widespread tooling compatibility.

## Decision

Use Docker and Docker Compose as the container runtime for local development and CI workflows.

## Consequences

- Pros:
  - Industry standard with ubiquitous support across platforms (Linux, macOS, Windows).
  - Excellent documentation and community resources.
  - Native support in all major CI systems (GitHub Actions, GitLab CI, etc.).
  - Docker Compose v2 provides robust multi-container orchestration.
  - Wide compatibility with third-party tools and IDE integrations.

- Cons / Trade-offs:
  - Requires Docker daemon running (Docker Desktop on macOS/Windows).
  - Docker Desktop requires license for commercial use in larger organizations.

## Alternatives considered

- Podman: daemonless and rootless by default, good OCI compatibility, but less widespread tooling support and occasional compatibility issues.
- containerd + nerdctl: modern stack but higher setup complexity for contributors.

## Implementation

- Use `docker compose` (v2) commands throughout documentation and scripts.
- Provide `docker-compose.yml` for container orchestration.
- CI pipelines use Docker-based runners.

## References

- https://docs.docker.com/
- https://docs.docker.com/compose/
