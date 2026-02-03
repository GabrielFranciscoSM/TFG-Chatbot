# Chatbot Service Architecture

This document describes the architecture of the Chatbot Service, a LangGraph-powered AI agent that orchestrates conversations with students.

## System Architecture

```mermaid
flowchart TB
    subgraph External["External Services"]
        Backend[Backend Gateway<br/>Port 8000]
        RAG[RAG Service<br/>Port 8081]
        MongoDB[(MongoDB<br/>Port 27017)]
        Phoenix[Phoenix<br/>Port 6006]
    end
    
    subgraph Chatbot["Chatbot Service (Port 8080)"]
        subgraph API["API Layer"]
            FastAPI[FastAPI App]
            Endpoints[Endpoints]
            Middleware[Middleware]
        end
        
        subgraph Core["Core Logic"]
            GraphAgent[GraphAgent]
            TestGraph[TestSessionGraph]
            ProfileMgr[ProfileManager]
            DiffClassifier[DifficultyClassifier]
        end
        
        subgraph Tools["Tools Layer"]
            RAGTool[rag_search]
            GuiaTool[get_guia]
            TestTool[generate_test]
        end
        
        subgraph Infra["Infrastructure"]
            Checkpointer[SQLite Checkpointer]
            MongoClient[MongoDB Client]
            LLMClient[LLM Client]
        end
    end
    
    subgraph LLM["LLM Providers"]
        Gemini[Google Gemini]
        Mistral[Mistral AI]
        vLLM[vLLM Local]
    end
    
    Backend --> FastAPI
    FastAPI --> GraphAgent
    GraphAgent --> Tools
    GraphAgent --> Checkpointer
    GraphAgent --> LLMClient
    
    RAGTool --> RAG
    GuiaTool --> MongoClient
    TestTool --> LLMClient
    
    ProfileMgr --> MongoClient
    MongoClient --> MongoDB
    
    LLMClient --> Gemini
    LLMClient --> Mistral
    LLMClient --> vLLM
    
    FastAPI -.->|traces| Phoenix
```

## Component Overview

### API Layer

The API layer handles HTTP requests and coordinates with the core logic.

| Component | File | Responsibility |
|-----------|------|----------------|
| **FastAPI App** | `api.py` | Application setup, middleware, endpoints |
| **Models** | `models.py` | Request/Response Pydantic models |
| **Config** | `config.py` | Environment-based settings |

### Core Logic

The brain of the chatbot service:

| Component | File | Responsibility |
|-----------|------|----------------|
| **GraphAgent** | `logic/graph.py` | Main LangGraph state machine |
| **TestSessionGraph** | `logic/testGraph.py` | Interactive test subgraph |
| **ProfileManager** | `logic/profile_manager.py` | Student progress tracking |
| **DifficultyClassifier** | `logic/difficulty.py` | Question complexity analysis |
| **Prompts** | `logic/prompts.py` | System prompts per difficulty |

### Tools Layer

LangChain tools for agent capabilities:

| Tool | File | Description |
|------|------|-------------|
| **rag_search** | `logic/tools/rag.py` | Semantic search via RAG service |
| **get_guia** | `logic/tools/guia.py` | Teaching guide retrieval |
| **generate_test** | `logic/tools/test_gen.py` | Test question generation |

### Infrastructure

Supporting services and clients:

| Component | File | Description |
|-----------|------|-------------|
| **MongoDBClient** | `db/mongo.py` | MongoDB connection wrapper |
| **SQLite Checkpointer** | LangGraph | Conversation state persistence |
| **Instrumentation** | `instrumentation.py` | Phoenix/OpenTelemetry setup |

## Data Flow

