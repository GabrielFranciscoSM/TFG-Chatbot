# Architecture Decision Records (ADR)

This folder contains ADRs — human-readable records of important architecture decisions.

Purpose
- Keep a lightweight history of why important technical decisions were made.
- Make it easier to review, revisit and evolve decisions.

How to name ADR files
- Use a four-digit sequence and a short slug, e.g. `0001-use-postgres-for-persistence.md`.

Template
- Use `adr-template.md` as a starting point.

Quick workflow
1. Create a new ADR with the provided script: `scripts/new_adr.sh "Short title"`.
2. Edit the file, fill Context/Decision/Consequences.
3. Commit the ADR in the same PR that introduces the corresponding architectural change.

Guidelines
- Keep ADRs brief and focused on why, not how.
- Record alternatives considered and the trade-offs.
