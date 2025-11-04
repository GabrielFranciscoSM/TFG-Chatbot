---
adr: 0011
title: "Use uv for virtual environments and dependency management"
date: 2025-10-29
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 11
---

# ADR 0011 — Use uv for virtual environments and dependency management

## Status

Accepted

## Context

The project needs a reproducible, easy-to-use environment and dependency management approach for local development, CI, and deployments. Historically the codebase has used a mix of tools (system Python + `venv` + `pip`, occasionally `pip-tools` and `requirements.txt`), which adds cognitive overhead for contributors and creates occasional inconsistencies between developer machines and CI.

We want a single, lightweight tool that creates per-project virtual environments, pins dependencies with a lockfile, produces deterministic installs, and integrates cleanly with CI and container builds.

## Decision

Standardize on `uv` as the team's primary tool for managing virtual environments and project dependencies.

The project will use `uv` for:

- Creating and activating per-project virtual environments.
- Declaring direct dependencies in a project-level manifest (e.g., `pyproject.toml` or `uv`'s own spec if applicable).
- Producing and committing a lockfile to ensure reproducible installs in CI and developer machines.
- Installing dependencies in CI and local development via `uv install` (or equivalent `uv` commands).

Developer onboarding documentation will include the minimal `uv` steps to create the environment, install dependencies and run tests. CI configs will be updated to use `uv` to install dependencies from the committed lockfile.

## Consequences

- Pros:
  - Single, consistent workflow for creating environments and installing dependencies reduces onboarding friction.
  - Lockfiles enable deterministic installs in CI and reproducible developer setups.
  - Per-project virtual environments avoid contaminating global Python and reduce "works-on-my-machine" issues.
  - Simpler developer commands (one tool) reduce cognitive load and accidental mixing of tools.

- Cons / Trade-offs:
  - Team members must install and learn another tool (`uv`), adding a small initial onboarding cost.
  - If `uv` behaves differently from other popular tools, third-party docs or examples may need translation.
  - Lockfile merging conflicts can occur when multiple branches change dependencies; process and tooling are required to resolve them safely.

## Alternatives considered

- Pure `venv` + `pip` + `requirements.txt`:
  - Pros: universally available, minimal dependencies on external tooling.
  - Cons: no standard lockfile format by default, manual pinning is error-prone and less reproducible.

- `pip-tools` (pip-compile / pip-sync):
  - Pros: produces a pinned requirements file and works with `venv` and `pip`.
  - Cons: two-step workflow and less modern developer ergonomics compared to newer tools.

- `Poetry`:
  - Pros: mature dependency manager with manifest + lockfile and built-in venv handling.
  - Cons: larger feature surface and breakout differences in commands; some projects prefer a lighter-weight tool.

- `PDM`:
  - Pros: modern, PEP 582 and install semantics; works well with `pyproject.toml`.
  - Cons: different conventions; team familiarity may be lower depending on contributors.

## Operational notes and recommendations

- Onboarding: add a short section to `README.md` and developer docs with the exact `uv` install steps and the basic commands to create an environment and install dependencies.
- CI: update relevant CI workflows to install `uv` and run `uv install --lockfile` (or the equivalent) before running tests/builds.
- Lockfile policy: commit the lockfile to the repository for reproducibility. When upgrading dependencies, update the lockfile in a single merge and include dependency changes as part of PRs.
- Containers: For Docker builds, prefer installing from the lockfile to create deterministic images.
- Dependency updates: Prefer small, reviewed dependency bumps. Use an automated tool (dependabot or equivalent) configured to update the manifest and lockfile together.

## References

- Project consistency and reproducibility best practices.
- `uv` documentation (team-maintained link or upstream docs).

