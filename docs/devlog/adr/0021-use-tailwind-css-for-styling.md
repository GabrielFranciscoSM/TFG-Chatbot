---
layout: default
title: "Use Tailwind CSS for Styling"
date: 2025-11-24
parent: Architecture Decision Records
nav_order: 21
---

# ADR 0021 — Use Tailwind CSS for Styling

## Status

Accepted

## Context

We need a styling solution that allows for rapid UI development, consistency, and maintainability. Traditional CSS or SASS can lead to large stylesheets and naming conflicts. We want a utility-first approach to build custom designs without leaving the HTML/JSX.

## Decision

We will use **Tailwind CSS** as the styling framework.

## Consequences

- **Pros:**
  - **Speed:** Rapid prototyping by applying utility classes directly in markup.
  - **Consistency:** Enforces a design system (colors, spacing, typography) via configuration.
  - **Bundle Size:** Purges unused styles in production, resulting in very small CSS files.
  - **Modern:** Industry standard for modern React applications.

- **Cons / Trade-offs:**
  - **Learning Curve:** Requires learning the utility class names.
  - **Markup Clutter:** HTML/JSX can become verbose with many class names (mitigated by component extraction).

## Alternatives considered

- **CSS Modules:** Scoped CSS, but requires writing custom CSS files and switching context.
- **Styled Components (CSS-in-JS):** Powerful dynamic styling, but adds runtime overhead and increases bundle size.
- **Bootstrap:** Pre-built components are easy, but harder to customize and can look "generic".

## References

- https://tailwindcss.com/
