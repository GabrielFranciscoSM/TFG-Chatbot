---
adr: 0014
title: "Use Black for code formatting"
date: 2025-11-15
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 14
---

# ADR 0014 — Use Black for code formatting

## Status

Accepted

## Context

Code formatting consistency is important for maintainability and reducing friction in code reviews. Without automated formatting, teams spend time debating style choices and reviewing formatting issues instead of focusing on logic and functionality.

We need a code formatter that:
- Enforces consistent style across the entire codebase
- Requires minimal configuration decisions
- Integrates well with editors and CI
- Is widely adopted in the Python ecosystem
- Can be automated to remove formatting from code review discussions

## Decision

Adopt **Black** as the automatic code formatter for the project.

Black will be used to:
- Automatically format all Python code to a consistent style
- Run in CI to enforce formatting consistency
- Integrate with editors for format-on-save functionality
- Eliminate formatting discussions in code reviews

The formatter will be configured with minimal options (Black's philosophy is "uncompromising"), primarily setting the line length to match project preferences.

## Consequences

- Pros:
  - **Consistency**: All code follows the same style automatically
  - **No debates**: Black's opinionated approach eliminates formatting discussions
  - **Time savings**: No manual formatting or formatting reviews needed
  - **Focus on logic**: Code reviews can focus on functionality, not style
  - **Wide adoption**: Black is the de facto standard formatter in the Python community
  - **Stable formatting**: Code formatting doesn't change between versions unnecessarily
  - **Tool compatibility**: Works well with Ruff, isort, and other tools

- Cons / Trade-offs:
  - Opinionated style may not match all personal preferences
  - Some formatting choices (e.g., string quotes, line breaks) are not configurable
  - Initial reformatting may create large diffs in version control
  - Team members must accept Black's style decisions

## Alternatives considered

- **autopep8**:
  - Pros: More configurable, less opinionated
  - Cons: Configuration overhead, less consistent formatting across projects, not as widely adopted

- **YAPF** (Yet Another Python Formatter):
  - Pros: Highly configurable
  - Cons: Too many configuration options lead to debates, slower adoption, maintenance concerns

- **Manual formatting with style guide**:
  - Pros: Full control over style
  - Cons: Inconsistent application, time-consuming reviews, human error

- **Ruff format** (newer alternative):
  - Pros: Extremely fast, Black-compatible
  - Cons: Newer tool, still stabilizing; Black is more mature and battle-tested

## Operational notes and recommendations

- **Configuration**: Configure Black in `pyproject.toml`:
  ```toml
  [tool.black]
  line-length = 88  # or project preference
  target-version = ['py311']  # or appropriate Python version
  ```

- **Initial adoption**:
  1. Run Black on entire codebase in a single commit
  2. Clearly mark this commit in history (e.g., "Apply Black formatting")
  3. Configure git blame to ignore this commit

- **CI Integration**: Add Black check to CI with `black --check` to fail builds with formatting issues

- **Editor Integration**: 
  - Configure VS Code to run Black on save
  - Share editor configuration in `.vscode/settings.json`

- **Pre-commit hooks**: Add Black to pre-commit hooks to format code automatically before commits

- **Git configuration**: Add to `.git-blame-ignore-revs` to skip formatting commits in blame views

- **Team communication**: Inform team about initial formatting commit and setup instructions

## References

- [Black documentation](https://black.readthedocs.io/)
- [Black playground](https://black.vercel.app/) for testing formatting
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- Project's `pyproject.toml` for configuration
