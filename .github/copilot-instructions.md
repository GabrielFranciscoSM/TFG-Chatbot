# Copilot Instructions for TFG-Chatbot

## Architecture Overview

This is a **microservices-based educational chatbot** using LangGraph for AI orchestration. Four containerized services (Podman) communicate via HTTP:

```
Frontend → Backend (gateway) → Chatbot (AI agent) → RAG Service
                  ↓                    ↓                 ↓
                MongoDB              LLM           Qdrant + Ollama
```

- **backend/** - FastAPI gateway handling auth, sessions, and routing to chatbot
- **chatbot/** - LangGraph agent with tools (RAG, guía docente, web search, test generation)
- **rag_service/** - Document indexing and semantic search via Qdrant/Ollama
- **frontend/** - Vite + React + TypeScript + TailwindCSS + shadcn/ui (in active development)

**LLM Inference**: Gemini API for development, vLLM for production deployment. Configured via `LLM_PROVIDER` env var.

## Project Methodology

This project follows **SCRUM** methodology. Key documentation in `docs/`:
- **ADRs** (`docs/ADR/`) - Architecture Decision Records for all technical choices
- **Sprint artifacts** - `sprint planing/`, `sprint retrospective/`, `daily scrum/`
- When making architectural decisions, document them as ADRs following `docs/ADR/adr-template.md`

## Key Patterns

### LangGraph Agent Structure (chatbot/logic/graph.py)
The agent uses `StateGraph` with nodes for each tool. State includes `asignatura` (subject) and `context`. Tool routing happens via `should_continue()` which returns the tool name from `tool_calls[0]["name"]`.

```python
# Pattern: Add new tools
1. Create tool with @tool decorator in chatbot/logic/tools/tools.py
2. Add to AVAILABLE_TOOLS list
3. Add node in GraphAgent.build_graph()
4. Add edge mapping in should_continue routing
```

### Service Communication
Services use environment-based URLs defaulting to Podman Compose service names:
- Backend → Chatbot: `CHATBOT_SERVICE_URL` (default: `http://chatbot:8080`)
- Chatbot → RAG: `RAG_SERVICE_URL` (default: `http://rag_service:8081`)

### Configuration Pattern
- Use `pydantic_settings.BaseSettings` for type-safe config (see `rag_service/config.py`)
- Backend uses simpler class-based `Settings` (see `backend/config.py`)
- All configs load from `.env` with sensible defaults for Podman Compose

### Test Session Flow (chatbot/logic/testGraph.py)
Interactive tests use LangGraph interrupts:
1. `generate_test` tool creates questions
2. Subgraph presents questions via `interrupt()` 
3. `/resume_chat` endpoint resumes with user answer
4. State tracks `current_question_index`, `scores`, `user_answers`

## Development Commands

```bash
# Environment setup with uv (preferred)
uv venv                                        # Create virtual environment
source .venv/bin/activate                      # Activate venv
uv pip install -e ./backend -e ./rag_service -e ./chatbot  # Install packages

# Run tests (use markers for filtering)
pytest backend/tests/ -m unit -v              # Backend unit tests
pytest rag_service/tests/ -m unit -v          # RAG service tests  
pytest tests/infrastructure/ -m podman_container  # Requires containers

# Linting (pre-commit installed)
ruff check . && black . && isort .

# Podman development
podman-compose up -d                           # Start all services
INSTALL_DEV=true podman-compose build          # Build with dev deps
```

## Test Patterns

- **Mocking**: Use `mongomock` for MongoDB (see `backend/tests/conftest.py`)
- **Fixtures**: Create `test_user`, `test_professor` with hashed passwords
- **Token Auth**: Generate tokens via `create_access_token()` for authenticated tests
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.infrastructure`

## Important Conventions

1. **User roles**: `UserRole.STUDENT` and `UserRole.PROFESSOR` with subject-based access
2. **Session ownership**: Sessions are tied to `user_id`, validated in `chat.py` router
3. **LLM Provider**: Gemini (dev) / vLLM (prod) via `LLM_PROVIDER` env var
4. **Guía Docente**: UGR teaching guides stored in MongoDB via scraper tool
5. **Thread IDs**: LangGraph uses `thread_id` from request `id` for checkpointing
6. **Containerization**: Use Podman (not Docker) - commands are compatible

## File Organization

```
chatbot/logic/
├── graph.py        # Main GraphAgent with tool nodes
├── testGraph.py    # Test session subgraph with interrupts
├── prompts.py      # System prompts and LLM prompt templates
├── models.py       # Pydantic models for tools/state
└── tools/tools.py  # All @tool decorated functions

docs/
├── ADR/            # Architecture Decision Records (critical!)
├── sprint planing/ # SCRUM sprint planning docs
├── sprint retrospective/
└── daily scrum/
```

## Common Mistakes to Avoid

- Don't create new `GraphAgent` per request - use single instance for checkpoint consistency
- Always add `tool_call_id` when returning `ToolMessage` from tool nodes
- RAG results need normalization - check `_normalize_rag_results()` pattern
- Session validation requires checking both existence AND ownership
- Document architectural decisions in ADRs, not just in code comments