### Chat Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Agent as GraphAgent
    participant LLM
    participant Tools
    participant RAG as RAG Service
    participant DB as MongoDB
    
    Client->>API: POST /chat
    API->>API: Log question event
    API->>Agent: call_agent(query, id, asignatura)
    
    Agent->>Agent: Classify difficulty
    Agent->>Agent: Select adaptive prompt
    Agent->>LLM: invoke(messages + tools)
    
    alt Tool Call Required
        LLM-->>Agent: tool_calls: [rag_search]
        Agent->>Tools: Execute rag_search
        Tools->>RAG: POST /search
        RAG-->>Tools: Document chunks
        Tools-->>Agent: ToolMessage
        Agent->>LLM: Continue with context
    end
    
    LLM-->>Agent: Final response
    Agent->>Agent: Save checkpoint
    Agent-->>API: Response with messages
    
    API->>DB: Update student profile
    API->>API: Log answer event
    API-->>Client: ChatResponse
```

### Test Session Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Agent as GraphAgent
    participant SubGraph as TestSessionGraph
    participant LLM
    
    Client->>API: POST /chat (request test)
    API->>Agent: call_agent
    Agent->>LLM: Process request
    LLM-->>Agent: tool_call: generate_test
    Agent->>SubGraph: Enter test_session node
    
    SubGraph->>SubGraph: Initialize test state
    SubGraph->>SubGraph: Present question 1
    SubGraph-->>Agent: INTERRUPT
    Agent-->>API: interrupted=true, interrupt_info
    API-->>Client: Question 1 + options
    
    Client->>API: POST /resume_chat (answer)
    API->>Agent: call_agent_resume
    Agent->>SubGraph: Resume with answer
    SubGraph->>LLM: Evaluate answer
    LLM-->>SubGraph: Feedback
    SubGraph->>SubGraph: Present question 2
    SubGraph-->>Agent: INTERRUPT
    Agent-->>API: Question 2
    
    Note over Client,LLM: Repeat for all questions
    
    SubGraph->>SubGraph: Generate summary
    SubGraph-->>Agent: Complete
    Agent-->>API: Final results
    API-->>Client: Test summary
```

## State Management

### SubjectState Schema

The main state object that flows through the graph:

```python
class SubjectState(MessagesState):
    # Core conversation
    messages: list[BaseMessage]  # Inherited
    asignatura: str | None       # Current subject
    context: list[dict] | None   # RAG results
    
    # Difficulty classification
    thinking: str | None         # CoT reasoning (advanced)
    query_difficulty: str | None # basic/intermediate/advanced
    
    # Test session (shared with TestSessionState)
    topic: str | None
    num_questions: int | None
    difficulty: str | None
    questions: list[MultipleChoiceTest] | None
    current_question_index: int | None
    user_answers: list[str] | None
    feedback_history: list[str] | None
    scores: list[bool] | None
    pending_feedback: str | None
```

### Checkpoint Persistence

LangGraph uses SQLite for conversation state:

```
chatbot/storage/checkpoints.db
```

Each thread (identified by `thread_id`) maintains:
- Full message history
- Tool call/response pairs
- Test session progress
- Context from RAG searches

## LangGraph Architecture

### Graph Structure

```mermaid
flowchart TD
    subgraph MainGraph["Main GraphAgent"]
        Entry([Entry Point])
        Think[think]
        RAG[rag_search]
        Guia[get_guia]
        TestNode[test_session]
        End([END])
        
        Entry --> Think
        Think -->|tool: rag_search| RAG
        Think -->|tool: get_guia| Guia
        Think -->|tool: generate_test| TestNode
        Think -->|no tool| End
        RAG --> Think
        Guia --> Think
        TestNode --> End
    end
    
    subgraph TestSubgraph["Test Session Subgraph"]
        Init([Initialize])
        Present[present_question]
        Interrupt((INTERRUPT))
        Evaluate[evaluate_answer]
        Check{More questions?}
        Summary[provide_summary]
        
        Init --> Present
        Present --> Interrupt
        Interrupt -.->|resume| Evaluate
        Evaluate --> Check
        Check -->|Yes| Present
        Check -->|No| Summary
    end
    
    TestNode -.-> Init
```

### Node Functions

