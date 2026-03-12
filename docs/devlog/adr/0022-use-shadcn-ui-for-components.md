---
layout: default
title: "Use Shadcn/ui for UI Components"
date: 2025-11-24
parent: Architecture Decision Records
nav_order: 22
---

# ADR 0022 — Use Shadcn/ui for UI Components

## Status

Accepted

## Context

We need a set of accessible, high-quality UI components (buttons, inputs, dialogs, etc.) to build a polished interface quickly. However, we want to avoid the "black box" problem of traditional component libraries where customization is difficult and we depend on an external package's updates. The developer wants to "own the code".

## Decision

We will use **Shadcn/ui** as the component collection.

## Consequences

- **Pros:**
  - **Ownership:** Components are copied into the project's source code, allowing full control and customization.
  - **Accessibility:** Built on top of Radix UI primitives, ensuring WAI-ARIA compliance.
  - **Styling:** Uses Tailwind CSS, integrating perfectly with our styling decision (ADR 0021).
  - **Modern:** Very popular in the React ecosystem, with a clean and professional aesthetic.

- **Cons / Trade-offs:**
  - **Maintenance:** We are responsible for the code of the components once copied. Updates must be applied manually.
  - **Setup:** Requires slightly more initial setup than `npm install @mui/material`.

## Alternatives considered

- **Mantine UI:** Excellent library with many hooks, but it is a dependency (black box) and harder to fully customize the internal DOM structure.
- **Material UI (MUI):** The enterprise standard, but heavy and has a very distinct "Google" look that is hard to override.
- **Chakra UI:** Good developer experience, but relies on runtime CSS-in-JS which has performance costs.

## References

- https://ui.shadcn.com/
- https://www.radix-ui.com/
