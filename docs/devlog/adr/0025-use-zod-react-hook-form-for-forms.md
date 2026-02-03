---
layout: default
title: "Use Zod and React Hook Form for Forms"
date: 2025-11-24
parent: Architecture Decision Records
nav_order: 25
---

# ADR 0025 — Use Zod and React Hook Form for Forms

## Status

Accepted

## Context

The application involves several complex forms (Login, Registration, Agent Configuration). Managing form state, validation, and error handling manually in React is tedious and can lead to performance issues (excessive re-renders). We need a performant and type-safe way to handle forms.

## Decision

We will use **React Hook Form** for form state management and **Zod** for schema validation.

## Consequences

- **Pros:**
  - **Performance:** React Hook Form uses uncontrolled components to minimize re-renders.
  - **Type Safety:** Zod allows defining schemas that infer TypeScript types, ensuring the form data matches the expected structure.
  - **DX:** Easy integration between the two via `@hookform/resolvers`.
  - **Validation:** Zod provides a powerful and expressive API for validation rules (email, password strength, etc.).

- **Cons / Trade-offs:**
  - **Learning Curve:** Requires understanding the "uncontrolled" component pattern and Zod schema definition.

## Alternatives considered

- **Formik:** The previous standard. Slower performance (re-renders on every keystroke) and larger bundle size compared to RHF.
- **Manual State:** Using `useState` for every field. Rejected due to verbosity and performance concerns.
- **Yup:** A validation library similar to Zod. Rejected because Zod has better TypeScript inference and is the modern standard in the React ecosystem.

## References

- https://react-hook-form.com/
- https://zod.dev/
