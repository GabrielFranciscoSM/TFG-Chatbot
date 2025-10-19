# RAG - 🔍 **Búsqueda semántica** usando embeddings de Ollama (nomic-embed-text)
- 📊 **Base de datos vectorial** Qdrant con persistencia
- 🏷️ **Filtrado por metadata** (asignatura, tipo de documento, etc.)
- ✂️ **Chunking automático** de documentos largos con overlap inteligente
- 📁 **Carga de archivos** desde disco (TXT, PDF, DOCX, Markdown)
- 🚀 **API REST** con FastAPI
- 🐳 **Dockerizado** para fácil despliegue

Servicio de Retrieval-Augmented Generation para el chatbot educativo.

## Características

- 🔍 **Búsqueda semántica** usando embeddings de Ollama (nomic-embed-text)
- 📊 **Base de datos vectorial** Qdrant con persistencia
- 🏷️ **Filtrado por metadata** (asignatura, tipo de documento, etc.)
- ✂️ **Chunking automático** de documentos largos con overlap inteligente
- � **Carga de archivos** desde disco (TXT, PDF, DOCX)
- �🚀 **API REST** con FastAPI
- 🐳 **Dockerizado** para fácil despliegue

## Arquitectura

```
rag-service/
├── __init__.py              # Inicialización del paquete
├── api.py                   # FastAPI application
├── config.py                # Configuración y settings
├── models.py                # Modelos Pydantic
├── embeddings.py            # Servicio de embeddings (Ollama)
├── vector_store.py          # Operaciones con Qdrant
├── document_processor.py    # Chunking de documentos
├── file_loader.py           # Carga de archivos (TXT, PDF, DOCX)
├── example_usage.py         # Ejemplos de uso
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Imagen Docker
├── .env.example            # Ejemplo de configuración
├── documents/              # Directorio para documentos a procesar
├── docs/
│   └── CHUNKING.md         # Documentación sobre chunking
└── tests/                  # Tests unitarios
```

## Instalación

### Con Docker (recomendado)

```bash
# Desde el directorio raíz del proyecto
docker-compose up qdrant ollama rag-service
```

### Desarrollo local

```bash
cd rag-service

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
cp .env.example .env

# Ejecutar API
python -m uvicorn api:app --reload --port 8081
```

## Uso

### Indexar documentos

```python
import requests

documents = [
    {
        "content": "Un conjunto difuso es una generalización de un conjunto clásico...",
        "metadata": {
            "asignatura": "Lógica Difusa",
            "tipo_documento": "apuntes",
            "fecha": "2025-10-14",
            "tema": "Conjuntos difusos",
            "fuente": "PRADO UGR",
            "idioma": "es"
        }
    }
]

response = requests.post(
    "http://localhost:8081/index",
    json=documents
)
print(response.json())
```

### Búsqueda semántica

```python
import requests

query = {
    "query": "¿Qué es un conjunto difuso?",
    "asignatura": "Lógica Difusa",
    "tipo_documento": "apuntes",
    "top_k": 5
}

response = requests.post(
    "http://localhost:8081/search",
    json=query
)
print(response.json())
```

### Endpoints disponibles

- `GET /` - Información del servicio
- `GET /health` - Health check
- `POST /search` - Búsqueda semántica
- `POST /index` - Indexar documentos directamente
- `GET /files` - Listar archivos disponibles en el directorio de documentos
- `GET /files/{filename}` - Información de un archivo específico
- `POST /load-file` - Cargar e indexar un archivo desde el directorio de documentos
- `GET /collection/info` - Información de la colección

### Cargar archivos desde disco

```python
import requests

# Listar archivos disponibles
response = requests.get("http://localhost:8081/files")
print(response.json())

# Cargar e indexar un archivo
load_request = {
    "filename": "tema1-conjuntos-difusos.pdf",
    "metadata": {
        "asignatura": "Lógica Difusa",
        "tipo_documento": "apuntes",
        "fecha": "2025-10-17",
        "tema": "Conjuntos difusos",
        "fuente": "PRADO UGR",
        "idioma": "es"
    }
}

response = requests.post(
    "http://localhost:8081/load-file",
    json=load_request
)
print(response.json())
# Output: {"filename": "tema1-conjuntos-difusos.pdf", "doc_id": "tema1-conjuntos-difusos", "indexed_count": 5}
```

### Copiar archivos al contenedor Docker

```bash
# Copiar un archivo al volumen del contenedor
docker cp mi_documento.pdf rag-service:/app/documents/

# Listar archivos en el contenedor
docker exec rag-service ls -la /app/documents/
```

## Configuración

Variables de entorno principales:

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

```bash
# Ejecutar tests
pytest tests/

# Con coverage
pytest tests/ --cov=rag_service
```

## Desarrollo

### Añadir nuevas funcionalidades

1. Modifica los modelos en `models.py`
2. Implementa la lógica en `vector_store.py` o `embeddings.py`
3. Añade endpoints en `api.py`
4. Actualiza tests en `tests/`

### Logs

Los logs se configuran automáticamente en `api.py`. Para desarrollo:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Próximos pasos

- [ ] Implementar chunking semántico avanzado
- [ ] Añadir soporte para PDFs y DOCX
- [ ] Implementar caché de embeddings
- [ ] Añadir métricas y monitoring
- [ ] Implementar rate limiting
- [ ] Añadir autenticación
- [ ] Tests de integración completos

## Documentación Adicional

- **[Chunking de Documentos](docs/CHUNKING.md)** - Guía completa sobre chunking
- **[Ejemplos de Uso](example_usage.py)** - Ejemplos prácticos

## Referencias

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangChain RAG](https://python.langchain.com/docs/tutorials/rag/)
- [Ollama Python](https://github.com/ollama/ollama-python)