| Node | Function | Description |
|------|----------|-------------|
| `think` | `GraphAgent.think()` | Main reasoning, tool selection |
| `rag_search` | `GraphAgent.rag_search()` | Execute RAG tool |
| `get_guia` | `GraphAgent.get_guia()` | Execute guia tool |
| `test_session` | Compiled subgraph | Handle interactive tests |

### Conditional Routing

```python
def should_continue(state: SubjectState):
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return last_message.tool_calls[0]["name"]  # Route to tool node
    else:
        return END  # Conversation complete
```

## LLM Provider Architecture

### Multi-Provider Support

```mermaid
flowchart TD
    Config[Settings.llm_provider]
    
    Config -->|gemini| Gemini[ChatGoogleGenerativeAI]
    Config -->|mistral| Mistral[ChatMistralAI]
    Config -->|vllm| VLLM[ChatOpenAI + vLLM]
    
    Gemini --> LLM[Unified LLM Interface]
    Mistral --> LLM
    VLLM --> LLM
    
    LLM --> Agent[GraphAgent]
```

### Provider Configuration

| Provider | Class | Configuration |
|----------|-------|---------------|
| **Gemini** | `ChatGoogleGenerativeAI` | `GEMINI_API_KEY`, `GEMINI_MODEL` |
| **Mistral** | `ChatMistralAI` | `MISTRAL_API_KEY`, `MISTRAL_MODEL` |
| **vLLM** | `ChatOpenAI` | `VLLM_HOST`, `VLLM_PORT`, `MODEL_PATH` |

## Adaptive Prompting

### Difficulty-Based Prompt Selection

```mermaid
flowchart TD
    Query[User Query]
    Classify[DifficultyClassifier]
    
    Query --> Classify
    Classify --> Decision{Level}
    
    Decision -->|basic| Basic[SYSTEM_PROMPT_BASIC<br/>Simple language, many examples]
    Decision -->|intermediate| Inter[SYSTEM_PROMPT_INTERMEDIATE<br/>Technical terms, practical use]
    Decision -->|advanced| Adv[SYSTEM_PROMPT_ADVANCED<br/>Full complexity, CoT reasoning]
    
    Basic --> Prompt[Selected Prompt]
    Inter --> Prompt
    Adv --> Prompt
    
    Prompt --> LLM[LLM with adapted style]
```

### Classification Methods

1. **Heuristic-Based** (Fast, no latency)
   - Keyword matching ("qué es" → basic)
   - Pattern recognition (regex)
   
2. **Embedding-Based** (More accurate)
   - Semantic similarity to trained centroids
   - Requires embedding model

## Student Profile System

### Profile Data Model

```mermaid
erDiagram
    StudentProfile ||--o{ Interaction : has
    StudentProfile ||--o{ TopicMastery : tracks
    StudentProfile ||--o{ ConversationTurn : records
    
    StudentProfile {
        string user_id PK
        datetime created_at
        datetime updated_at
        int total_interactions
        dict difficulty_distribution
        dict subject_mastery
    }
    
    Interaction {
        datetime timestamp
        string query
        string difficulty
        string topic
        string subject
        bool was_test
        float test_score
    }
    
    TopicMastery {
        int interactions_count
        float level
        int correct_answers
        int total_test_questions
        datetime last_interaction
    }
    
    ConversationTurn {
        string session_id
        string query
        string answer
        string difficulty
        float latency_ms
        datetime timestamp
    }
```

### Profile Update Flow

```mermaid
sequenceDiagram
    participant API
    participant ProfileMgr as ProfileManager
    participant MongoDB
    
    API->>ProfileMgr: record_interaction(user_id, query, difficulty, ...)
    ProfileMgr->>MongoDB: $inc total_interactions
    ProfileMgr->>MongoDB: $inc difficulty_distribution.{level}
    ProfileMgr->>MongoDB: $push recent_interactions
    
    alt Has subject and topic
        ProfileMgr->>MongoDB: $inc subject_mastery.{subject}.{topic}
    end
    
    MongoDB-->>ProfileMgr: Update result
    ProfileMgr-->>API: Success
```

## Observability Architecture

