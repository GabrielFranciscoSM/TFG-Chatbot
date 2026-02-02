---
layout: default
title: Project Structure
parent: Developer Guide
nav_order: 8
---

# Project Structure

Overview of the TFG-Chatbot repository organization.

---

## Root Directory

```
TFG-Chatbot/
├── 📁 backend/                 # Backend Gateway Service
├── 📁 chatbot/                 # AI Chatbot Service
├── 📁 rag_service/             # RAG Service
├── 📁 frontend/                # React Web Application
├── 📁 math_investigation/      # Mathematics TFG Module
├── 📁 tests/                   # Integration & Infrastructure Tests
├── 📁 scripts/                 # Utility Scripts
├── 📁 docs/                    # Project Documentation (GitHub Pages)
├── 📁 notebooks/               # Jupyter Notebooks
├── 📁 models/                  # Downloaded ML Models
├── 📁 test-reports/            # Generated Test Reports
│
├── docker-compose.yml          # Container orchestration
├── pyproject.toml              # Python project configuration
├── _config.yml                 # Jekyll configuration (GitHub Pages)
├── .env                        # Environment variables (not committed)
└── README.md                   # Project overview
```

---

## Backend Service (`backend/`)

FastAPI gateway that handles authentication, session management, and request routing.

```
backend/
├── api.py                      # FastAPI application entry point
├── config.py                   # Configuration settings
├── models.py                   # Pydantic models
├── security.py                 # JWT and password utilities
├── dependencies.py             # FastAPI dependencies
├── Dockerfile                  # Container definition
├── pyproject.toml              # Package configuration
│
├── routers/                    # API route handlers
│   ├── auth.py                 # Authentication (login, register)
│   ├── users.py                # User management (CRUD)
│   ├── chat.py                 # Chat proxy to chatbot service
│   └── sessions.py             # Session management
│
├── db/                         # Database utilities
│   ├── connection.py           # MongoDB connection
│   └── users.py                # User CRUD operations
│
├── logic/                      # Business logic
│   └── ...
│
└── tests/                      # Unit tests
    ├── conftest.py             # Test fixtures
    ├── test_auth.py            # Authentication tests
    └── test_users.py           # User management tests
```

---

## Chatbot Service (`chatbot/`)

LangGraph-based AI agent with pedagogical tools.

```
chatbot/
├── api.py                      # FastAPI application
├── config.py                   # LLM and service settings
├── models.py                   # State and tool models
├── Dockerfile                  # Container definition
├── pyproject.toml              # Package configuration
│
├── logic/                      # Core chatbot logic
│   ├── graph.py                # LangGraph agent definition
│   ├── testGraph.py            # Test session subgraph
│   ├── prompts.py              # System prompts
│   ├── models.py               # State and tool models
│   ├── difficulty.py           # Question difficulty classifier
│   └── tools/                  # Agent tools
│       └── tools.py            # RAG, calculator, web search, etc.
│
├── db/                         # Database utilities
│   └── checkpointer.py         # SQLite checkpointer for LangGraph
│
├── data/                       # Static data files
│   └── difficulty_centroids.json  # Trained classifier centroids
│
└── tests/                      # Unit tests
    └── ...
```

---

## RAG Service (`rag_service/`)

Document indexing and semantic search service.

```
rag_service/
├── api.py                      # FastAPI application
├── config.py                   # Qdrant, Ollama settings
├── models.py                   # Request/response models
├── Dockerfile                  # Container definition
├── pyproject.toml              # Package configuration
│
├── routes/                     # API route handlers
│   ├── indexing.py             # Document upload and indexing
│   └── search.py               # Semantic search endpoints
│
├── embeddings/                 # Embedding generation
│   └── ollama.py               # Ollama embeddings client
│
├── documents/                  # Document processing
│   └── processor.py            # PDF/text extraction
│
└── tests/                      # Unit tests
    └── ...
```

---

## Frontend (`frontend/`)

React application with TypeScript and Tailwind CSS.

