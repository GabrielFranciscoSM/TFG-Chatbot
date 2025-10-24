---
adr: 0006
title: "Use pytest for testing"
date: 2025-10-24
status: Accepted
parent: Architecture Decision Records
nav_order: 6
---

# ADR 0006 — Use pytest for testing

## Status

Accepted

## Context

We need a test framework that supports unit and integration tests, fixtures, parametrization, and a rich plugin ecosystem for linting, coverage and CI integration.

## Decision

Adopt `pytest` as the primary testing framework for unit and integration tests.

## Consequences

- Pros:
  - Concise tests, powerful fixture system, good ecosystem (pytest-xdist, pytest-cov, plugins).
  - Already present in the repository (existing `pytest.ini` files) and familiar to the team.

- Cons / Trade-offs:
  - Tests need to be written idiomatically (use fixtures and avoid heavy global state) to remain maintainable.

## Alternatives considered

- unittest (stdlib): more verbose and less ergonomic for fixtures/parametrization.
- nose2: less widely used and fewer modern plugins.

## References

- https://docs.pytest.org/
