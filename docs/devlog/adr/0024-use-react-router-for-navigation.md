---
layout: default
title: "Use React Router for Navigation"
date: 2025-11-24
parent: Architecture Decision Records
nav_order: 24
---

# ADR 0024 — Use React Router for Navigation

## Status

Accepted

## Context

The application is a Single Page Application (SPA) with multiple views (Login, Register, Chat, Dashboard). We need a client-side routing library to manage navigation, URL parameters, and protected routes without reloading the page.

## Decision

We will use **React Router DOM** (v6+) for client-side routing.

## Consequences

- **Pros:**
  - **Standard:** The de-facto standard for routing in React applications.
  - **Features:** Supports nested routes, layouts, route guards, and dynamic parameters.
  - **Community:** Vast amount of documentation, tutorials, and community support.

- **Cons / Trade-offs:**
  - **Breaking Changes:** v6 introduced significant changes from v5, which can be confusing when looking at older tutorials.
  - **Type Safety:** While good, it is not as strictly type-safe as newer alternatives like TanStack Router (though sufficient for our needs).

## Alternatives considered

- **TanStack Router:** Offers 100% type-safe routing. Rejected for now to avoid the steeper learning curve and setup complexity, preferring the familiarity of React Router.
- **Wouter:** A minimalist router. Rejected because we need features like nested layouts for the dashboard and robust route guards.

## References

- https://reactrouter.com/
