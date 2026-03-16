# Copilot Instructions for TFG-Chatbot

## Project Guidelines

### Scope

This workspace combines two coordinated lines of work:

- Computer Science TFG: an educational chatbot platform with microservices.
- Mathematics TFG: from-scratch document clustering and topic modeling in `math_investigation/`.

### Architecture

Core runtime services are orchestrated with Docker Compose:

- `frontend/` (React + Vite) on port 3000.
- `backend/` (FastAPI gateway) on port 8000.
- `chatbot/` (LangGraph agent) on port 8080.
- `rag_service/` (retrieval/indexing) on port 8081.
- `math_service/` (FAQ/topic pipelines) on port 8083.
- Supporting infrastructure: MongoDB, Qdrant, Ollama, vLLM, Phoenix, Prometheus, Grafana.

Primary service flow:

- Frontend -> Backend -> Chatbot/RAG/Math Service.
- Chatbot uses RAG for retrieval.
- Math Service integrates with MongoDB, RAG, and Ollama.

### Build And Test

Use `uv` for local Python workflows.

```bash
# Local environment
uv venv
source .venv/bin/activate
uv pip install -e ./backend -e ./rag_service -e ./chatbot -e ./math_service -e .

# Main test run
uv run pytest backend/tests/ chatbot/tests/ rag_service/tests/ math_service/tests/ -v

# Docker-based dev run
docker compose up -d

# Container tests need dev dependencies in images
INSTALL_DEV=true docker compose build
./scripts/run_tests.sh all

# Python lint/format
ruff check . && black . && isort .
```

### Conventions

- Use `pydantic-settings` style typed settings with `.env` support for service config.
- Keep gateway boundaries in `backend/routers/` and avoid embedding orchestration logic in unrelated layers.
- For LangGraph tool execution in `chatbot/logic/graph.py`, every `ToolMessage` must include `tool_call_id`.
- For backend session access, always validate both session existence and ownership (`user_id`).
- Normalize RAG responses before downstream use; do not assume one fixed payload shape.
- Keep math algorithms educational and from scratch in `math_investigation/` (no scikit-learn implementations for core algorithms).

### Key Patterns

- Add chatbot tools by updating both tool registration and graph routing:
    1. Create/update tool in `chatbot/logic/tools/`.
    2. Ensure it is included in `AVAILABLE_TOOLS`.
    3. Add graph node/edge wiring in `chatbot/logic/graph.py`.
- Use `httpx.AsyncClient` for service-to-service calls with explicit timeouts.
- Keep integration tests aligned with markers in repo/service `pytest.ini` files.

### Documentation And Decisions

- Architecture and service docs live under `docs/services/`.
- Scrum/devlog artifacts and ADRs live under `docs/devlog/` and `docs/devlog/adr/`.
- When changing architecture or cross-service contracts, record the decision as an ADR.

### Pitfalls To Avoid

- Do not create a new graph agent instance per request when checkpoint continuity is required.
- Do not skip `INSTALL_DEV=true` before container test runs.
- Do not assume chatbot Docker Python version matches other services; verify version compatibility when touching dependencies.
- Do not bypass ownership checks when reading or mutating chat sessions.