```
frontend/
├── src/
│   ├── components/             # UI components (shadcn/ui)
│   │   ├── ui/                 # Base UI components
│   │   ├── chat/               # Chat interface components
│   │   └── admin/              # Admin panel components
│   │
│   ├── pages/                  # Page components
│   │   ├── ChatPage.tsx        # Main chat interface
│   │   ├── LoginPage.tsx       # Login form
│   │   └── AdminPage.tsx       # Admin dashboard
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts          # Authentication hook
│   │   └── useChat.ts          # Chat state hook
│   │
│   ├── context/                # React Context
│   │   └── AuthContext.tsx     # Authentication context
│   │
│   ├── api/                    # API client functions
│   │   └── client.ts           # Fetch wrapper
│   │
│   ├── types/                  # TypeScript types
│   └── App.tsx                 # Root component
│
├── public/                     # Static assets
├── package.json                # Node.js dependencies
├── vite.config.ts              # Vite configuration
├── biome.json                  # Linter configuration
└── Dockerfile                  # Container definition
```

---

## Math Investigation (`math_investigation/`)

From-scratch implementations of clustering algorithms.

```
math_investigation/
├── clustering/                 # Clustering algorithms
│   ├── kmeans.py               # K-Means with K-Means++ init
│   ├── fcm.py                  # Fuzzy C-Means
│   └── metrics.py              # Evaluation metrics
│
├── topic_modeling/             # Topic modeling
│   ├── nmf.py                  # Non-negative Matrix Factorization
│   └── coherence.py            # Topic coherence metrics
│
├── nlp/                        # Text vectorization
│   ├── tfidf.py                # TF-IDF vectorizer
│   ├── bow.py                  # Bag of Words vectorizer
│   └── embeddings.py           # Ollama embeddings wrapper
│
├── visualization/              # Plotting utilities
│   └── plots.py                # Matplotlib plots
│
├── cli/                        # Command-line runners
│   ├── run_clustering.py       # Run clustering experiments
│   ├── run_topic_modeling.py   # Run topic modeling
│   └── compare.py              # Compare algorithms
│
├── utils/                      # Utility functions
├── data/                       # Datasets
└── results/                    # Experiment outputs
```

---

## Tests (`tests/`)

Integration and infrastructure tests.

```
tests/
├── infrastructure/             # Container health tests
│   ├── conftest.py             # Shared fixtures
│   ├── test_backend_container.py
│   ├── test_chatbot_container.py
│   ├── test_frontend_container.py
│   ├── test_mongo_container.py
│   ├── test_ollama_container.py
│   ├── test_qdrant_container.py
│   ├── test_rag_service_container.py
│   ├── test_vllm_container.py
│   └── README.md
│
├── integration/                # End-to-end tests
│   ├── conftest.py             # Test fixtures
│   ├── test_backend.py
│   ├── test_rag_service.py
│   ├── test_proactive_rag.py
│   └── README.md
│
└── __init__.py
```

---

## Documentation (`docs/`)

GitHub Pages documentation using Jekyll (Just the Docs theme).

```
docs/
├── index.md                    # DevLog index
├── guide/                      # Developer Guide (this section)
│   ├── index.md
│   ├── installation.md
│   ├── quickstart.md
│   ├── scripts.md
│   ├── testing.md
│   ├── configuration.md
│   ├── troubleshooting.md
│   ├── math-investigation.md
│   └── project-structure.md
│
├── ADR/                        # Architecture Decision Records
│   ├── index.md
│   ├── 0001-use-fastapi-for-api.md
│   └── ... (37 ADRs)
│
├── daily scrum/                # Daily scrum logs
├── sprint planing/             # Sprint planning docs
├── sprint retrospective/       # Sprint retrospectives
├── api/                        # Exported OpenAPI specs
├── investigacion/              # Research notes
└── latex/                      # TFG LaTeX documents
```

---

## Scripts (`scripts/`)

Utility scripts for development and operations.

| Script | Purpose |
|--------|---------|
| `run_tests.sh` | Run tests in containers |
| `run_fastAPI.sh` | Quick backend start |
| `seed_users.py` | Create demo users |
| `init_ollama.sh` | Setup embeddings model |
| `train_difficulty_centroids.py` | Train difficulty classifier |
| `label_questions_with_llm.py` | Auto-label questions |
| `download_model.py` | Download HuggingFace models |
| `query_student_history.py` | Query conversation history |
| `export_openapi.py` | Export API specifications |
| `new_adr.sh` | Create new ADR file |
| `bump_version.py` | Update version number |
| `release.sh` | Create release |

---

## Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Container orchestration |
| `pyproject.toml` | Python project config (uv, ruff, pytest) |
| `_config.yml` | Jekyll configuration for GitHub Pages |
| `pytest.ini` | Pytest configuration |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `.github/workflows/` | GitHub Actions CI/CD |
| `.github/copilot-instructions.md` | Copilot context |
