# RAG Service — Búsqueda semántica

RAG service implements retrieval-augmented search for the educational chatbot.
It provides:

- Semantic search using Ollama embeddings (nomic-embed-text)
- Qdrant as a vector database with metadata filtering
- Automatic chunking of long documents
- File ingestion (txt, pdf, markdown, docx) and upload endpoint
- FastAPI REST interface and Docker support

## Arquitectura

```
rag_service/
├── __init__.py              # Inicialización del paquete
├── api.py                   # FastAPI application (routes registration)
├── config.py                # Settings and configuration
├── models.py                # Pydantic models
├── embeddings/              # Embeddings & vector store services
│   ├── __init__.py
│   ├── embeddings.py
│   └── store.py
├── routes/                  # FastAPI route handlers
│   ├── __init__.py
│   ├── general.py
│   ├── files.py
│   ├── search_index.py
│   └── subjects.py
├── documents/               # Document processing utilities and loaders
│   ├── __init__.py
│   ├── document_processor.py
│   ├── file_loader.py
│   └── file_utils.py
├── pyproject.toml          # Project metadata & dependencies
├── Dockerfile               # Docker image for rag_service
├── .env.example             # Example environment variables
├── upload_example.py        # Example script to upload documents
├── docs/                    # Human-facing documentation (markdown)
└── tests/                   # Unit and integration tests
```

## Instalación

### Con Docker Compose (recomendado para desarrollo)

Run Qdrant, Ollama and rag-service together using the top-level compose file:

```bash
# From repository root
docker-compose up --build qdrant ollama rag-service
```

# Desarrollo local (sin Docker)

```bash
cd rag_service

# Create a virtualenv and install deps from pyproject.toml
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install ./rag_service

# Copy example env and run
cp .env.example .env
python -m uvicorn rag_service.api:app --reload --port 8081
```

## Uso básico

Indexar documentos (API):

```python
import requests

documents = [{
    "content": "Ejemplo...",
    "metadata": {
        "asignatura": "Lógica Difusa",
        "tipo_documento": "apuntes",
        "fecha": "2025-10-14",
    }
}]

resp = requests.post("http://localhost:8081/index", json=documents)
print(resp.json())
```

Search example:

```python
import requests

q = {"query": "¿Qué es un conjunto difuso?", "top_k": 5}
resp = requests.post("http://localhost:8081/search", json=q)
print(resp.json())
```

### Endpoints disponibles

- `GET /` - Service info
- `GET /health` - Health check (includes Qdrant connectivity)
- `POST /search` - Semantic search
- `POST /index` - Index documents (bulk)
- `GET /files` - List files in `DOCUMENTS_PATH` (optional filters)
- `GET /files/{filename}` - File info
- `POST /load-file` - Load + index file from `DOCUMENTS_PATH`
- `POST /upload` - Upload file and optionally auto-index
- `GET /collection/info` - Qdrant collection info

### Upload and load file

List files:

```bash
curl http://localhost:8081/files
```

Load a file (already present in `DOCUMENTS_PATH`):

```bash
curl -X POST http://localhost:8081/load-file -H "Content-Type: application/json" -d '{"filename":"tema1.pdf","metadata":{"asignatura":"Lógica Difusa","tipo_documento":"apuntes","fecha":"2025-10-17"}}'
```

### Copiar archivos al contenedor Docker

```bash
# Copiar un archivo al volumen del contenedor
docker cp mi_documento.pdf rag-service:/app/documents/

# Listar archivos en el contenedor
docker exec rag-service ls -la /app/documents/
```

## Configuración

Principales variables de entorno (ver `rag_service/config.py`):

| Variable | Descripción | Default |
|----------|-------------|---------|
| `QDRANT_HOST` | Host de Qdrant | `qdrant` |
| `QDRANT_PORT` | Puerto de Qdrant | `6333` |
| `OLLAMA_HOST` | Host de Ollama | `ollama` |
| `OLLAMA_PORT` | Puerto de Ollama | `11434` |
| `OLLAMA_EMBEDDING_MODEL` | Modelo de embeddings | `nomic-embed-text` |
| `RAG_TOP_K` | Resultados por defecto | `5` |
| `RAG_SIMILARITY_THRESHOLD` | Umbral de similitud | `0.7` |
| `CHUNK_SIZE` | Tamaño de chunks (caracteres) | `1000` |
| `CHUNK_OVERLAP` | Overlap entre chunks | `200` |
| `DOCUMENTS_PATH` | Ruta de documentos | `/app/documents` |

## Modelo de Metadata

Cada documento indexado debe incluir:

```python
{
    "asignatura": str,          # Ej: "Lógica Difusa"
    "tipo_documento": str,      # Ej: "apuntes", "ejercicios", "examen"
    "fecha": str,               # ISO format: "2025-10-14"
    "tema": str,                # Ej: "Conjuntos difusos"
    "autor": str,               # Opcional
    "fuente": str,              # Ej: "PRADO UGR"
    "idioma": str,              # "es" o "en"
}
```

## Testing

Run unit tests for the RAG service:

```bash
pytest rag_service/tests
```

For integration tests, see `rag_service/docs/INTEGRATION_TESTS.md`.

## Desarrollo

When developing, update models in `rag_service/models.py`, add logic to `rag_service/embeddings` or `rag_service/embeddings/store.py` and add tests under `rag_service/tests/`.

Enable debug logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Roadmap

- Implementar chunking semántico avanzado
- Añadir soporte para PDFs y DOCX (if not already wired)
- Implementar caché de embeddings
- Añadir métricas y monitoring
- Implementar rate limiting and authentication
- Complete integration test suite (see docs)

## Documentación adicional

- **Chunking de Documentos:** `rag_service/docs/CHUNKING.md`
- **API Reference:** `rag_service/docs/API.md`
- **CI Guide:** `rag_service/docs/CI.md`
- **Integration Tests:** `rag_service/docs/INTEGRATION_TESTS.md`
- **Deployment:** `rag_service/docs/DEPLOYMENT.md`

See `devLog/notas/Project_docs_plan.md` for the broader documentation roadmap.

## Referencias

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain RAG](https://python.langchain.com/docs/tutorials/rag/)
- [Ollama Python](https://github.com/ollama/ollama-python)
