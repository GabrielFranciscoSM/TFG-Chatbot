# RAG Service Architecture

This document describes the internal architecture and data flow of the RAG (Retrieval-Augmented Generation) service.

## High-Level Architecture

```mermaid
graph TB
    subgraph "API Layer"
        API[FastAPI Application]
        Routes[Route Handlers]
    end
    
    subgraph "Document Layer"
        FileLoader[FileLoader]
        DocProcessor[DocumentProcessor]
        FileUtils[File Utilities]
    end
    
    subgraph "Embedding Layer"
        EmbeddingService[EmbeddingService]
        VectorStore[VectorStoreService]
    end
    
    subgraph "External Services"
        Ollama[Ollama API :11434]
        Qdrant[(Qdrant :6333)]
        FS[File System]
    end
    
    API --> Routes
    Routes --> FileLoader
    Routes --> VectorStore
    FileLoader --> FileUtils
    FileLoader --> DocProcessor
    DocProcessor --> VectorStore
    VectorStore --> EmbeddingService
    EmbeddingService --> Ollama
    VectorStore --> Qdrant
    FileLoader --> FS
    FileUtils --> FS
```

## Component Overview

### API Layer

| Component | File | Purpose |
|-----------|------|---------|
| FastAPI App | `api.py` | Application entry point, middleware |
| General Routes | `routes/general.py` | Health check, root endpoint |
| Search Routes | `routes/search_index.py` | Search and indexing |
| File Routes | `routes/files.py` | File management, upload |
| Subject Routes | `routes/subjects.py` | Subject discovery |

### Document Layer

| Component | File | Purpose |
|-----------|------|---------|
| FileLoader | `documents/file_loader.py` | Load files (PDF, TXT, MD) |
| DocumentProcessor | `documents/document_processor.py` | Text chunking |
| File Utilities | `documents/file_utils.py` | File system operations |

### Embedding Layer

| Component | File | Purpose |
|-----------|------|---------|
| EmbeddingService | `embeddings/embeddings.py` | Generate text embeddings |
| VectorStoreService | `embeddings/store.py` | Qdrant operations |

---

## Data Flow

### Document Indexing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant FileLoader
    participant DocProcessor
    participant EmbeddingService
    participant VectorStore
    participant Qdrant
    participant Ollama
    
    Client->>API: POST /upload (file + metadata)
    API->>FileLoader: save_uploaded_file()
    FileLoader-->>API: saved_path
    
    API->>FileLoader: load_file()
    FileLoader->>FileLoader: Extract text (PDF/TXT/MD)
    FileLoader-->>API: Document
    
    API->>VectorStore: index_documents([doc])
    VectorStore->>DocProcessor: chunk_documents()
    DocProcessor-->>VectorStore: [chunk1, chunk2, ...]
    
    VectorStore->>EmbeddingService: embed_documents(texts)
    EmbeddingService->>Ollama: POST /api/embeddings
    Ollama-->>EmbeddingService: vectors[]
    EmbeddingService-->>VectorStore: embeddings[]
    
    VectorStore->>Qdrant: upsert(points)
    Qdrant-->>VectorStore: success
    VectorStore-->>API: indexed_count
    API-->>Client: LoadFileResponse
```

### Semantic Search Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant VectorStore
    participant EmbeddingService
    participant Ollama
    participant Qdrant
    
    Client->>API: POST /search {query, filters}
    API->>VectorStore: search(query, filters)
    
    VectorStore->>EmbeddingService: embed_query(query)
    EmbeddingService->>Ollama: POST /api/embeddings
    Ollama-->>EmbeddingService: query_vector
    EmbeddingService-->>VectorStore: embedding
    
    VectorStore->>Qdrant: query_points(vector, filter)
    Qdrant-->>VectorStore: similar_points[]
    
    VectorStore->>VectorStore: Convert to SearchResults
    VectorStore-->>API: results[]
    API-->>Client: QueryResponse
```

---

## Module Structure