### Tracing with Phoenix

```mermaid
flowchart LR
    subgraph Chatbot
        LangChain[LangChain Calls]
        Instrumentor[LangChainInstrumentor]
        Exporter[OTLP Exporter]
    end
    
    subgraph Phoenix["Phoenix Collector"]
        Collector[Trace Collector]
        UI[Phoenix UI<br/>Port 6006]
    end
    
    LangChain --> Instrumentor
    Instrumentor --> Exporter
    Exporter -->|OTLP/HTTP| Collector
    Collector --> UI
```

### Metrics with Prometheus

```mermaid
flowchart LR
    subgraph Chatbot
        FastAPI[FastAPI App]
        Instrumentator[prometheus-fastapi-instrumentator]
        Metrics[/metrics endpoint]
    end
    
    subgraph Monitoring
        Prometheus[Prometheus]
        Grafana[Grafana]
    end
    
    FastAPI --> Instrumentator
    Instrumentator --> Metrics
    Prometheus -->|scrape| Metrics
    Grafana --> Prometheus
```

## Error Handling

### Error Flow

```mermaid
flowchart TD
    Request[API Request]
    
    Request --> Validate{Validation}
    Validate -->|Invalid| Error422[422 Validation Error]
    Validate -->|Valid| Process[Process Request]
    
    Process --> Agent[GraphAgent]
    Agent --> LLM{LLM Call}
    
    LLM -->|Timeout| Retry[Retry Logic]
    LLM -->|API Error| Error500[500 Internal Error]
    LLM -->|Success| Tools{Tool Execution}
    
    Tools -->|RAG Timeout| Fallback[Fallback Response]
    Tools -->|Success| Response[Success Response]
    
    Retry -->|Max Retries| Error500
    Retry -->|Success| Tools
```

### Error Categories

| Category | Handling | User Message |
|----------|----------|--------------|
| **Validation** | FastAPI automatic | Field-specific errors |
| **LLM Errors** | Retry with backoff | "Temporary issue, please retry" |
| **Tool Errors** | Graceful fallback | Continue without tool result |
| **DB Errors** | Log and continue | Non-blocking for chat |

## Security Considerations

### API Security

- **No direct authentication** - Relies on Backend gateway
- **Input validation** - Pydantic models
- **Rate limiting** - Configured at gateway level
- **Correlation IDs** - Request tracing

### Data Security

- **API keys as SecretStr** - Never logged
- **MongoDB auth** - Username/password authentication
- **Non-root container** - Runs as `appuser` (UID 1000)

## File Structure

```
chatbot/
├── __init__.py
├── __main__.py           # CLI entry point
├── api.py                # FastAPI application
├── config.py             # Settings with pydantic-settings
├── models.py             # API request/response models
├── events.py             # Event logging
├── instrumentation.py    # Phoenix setup
├── logging_config.py     # Structured logging
├── Dockerfile
├── pyproject.toml
│
├── db/
│   └── mongo.py          # MongoDB client wrapper
│
├── logic/
│   ├── graph.py          # Main GraphAgent
│   ├── testGraph.py      # Test session subgraph
│   ├── prompts.py        # System prompts
│   ├── difficulty.py     # Difficulty classifier
│   ├── profile_manager.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tool_models.py
│   │   └── student_profile.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── tools.py      # Tool registry
│       ├── rag.py        # RAG search tool
│       ├── guia.py       # Teaching guide tool
│       ├── test_gen.py   # Test generation tool
│       └── utils.py      # Tool utilities
│
├── storage/
│   └── checkpoints.db    # LangGraph state (generated)
│
└── tests/
    ├── conftest.py
    ├── test_graph.py
    ├── test_testGraph.py
    ├── test_difficulty.py
    └── ...
```

## Related Documentation

- [API Endpoints](api-endpoints.md) - Complete endpoint reference
- [LangGraph Agent](langgraph.md) - Detailed agent documentation
- [Tools](tools.md) - Tool implementations
- [Configuration](configuration.md) - All settings
