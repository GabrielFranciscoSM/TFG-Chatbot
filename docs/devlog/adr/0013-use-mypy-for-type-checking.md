---
adr: 0013
title: "Use Mypy for static type checking"
date: 2025-11-15
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 13
---

# ADR 0013 — Use Mypy for static type checking

## Status

Accepted

## Context

Python's dynamic typing provides flexibility but can lead to runtime errors that could be caught earlier with static analysis. As the project grows in complexity, type-related bugs become more likely and harder to track down.

We need a static type checker that:
- Catches type-related bugs before runtime
- Improves code documentation through type hints
- Provides IDE support for better autocomplete and refactoring
- Integrates well with modern Python development (PEP 484+ type hints)
- Works with the existing codebase and dependencies

## Decision

Adopt **Mypy** as the static type checker for the project.

Mypy will be used to:
- Verify type consistency across the codebase
- Catch potential type-related bugs during development and CI
- Enforce type hints in new code
- Gradually improve type coverage in existing code

Type hints will be added incrementally, starting with new code and critical paths, without requiring a full-codebase rewrite.

## Consequences

- Pros:
  - **Early bug detection**: Catches many classes of bugs before runtime
  - **Better documentation**: Type hints serve as inline documentation of expected types
  - **Improved IDE support**: Better autocomplete, navigation, and refactoring in editors
  - **Refactoring confidence**: Type checker validates that changes maintain type consistency
  - **Industry standard**: Mypy is the most widely used and mature Python type checker
  - **Gradual adoption**: Can be introduced incrementally without requiring all code to be typed immediately

- Cons / Trade-offs:
  - Additional development time to add and maintain type hints
  - Learning curve for team members unfamiliar with Python's type system
  - May require stub files for untyped third-party libraries
  - Can slow down initial development until team is comfortable with typing
  - Some valid Python patterns may be difficult to type correctly

## Alternatives considered

- **Pyright**:
  - Pros: Faster than Mypy, powers Pylance in VS Code, good error messages
  - Cons: More strict by default, smaller community, different configuration approach

- **Pyre**:
  - Pros: Fast, developed by Meta for large codebases
  - Cons: Less widely adopted, more complex setup, less community support

- **No type checking**:
  - Pros: No additional tooling or type annotation overhead
  - Cons: Loses all benefits of static type checking, higher risk of type-related runtime bugs

## Operational notes and recommendations

- **Configuration**: Configure Mypy in `pyproject.toml` with:
  - Strict mode options adjusted to project needs
  - `ignore_missing_imports` for libraries without type stubs (initially)
  - Per-module configuration for gradual adoption
  
- **Gradual adoption strategy**:
  1. Start with strict checking on new modules
  2. Add type hints to critical business logic
  3. Gradually increase coverage over time
  4. Use `# type: ignore` sparingly with comments explaining why

- **CI Integration**: Add Mypy to CI pipeline to prevent untyped or incorrectly typed code from being merged

- **Editor Integration**: Configure VS Code to show Mypy errors inline for immediate feedback

- **Documentation**: Add guidelines to contribution docs on when and how to add type hints

- **Dependencies**: Consider installing type stub packages (`types-*`) for common dependencies

## References

- [Mypy documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 526 - Syntax for Variable Annotations](https://www.python.org/dev/peps/pep-0526/)
- Project's `pyproject.toml` for configuration
