---
layout: default
title: "Use TanStack Query for Data Fetching"
date: 2025-11-24
parent: Architecture Decision Records
nav_order: 23
---

# ADR 0023 — Use TanStack Query for Data Fetching

## Status

Accepted

## Context

The frontend needs to fetch data from the backend API (chat history, user profile, dashboard stats). Managing server state (loading, error, success, caching, re-fetching) manually with `useEffect` and `useState` is error-prone and leads to boilerplate code. We need a robust solution for asynchronous state management.

## Decision

We will use **TanStack Query (React Query)** for data fetching and server state management.

## Consequences

- **Pros:**
  - **Boilerplate Reduction:** Eliminates the need for manual loading/error state tracking.
  - **Caching:** Automatic caching and background re-fetching (stale-while-revalidate).
  - **UX:** improved user experience with optimistic updates and window focus refetching.
  - **DevTools:** Excellent developer tools for debugging queries.

- **Cons / Trade-offs:**
  - **Complexity:** Adds a new concept/abstraction to learn.
  - **Bundle Size:** Adds a small amount to the bundle (negligible compared to the benefits).

## Alternatives considered

- **SWR:** A lightweight alternative by Vercel. Good, but TanStack Query offers more advanced features (mutations, infinite queries) that might be needed.
- **Redux Toolkit Query (RTK Query):** Powerful, but requires using Redux, which we are avoiding to keep the state management simple.
- **Axios + useEffect:** The manual approach. Rejected due to complexity in handling race conditions, caching, and deduping requests.

## References

- https://tanstack.com/query/latest
