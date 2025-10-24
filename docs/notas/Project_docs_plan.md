# Project Documentation Plan

Purpose
-------
This note outlines a documentation plan for the `TFG-Chatbot` project with a focus on the RAG service, developer onboarding, and user-facing docs.

Documentation goals
-------------------
- Provide clear README and quickstart for developers.
- Document architecture and high-level design decisions.
- Provide API reference for the RAG service endpoints.
- Document deployment (Docker, docker-compose, Kubernetes) and CI processes.
- Include troubleshooting and FAQ for common runtime issues.

Suggested docs structure (under `rag_service/docs/`)
---------------------------------------------------
1. `API.md` — Detailed API endpoints, request/response examples, schemas.
2. `CI.md` — CI workflow and how to run tests locally and in CI.
3. `INTEGRATION_TESTS.md` — Integration test plan and how to run them.
4. `DEPLOYMENT.md` — How to run with docker-compose, deploy to k8s, environment variables.
5. `CHUNKING.md` — Explanations about chunking strategy and parameters.
6. `OPERATIONS.md` — How to inspect Qdrant, reindex, backup/restore data.
7. `CONTRIBUTING.md` — Contributing guidelines, coding style, and PR checklist.

Developer onboarding
--------------------
- `README.md` with quickstart (docker-compose), Python dev setup, and where to find tests.
- `CONTRIBUTING.md` with linter rules, commit message guide, and how to run tests locally.

Docs format and tooling
-----------------------
- Use Markdown for docs and keep them in `rag_service/docs/` and higher-level project docs in `devLog/` or `notas/`.
- Optionally, use MkDocs to generate static documentation site if needed in the future.

Prioritized next docs to write
-----------------------------
1. `API.md` — because it helps QA and integrators.
2. `CI.md` — describe how to run tests and CI workflow (mirrors CI note).
3. `INTEGRATION_TESTS.md` — practical steps for running integration tests.

Next steps
----------
1. Create the three files above as a start and add them to `rag_service/docs/`.
2. Add links in `rag_service/README.md` to the docs.
3. Iterate and expand docs as features or infra change.
