# Integration Tests Plan for RAG Service

Purpose
-------
This note describes an approach to add robust integration tests for `rag_service`. Integration tests will exercise the core E2E behavior: ingesting documents, generating embeddings, indexing into Qdrant, and performing searches with metadata filters.

Objectives
----------
- Verify end-to-end behavior of the RAG service components under realistic conditions.
- Detect regressions in chunking, embedding, and vector-store logic.
- Keep integration tests reproducible and isolated from production data.

Test scope and scenarios
-----------------------
1. Index-and-search flow (happy path)
   - Start Qdrant (container) and a mocked embedding service (or real Ollama if feasible).
   - POST index request or load a file into the service.
   - Wait or poll until vector store reports points are available.
   - Run a search query and assert expected top-k results and metadata.

2. Metadata filtering
   - Index documents with distinct `asignatura` and `tipo_documento`.
   - Search with `asignatura` filter and ensure results are filtered accordingly.

3. Chunking correctness
   - Index a long document and assert the number of chunks equals expected (based on chunk_size and overlap).

4. Error cases
   - Attempt to load an unsupported file type and assert correct 400/404 responses.
   - Simulate Qdrant unavailable and assert the service handles errors gracefully.

Test setup options
------------------
- Option A: Service containers (recommended for realism)
  - Use Docker Compose or GitHub Actions service containers for Qdrant and optionally Ollama.
  - Advantages: realistic behavior, closer to production.
  - Disadvantages: slower, heavier on CI resources.

- Option B: Hybrid (recommended for CI)
  - Start actual Qdrant container, but mock Ollama embeddings with deterministic vectors.
  - This keeps vector store behavior real while avoiding heavy dependency on Ollama runtime.

Test orchestration
------------------
- Use a pytest tests/integration/ folder.
- Provide fixtures to start/stop containers (or reuse GH Actions services) and to seed test documents into a temporary `DOCUMENTS_PATH`.
- Use retries/polling when waiting for indexing to finish (with short timeouts to avoid flakiness).

Data management
---------------
- Use ephemeral directories for documents (tmp_path fixture).
- Ensure Qdrant collections used by tests are uniquely named (e.g., `test-<CI_JOB_ID>`) and removed after tests.

Stability techniques
--------------------
- Use deterministic embeddings (seeded PRNG or fixed vectors) for predictable search order.
- Limit number of documents and chunk sizes to keep indexing fast.
- Poll with exponential backoff when waiting for candidates in Qdrant.

Gating strategy
---------------
- Run quick hybrid integration tests on PRs (Qdrant + mocked embeddings).
- Run full end-to-end nightly or on-demand (real Ollama + Qdrant) if needed.

Next steps
----------
1. Create `tests/integration/` with a minimal happy-path test using Qdrant service and mocked embeddings.
2. Add fixture utilities to manage collection lifecycle.
3. Add a GH Actions workflow or job to run integration tests (gated/manual or nightly).

References
----------
- Qdrant API: https://qdrant.tech/documentation/
- Example GH Actions with services: https://docs.github.com/actions/using-containerized-services
