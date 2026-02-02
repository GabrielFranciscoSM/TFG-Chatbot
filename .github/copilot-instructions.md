# Copilot Instructions for TFG-Chatbot

## Project Overview

This is a **dual degree TFG (Trabajo Fin de Grado)** for Computer Science and Mathematics at University of Granada:

- **Computer Science TFG**: Pedagogical chatbot using LangGraph for AI orchestration with microservices architecture
- **Mathematics TFG**: Document clustering research (K-Means, Fuzzy C-Means, NMF) to enhance the chatbot's question classification

## Architecture Overview

### Chatbot Microservices (Computer Science)

Four containerized services (Podman) communicate via HTTP:

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

### Math Investigation Module (Mathematics)

The `math_investigation/` module contains from-scratch implementations of clustering algorithms:

```
math_investigation/
├── clustering/           # K-Means, FCM implementations
│   ├── kmeans.py         # K-Means with K-Means++ init
│   ├── fcm.py            # Fuzzy C-Means with fuzziness m
│   └── metrics.py        # Silhouette, ARI, NMI, FPC
├── topic_modeling/       # NMF for topic discovery
│   ├── nmf.py            # Multiplicative update rules
│   └── coherence.py      # Topic coherence metrics
├── nlp/                  # Text vectorization
│   ├── tfidf.py          # TF-IDF from scratch
│   ├── bow.py            # Bag of Words
│   └── embeddings.py     # Ollama embeddings wrapper
├── visualization/        # Matplotlib plots
└── cli/                  # Experiment runners
```

**Mathematical foundations** (documented in TFG thesis):
- K-Means: Minimizes SSE(S,C) = Σ_{i=1}^{k} Σ_{x ∈ S_i} ||x - c_i||²
- FCM: Minimizes J_m(U,C) = Σ Σ (μ_ji)^m ||x_i - c_j||² where m > 1
- NMF: Factorizes V ≈ WH with non-negativity constraints

### Integration: Math Investigation ↔ Chatbot
The clustering algorithms enhance the chatbot in several ways:
- **Question classification**: K-Means/FCM cluster student questions by topic
- **Difficulty estimation**: Cluster centroids trained on labeled questions predict difficulty
- **RAG improvement**: NMF topic modeling helps organize and retrieve documents
- Scripts like `scripts/train_difficulty_centroids.py` bridge the two components

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

# Math investigation experiments
python -m math_investigation.cli.run_clustering --k 5 --vectorizer tfidf
python -m math_investigation.cli.run_topic_modeling --n-topics 5
python -m math_investigation.cli.compare --k-range 3,10

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

math_investigation/
├── clustering/     # K-Means, FCM with full implementations
│   ├── kmeans.py   # K-Means++ init, SSE minimization
│   ├── fcm.py      # Fuzzy membership, J_m minimization
│   └── metrics.py  # External + internal validation metrics
├── topic_modeling/ # NMF-based topic modeling
├── nlp/            # Vectorizers (TF-IDF, BoW, embeddings)
├── cli/            # Command-line experiment runners
└── visualization/  # Matplotlib plotting utilities

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

## Math Investigation Patterns

### Algorithm Implementation Rules
- All algorithms implemented **from scratch** without scikit-learn (educational purpose)
- NumPy is the only allowed numerical library
- Each algorithm has docstrings referencing the TFG thesis section
- Convergence tracking: store `sse_history_` (K-Means) or `jm_history_` (FCM)

### Vectorizer Interface
All vectorizers in `math_investigation/nlp/` follow this interface:
```python
class Vectorizer:
    def fit(self, documents: list[str]) -> "Vectorizer": ...
    def transform(self, documents: list[str]) -> np.ndarray: ...
    def fit_transform(self, documents: list[str]) -> np.ndarray: ...
```

### Clustering Interface
Both K-Means and FCM follow scikit-learn-like interface:
```python
class Clusterer:
    def fit(self, X: np.ndarray) -> "Clusterer": ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
    def fit_predict(self, X: np.ndarray) -> np.ndarray: ...
```

### Adding New Metrics
Metrics go in `math_investigation/clustering/metrics.py`:
- Internal metrics (no ground truth): silhouette, Davies-Bouldin, elbow
- External metrics (require labels): ARI, NMI
- FCM-specific: Fuzzy Partition Coefficient (FPC)