```
rag_service/
├── api.py                    # FastAPI application
├── config.py                 # Settings (pydantic-settings)
├── models.py                 # Pydantic request/response models
├── logging_config.py         # Structured logging setup
│
├── routes/                   # API endpoints
│   ├── general.py            # / and /health
│   ├── search_index.py       # /search, /index, /collection/info
│   ├── files.py              # /files, /upload, /load-file
│   └── subjects.py           # /subjects
│
├── documents/                # Document processing
│   ├── file_loader.py        # FileLoader class
│   ├── document_processor.py # DocumentProcessor (chunking)
│   └── file_utils.py         # list_files, list_subjects, etc.
│
├── embeddings/               # Vector operations
│   ├── embeddings.py         # EmbeddingService (Ollama)
│   └── store.py              # VectorStoreService (Qdrant)
│
└── tests/                    # Unit and integration tests
```

---

## Key Design Patterns

### Singleton Services

Global service instances ensure single connections:

```python
# embeddings/store.py
_vector_store: VectorStoreService | None = None

def get_vector_store() -> VectorStoreService:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store
```

Used for:
- `VectorStoreService` - Single Qdrant connection
- `EmbeddingService` - Single Ollama connection
- `DocumentProcessor` - Consistent chunking config
- `FileLoader` - Single file system root

### Metadata Schema

All documents use consistent metadata:

```python
class DocumentMetadata(BaseModel):
    filename: str | None
    asignatura: str           # Subject (required)
    tipo_documento: str       # Document type (required)
    fecha: str | None         # Date (ISO format)
    tema: str | None          # Topic
    autor: str | None         # Author
    fuente: str = "PRADO UGR" # Source
    idioma: str = "es"        # Language
    chunk_id: int | None      # Chunk index
    licencia: str | None      # License
```

### Layered Processing

Documents flow through three layers:

```
Raw File → FileLoader → Document → DocProcessor → Chunks → VectorStore → Qdrant
```

Each layer has single responsibility:
1. **FileLoader**: Extract text from files
2. **DocProcessor**: Split into optimal chunks
3. **VectorStore**: Embed and store in Qdrant

---

## External Dependencies

### Qdrant

Vector database for similarity search:

```mermaid
graph LR
    subgraph "Qdrant"
        Collection[academic_documents]
        Points[Vector Points]
        Payload[Metadata Payload]
    end
    
    Collection --> Points
    Points --> Payload
```

Configuration:
- Collection: `academic_documents`
- Distance: COSINE
- Vector size: 768 (nomic-embed-text)

### Ollama

Local embedding generation:

```mermaid
graph LR
    RAG[RAG Service]
    Ollama[Ollama API]
    Model[nomic-embed-text]
    
    RAG -->|POST /api/embeddings| Ollama
    Ollama --> Model
    Model -->|768-dim vector| RAG
```

Model: `nomic-embed-text` (768 dimensions)

---

## Error Handling

### HTTP Exceptions

```python
# Standard error responses
HTTPException(404, "File not found")
HTTPException(400, "Unsupported file type")
HTTPException(500, "Search failed: {error}")
```

### Health Check

Returns service status with Qdrant connection:

```python
HealthCheckResponse(
    status="healthy" | "unhealthy",
    qdrant_connected=True | False,
    collection={...} | None,
    message="..."
)
```

---

## Observability

### Prometheus Metrics

Auto-instrumented via `prometheus-fastapi-instrumentator`:

- `http_requests_total` - Request count
- `http_request_duration_seconds` - Latency histogram
- `http_requests_in_progress` - Active requests

Access: `GET /metrics`

### Structured Logging

JSON logs with correlation IDs:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Search called",
  "correlation_id": "abc123",
  "query": "What is Docker?",
  "top_k": 5
}
```

---

## Related Documentation

- [API Endpoints](api-endpoints.md) - Complete API reference
- [Embeddings](embeddings.md) - Embedding service details
- [Vector Store](vector-store.md) - Qdrant integration
- [Document Processing](document-processing.md) - Chunking strategies
