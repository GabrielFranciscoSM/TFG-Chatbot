# CI Workflow Plan for RAG Service

Purpose
-------
This note documents a recommended GitHub Actions CI workflow to run tests and basic checks for the `rag_service` subproject. The goal is to provide fast feedback on PRs and protect main branch quality by running unit tests, linters, and optional integration tests.

Goals
-----
- Run unit tests for `rag_service` on push and pull requests.
- Optionally run integration-like tests that rely on Qdrant and Ollama (in a controlled way).
- Fail early for broken tests or missing dependencies.
- Keep workflow fast and split longer steps to a separate job (e.g., nightly integration tests).
- Publish test artifacts (coverage reports, logs) for debugging failures.

High-level job layout
---------------------
1. unit-tests (fast)
   - runs on ubuntu-latest
   - installs Python dependencies
   - run `pytest -q rag_service/tests` with mocks for external services
   - uploads coverage artifact

2. lint (fast)
   - run black/ruff/isort or project's linters

3. integration-tests (optional, slow)
   - run only on `workflow_dispatch` or nightly schedule or when a label is added
   - starts Qdrant and Ollama containers as services
   - runs a curated integration suite that starts the RAG service (or test directly) and performs end-to-end checks: index -> search -> metadata filters

4. caching
   - use pip cache action or rely on runtime caching for faster runs

Concrete steps (unit-tests)
--------------------------
- Checkout code
- Set up Python (3.11)
- Install dependencies from `rag_service/requirements.txt`
- Run tests: `pytest -q rag_service/tests --maxfail=1 -q`
- Upload coverage and test results as artifacts (optional)

Integration tests guidance
--------------------------
- Integration tests may need real services. Two approaches:
  1. Use Docker-in-GitHub Actions with service containers (qdrant, ollama).
  2. Use mocks/fakes for Ollama (recommended for CI) and start a lightweight Qdrant container for vector store tests.

- For Ollama, either use a small test server or mock embeddings. Running the real Ollama binary in GH Actions may be heavy.

- Integration tests should be gated (manual dispatch or nightly) to avoid slowing PR feedback.

Secrets and configuration
-------------------------
- Use repository secrets for credentials if any external services are used.
- Example envs to set in the workflow: `QDRANT_HOST`, `QDRANT_PORT`, `DOCUMENTS_PATH`.

Artifacts and debugging
-----------------------
- Save pytest logs and coverage html as artifacts to help debug intermittent failures.
- When a job fails, capture the last 200 lines of the failing test log into the build summary.

Example file to add
-------------------
Create `.github/workflows/rag-service-ci.yml` with jobs: `unit-tests`, `lint`, `integration-tests` (optional). The unit-tests job runs on push/PR and the integration-tests job is triggered manually or nightly.

Open decisions
--------------
- Should integration tests run on every PR, or only nightly/manual? (Recommend nightly/manual.)
- Do we want to containerize the whole test run (podman/docker) to reproduce local dev exactly? (Recommend starting with plain Python job with service containers.)

Next steps
----------
1. Add a minimal workflow file under `.github/workflows/` (unit-tests + lint).
2. Add a gated `integration-tests` workflow or job with service containers (Qdrant + Ollama or mocked Ollama).
3. Add artifact uploading for coverage reports.
4. Iterate based on CI runtime and flakiness.

References
----------
- GitHub Actions docs: https://docs.github.com/actions
- Qdrant Docker image: https://hub.docker.com/r/qdrant/qdrant
- Ollama docs: https://ollama.com/docs
