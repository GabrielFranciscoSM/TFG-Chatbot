---
adr: 0015
title: "Use isort for import sorting"
date: 2025-11-15
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 15
---

# ADR 0015 — Use isort for import sorting

## Status

Accepted

## Context

Python imports can quickly become disorganized as projects grow, making it harder to identify dependencies and maintain clean module boundaries. Inconsistent import ordering creates unnecessary noise in diffs and code reviews.

We need a tool that:
- Automatically organizes imports in a consistent, standard way
- Groups imports logically (standard library, third-party, local)
- Integrates with our existing formatting tools (Black)
- Reduces merge conflicts related to import ordering
- Works seamlessly in development and CI workflows

## Decision

Adopt **isort** as the automatic import sorting tool for the project.

isort will be used to:
- Automatically sort and group all Python imports
- Organize imports into standard sections (stdlib, third-party, first-party)
- Maintain consistent import style across the codebase
- Run in CI to enforce import organization
- Integrate with Black for compatible formatting

Configuration will be set to be fully compatible with Black's formatting to avoid conflicts.

## Consequences

- Pros:
  - **Consistency**: All imports follow the same organization pattern
  - **Readability**: Easier to scan imports and understand dependencies
  - **Reduced conflicts**: Consistent ordering reduces merge conflicts in import blocks
  - **Automatic**: No manual sorting or organization needed
  - **PEP 8 compliant**: Follows Python's recommended import organization
  - **Black compatible**: Works seamlessly with Black when properly configured
  - **Editor support**: Good integration with VS Code and other editors

- Cons / Trade-offs:
  - Another tool to configure and run
  - May occasionally group imports in unexpected ways requiring manual adjustment
  - Configuration needed to ensure compatibility with Black
  - Initial run may create large diffs

## Alternatives considered

- **Ruff's isort rules** (I-rules):
  - Pros: Single tool, faster, built-in to Ruff
  - Cons: Less mature than standalone isort, fewer configuration options, not auto-fix by default

- **Manual import organization**:
  - Pros: Full control, no additional tooling
  - Cons: Inconsistent application, time-consuming, error-prone, creates review overhead

- **Black-only**:
  - Pros: One less tool to manage
  - Cons: Black doesn't sort imports, only formats them once they're in place

## Operational notes and recommendations

- **Configuration**: Configure isort in `pyproject.toml` for Black compatibility:
  ```toml
  [tool.isort]
  profile = "black"
  line_length = 88  # match Black's line length
  ```

- **Black compatibility**: Using `profile = "black"` ensures isort and Black work together without conflicts

- **Initial adoption**:
  1. Run isort on entire codebase in a single commit
  2. Can be combined with Black initial formatting commit
  3. Document this commit for git blame purposes

- **CI Integration**: Add isort check to CI with `isort --check-only` to fail builds with unsorted imports

- **Editor Integration**: 
  - Configure VS Code to run isort on save (before Black)
  - Order of operations: isort → Black for best results

- **Pre-commit hooks**: Add isort before Black in pre-commit configuration

- **Tool order**: When running multiple formatters, always run in this order:
  1. isort (organize imports)
  2. Black (format code)
  3. Ruff check --fix (fix auto-fixable linting issues)

- **Special cases**: Use `# isort: skip` or `# isort: split` comments for rare cases needing manual control

## References

- [isort documentation](https://pycqa.github.io/isort/)
- [Black and isort compatibility](https://pycqa.github.io/isort/docs/configuration/black_compatibility.html)
- [PEP 8 - Imports](https://www.python.org/dev/peps/pep-0008/#imports)
- Project's `pyproject.toml` for configuration
