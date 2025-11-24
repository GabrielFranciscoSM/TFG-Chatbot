---
layout: default
title: "Use React and Vite for Frontend"
date: 2025-11-24
parent: Architecture Decision Records
nav_order: 20
---

# ADR 0020 — Use React and Vite for Frontend

## Status

Accepted

## Context

The project requires a dynamic, responsive, and maintainable user interface for the chatbot and the professor's dashboard. We need a modern frontend framework that offers a rich ecosystem, strong community support, and excellent performance. We also need a build tool that provides a fast development experience.

## Decision

We will use **React** as the UI library and **Vite** as the build tool/bundler.

## Consequences

- **Pros:**
  - **React:** Huge ecosystem, component-based architecture, declarative UI, and widespread industry adoption.
  - **Vite:** Extremely fast server start and Hot Module Replacement (HMR), optimized build process using Rollup, and native ES modules support.
  - **TypeScript Support:** Both have first-class support for TypeScript, which we are using for type safety.

- **Cons / Trade-offs:**
  - React is a library, not a full framework, requiring additional choices for routing and state management (addressed in subsequent ADRs).
  - Vite is newer than Webpack, so some very old legacy plugins might not be compatible (unlikely to affect this new project).

## Alternatives considered

- **Angular:** Provides a full framework experience but has a steeper learning curve and more boilerplate.
- **Vue.js:** A strong contender, but the team (or solo developer) prefers React's ecosystem and JSX syntax.
- **Create React App (CRA):** Deprecated/legacy. Slower builds and less flexible than Vite.
- **Next.js:** Powerful full-stack framework, but deemed overkill for a client-side SPA (Single Page Application) that consumes a separate Python backend.

## References

- https://react.dev/
- https://vitejs.dev/
