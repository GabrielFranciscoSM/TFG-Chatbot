---
adr: 0012
title: "Use Ruff for linting"
date: 2025-11-15
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 12
---

# ADR 0012 — Use Ruff for linting

## Status

Accepted

## Context

The project needs a fast, modern linting tool to catch common bugs, enforce code quality standards, and maintain consistency across the codebase. Traditional Python linters like `flake8` and `pylint` can be slow on large codebases and require multiple plugins to achieve comprehensive coverage.

We need a tool that:
- Provides comprehensive linting rules (covering style, bugs, and best practices)
- Runs quickly to support fast feedback in development and CI
- Can be configured to match team standards
- Integrates well with modern Python development workflows

## Decision

Adopt **Ruff** as the primary linting tool for the project.

Ruff will be used to:
- Check for code quality issues, potential bugs, and anti-patterns
- Enforce consistent coding style (complementing Black for formatting)
- Validate imports, unused variables, and other common issues
- Run in CI pipelines to prevent problematic code from being merged

Configuration will be maintained in `pyproject.toml` to centralize project settings.

## Consequences

- Pros:
  - **Extremely fast**: Ruff is written in Rust and orders of magnitude faster than traditional Python linters
  - **Comprehensive**: Implements rules from Flake8, pylint, pyupgrade, isort, and many other tools in one package
  - **Modern**: Active development with good VS Code integration and modern Python support
  - **Zero dependencies**: Single binary with no plugin ecosystem to manage
  - **Auto-fixable**: Many issues can be automatically fixed with `ruff check --fix`

- Cons / Trade-offs:
  - Newer tool with potentially evolving rule sets
  - Some team members may need to learn new rule codes (though they're well-documented)
  - May require initial configuration to match team preferences

## Alternatives considered

- **Flake8**:
  - Pros: Mature, widely used, extensive plugin ecosystem
  - Cons: Slower performance, requires multiple plugins for comprehensive coverage, configuration spread across multiple tools

- **Pylint**:
  - Pros: Very comprehensive checks, configurable
  - Cons: Significantly slower, more opinionated default rules, steeper learning curve

- **Multiple tools** (flake8 + pyflakes + pycodestyle, etc.):
  - Pros: Individual tools are well-tested and stable
  - Cons: Multiple configurations to maintain, slower combined execution, overlapping checks

## Operational notes and recommendations

- **Configuration**: Define Ruff settings in `pyproject.toml` including:
  - Selected rule sets (e.g., E, F, I, N, UP, etc.)
  - Line length to match Black's configuration
  - Any project-specific ignores or per-file-ignores
  
- **CI Integration**: Add Ruff checks to CI pipeline before tests run
  
- **Editor Integration**: Configure VS Code or other editors to run Ruff on save for immediate feedback

- **Pre-commit hooks**: Consider adding Ruff to pre-commit hooks for early issue detection

- **Auto-fixing**: Use `ruff check --fix` to automatically fix many issues during development

## References

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Ruff rules reference](https://docs.astral.sh/ruff/rules/)
- Project's `pyproject.toml` for configuration
