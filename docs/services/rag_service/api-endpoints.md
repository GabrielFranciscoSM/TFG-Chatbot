# RAG Service API Endpoints

Complete reference for the RAG Service REST API.

## Base URL

- **Development**: `http://localhost:8081`
- **Docker**: `http://rag_service:8081`

---

## General Endpoints

### GET `/`

API information and status.

**Response:**
```json
{
  "name": "RAG Service",
  "version": "0.1.0",
  "description": "API for interacting with a Retrieval-Augmented Generation service",
  "status": "running"
}
```

---

### GET `/health`

Health check with Qdrant connection status.

**Response:**
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "collection": {
    "name": "academic_documents",
    "vectors_count": 52,
    "points_count": 52,
    "status": "green"
  },
  "message": "API is healthy and running"
}
```

**Unhealthy Response:**
```json
{
  "status": "unhealthy",
  "qdrant_connected": false,
  "collection": null,
  "message": "Service unhealthy: Connection refused"
}
```

---

## Search Endpoints

### POST `/search`

Perform semantic search over indexed documents.

**Request Body:**
```json
{
  "query": "What is fuzzy logic?",
  "asignatura": "logica-difusa",
  "tipo_documento": "apuntes",
  "top_k": 5,
  "similarity_threshold": 0.5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Natural language search query |
| `asignatura` | string | No | Filter by subject |
| `tipo_documento` | string | No | Filter by document type |
| `top_k` | integer | No | Max results (default: 5) |
| `similarity_threshold` | float | No | Min score 0-1 (default: 0.5) |

**Response:**
```json
{
  "results": [
    {
      "content": "Fuzzy logic is a form of many-valued logic...",
      "metadata": {
        "filename": "tema1.pdf",
        "asignatura": "logica-difusa",
        "tipo_documento": "apuntes",
        "tema": "Introducción",
        "chunk_id": 3
      },
      "score": 0.89
    }
  ],
  "total_results": 1,
  "query": "What is fuzzy logic?"
}
```

**Example:**
```bash
curl -X POST http://localhost:8081/search \
  -H "Content-Type: application/json" \
  -d '{"query": "membership functions", "asignatura": "logica-difusa"}'
```

---

## Indexing Endpoints

### POST `/index`

Index documents directly (without file upload).

**Request Body:**
```json
[
  {
    "content": "Document text content here...",
    "metadata": {
      "asignatura": "iv",
      "tipo_documento": "teoria",
      "tema": "Docker",
      "fuente": "Manual"
    },
    "doc_id": "docker-intro"
  }
]
```

**Response:**
```json
{
  "indexed_count": 5,
  "collection_name": "academic_documents",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### GET `/collection/info`

Get Qdrant collection statistics.

**Response:**
```json
{
  "name": "academic_documents",
  "vectors_count": 156,
  "points_count": 156,
  "status": "green"
}
```

---

## File Endpoints

### GET `/files`

List available files with optional filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `asignatura` | string | Filter by subject |
| `tipo_documento` | string | Filter by document type |

**Response:**
```json
{
  "files": [
    "logica-difusa/apuntes/tema1.pdf",
    "logica-difusa/ejercicios/practica1.md",
    "iv/teoria/docker.pdf"
  ],
  "total_files": 3
}
```

**Examples:**
```bash
# All files
curl http://localhost:8081/files

# Filter by subject
curl "http://localhost:8081/files?asignatura=logica-difusa"

# Filter by subject and type
curl "http://localhost:8081/files?asignatura=iv&tipo_documento=teoria"
```

---

### GET `/files/{filename}`

Get file information and metadata.

**Path Parameter:**
- `filename`: Relative path to file (e.g., `iv/teoria/docker.pdf`)

**Response:**
```json
{
  "filename": "iv/teoria/docker.pdf",
  "size_bytes": 245678,
  "size_kb": 239.92,
  "extension": "pdf",
  "modified": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `404`: File not found

---

### DELETE `/files/{filename}`

Delete a file from the documents directory.

**Path Parameter:**
- `filename`: Relative path to file

**Response:**
```json
{
  "message": "File 'iv/teoria/docker.pdf' deleted successfully"
}
```

**Errors:**
- `404`: File not found

---

### POST `/load-file`

Load an existing file and index it for semantic search.

**Request Body:**
```json
{
  "filename": "iv/teoria/docker.pdf",
  "metadata": {
    "asignatura": "iv",
    "tipo_documento": "teoria",
    "tema": "Introducción a Docker",
    "autor": "Profesor",
    "fuente": "PRADO UGR"
  }
}
```

**Response:**
```json
{
  "filename": "iv/teoria/docker.pdf",
  "doc_id": "docker",
  "indexed_count": 12,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `404`: File not found
- `400`: Unsupported file type

---

### POST `/upload`

Upload a file and optionally index it.

**Content-Type:** `multipart/form-data`

**Form Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `file` | binary | File to upload |
| `metadata` | string | JSON metadata (see below) |

**Metadata JSON:**
```json
{
  "asignatura": "iv",
  "tipo_documento": "ejercicios",
  "tema": "Docker Compose",
  "auto_index": true
}
```

| Metadata Field | Type | Required | Description |
|----------------|------|----------|-------------|
| `asignatura` | string | Yes | Subject name |
| `tipo_documento` | string | Yes | Document type |
| `tema` | string | No | Topic |
| `autor` | string | No | Author |
| `fecha` | string | No | Date (ISO format) |
| `fuente` | string | No | Source (default: "PRADO UGR") |
| `idioma` | string | No | Language (default: "es") |
| `licencia` | string | No | License |
| `auto_index` | boolean | No | Index after upload (default: true) |

**Response:**
```json
{
  "filename": "practica1.pdf",
  "doc_id": "practica1",
  "indexed_count": 8,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8081/upload \
  -F "file=@practica1.pdf" \
  -F 'metadata={"asignatura":"iv","tipo_documento":"ejercicios","auto_index":true}'
```

**Supported File Types:**
- `.txt` - Plain text
- `.pdf` - PDF documents
- `.md`, `.markdown` - Markdown
- `.docx` - Word documents (planned)

**Errors:**
- `400`: Unsupported file type or invalid metadata JSON

---

## Subject Endpoints

### GET `/subjects`

List all available subjects.

**Response:**
```json
{
  "subjects": [
    "iv",
    "logica-difusa",
    "ingenieria-software"
  ],
  "total_subjects": 3
}
```

---

### GET `/subjects/{asignatura}/types`

List document types for a specific subject.

**Path Parameter:**
- `asignatura`: Subject name

**Response:**
```json
{
  "asignatura": "iv",
  "document_types": [
    "teoria",
    "ejercicios",
    "examenes"
  ],
  "total_types": 3
}
```

---

## Metrics Endpoint

### GET `/metrics`

Prometheus metrics for monitoring.

**Response:** Prometheus text format

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",path="/search",status="200"} 42

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1",method="POST",path="/search"} 38
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad request (invalid input) |
| `404` | Resource not found |
| `500` | Internal server error |

---

## Data Models

### DocumentMetadata

```json
{
  "filename": "tema1.pdf",
  "asignatura": "logica-difusa",
  "tipo_documento": "apuntes",
  "fecha": "2025-10-14",
  "tema": "Conjuntos difusos",
  "autor": "Profesor",
  "fuente": "PRADO UGR",
  "idioma": "es",
  "chunk_id": 0,
  "licencia": "CC-BY"
}
```

### SearchResult

```json
{
  "content": "Document text content...",
  "metadata": { ... },
  "score": 0.89
}
```

---

## Related Documentation

- [Architecture](architecture.md) - System design
- [Embeddings](embeddings.md) - Embedding service
- [Vector Store](vector-store.md) - Qdrant integration
