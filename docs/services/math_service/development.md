# Math Service — Desarrollo local

Guía completa para desarrollar el Math Service localmente, incluyendo setup, tests y flujo de trabajo.

## Prerrequisitos

- **Python 3.13+**
- **uv** (gestor de paquetes recomendado)
- **MongoDB** corriendo (local o via Docker)
- **Ollama** con modelo `nomic-embed-text` instalado
- **RAG Service** arrancado (para endpoints de topics)

### Instalar Ollama y el modelo de embeddings

```bash
# Instalar Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar el modelo de embeddings
ollama pull nomic-embed-text
```

---

## Setup del entorno

### 1. Crear entorno virtual

```bash
# Desde la raíz del proyecto
uv venv
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
# Instalar el servicio y sus dependencias
uv pip install -e ./math_service

# Instalar el módulo de investigación matemática (requerido)
uv pip install -e ./math_investigation

# Instalar dependencias de desarrollo (tests, linting)
uv pip install -e "./math_service[dev]"
```

### 3. Crear archivo `.env`

```bash
cp .env.example .env  # si existe, o crear manualmente
```

Contenido mínimo para desarrollo:

```env
# MongoDB
MONGO_HOSTNAME=localhost
MONGO_PORT=27017

# Ollama
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=nomic-embed-text

# RAG Service
RAG_SERVICE_URL=http://localhost:8081

# Mistral (opcional - para títulos descriptivos de tópicos)
# MISTRAL_API_KEY=tu_api_key_aqui
```

### 4. Arrancar MongoDB en local

Con Docker (más sencillo):

```bash
docker run -d --name mongo-local -p 27017:27017 mongo:7
```

O con Docker Compose (stack completo):

```bash
docker compose up -d mongo ollama rag_service
```

---

## Arrancar el servidor de desarrollo

```bash
# Desde la raíz del proyecto
python -m math_service
```

El servidor arrancará en `http://localhost:8083` con recarga automática activada.

Verificar que está funcionando:

```bash
curl http://localhost:8083/health
```

### Con uvicorn directamente

```bash
uvicorn math_service.api:app --reload --host 0.0.0.0 --port 8083
```

---

## Ejecutar tests

### Tests unitarios

```bash
# Ejecutar todos los tests del servicio
pytest math_service/tests/ -v

# Solo tests unitarios
pytest math_service/tests/ -m unit -v

# Con cobertura
pytest math_service/tests/ --cov=math_service --cov-report=term-missing

# Un archivo concreto
pytest math_service/tests/test_clustering.py -v
```

### Tests de integración (requieren servicios arrancados)

```bash
pytest tests/ -m integration -k "math" -v
```

### Ver informe HTML de cobertura

```bash
pytest math_service/tests/ --cov=math_service --cov-report=html
open htmlcov/index.html
```

---

## Estructura de tests

```
math_service/tests/
├── __init__.py
├── test_api_faqs.py      # Tests de endpoints /faqs con TestClient
├── test_api_topics.py    # Tests de endpoints /topics con TestClient
├── test_clustering.py    # Tests unitarios de clustering.py y fcm.py
└── test_faq.py           # Tests de FAQService (con MongoDB mockeado)
```

### Patrón de fixtures

Los tests usan `mongomock` para no necesitar MongoDB real:

```python
import mongomock
import pytest
from fastapi.testclient import TestClient
from math_service.api import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_mongo():
    with mongomock.patch(servers=(("localhost", 27017),)):
        yield
```

### Ejemplo de test de endpoint

```python
def test_generate_faqs_no_questions(client, mock_mongo):
    response = client.post("/faqs/generate", json={"subject": "asignatura_sin_preguntas"})
    assert response.status_code == 500
    assert "No questions found" in response.json()["detail"]
```

### Ejemplo de test unitario de clustering

```python
import numpy as np
from math_service.services.clustering import get_optimal_k, get_closest_to_centroid

def test_get_optimal_k_returns_valid_k():
    X = np.random.rand(50, 10)
    k = get_optimal_k(X, max_k=8)
    assert 2 <= k <= 8

def test_get_closest_to_centroid():
    X = np.array([[1, 0], [1.1, 0.1], [5, 5], [4.9, 5.1]])
    labels = np.array([0, 0, 1, 1])
    centroids = np.array([[1.05, 0.05], [4.95, 5.05]])
    indices = get_closest_to_centroid(X, labels, centroids)
    assert len(indices) == 2
```

---

## Añadir un nuevo endpoint

### 1. Definir modelos Pydantic

En `math_service/models/__init__.py`:

```python
class MiNuevoRequest(BaseModel):
    subject: str
    parametro: int = 10

class MiNuevoResponse(BaseModel):
    status: str
    resultado: list[str]
```

### 2. Implementar la lógica de negocio

En `math_service/services/mi_servicio.py`:

```python
class MiServicio:
    def __init__(self):
        self.client = MongoClient(settings.get_mongo_uri())
        self.db = self.client[settings.db_name]

    def close(self):
        self.client.close()

    def procesar(self, subject: str, parametro: int) -> dict:
        # Lógica aquí
        return {"status": "success", "resultado": []}
```

### 3. Crear el router

En `math_service/routes/mi_router.py` o añadir al router existente:

```python
from fastapi import APIRouter
from math_service.models import MiNuevoRequest, MiNuevoResponse
from math_service.services.mi_servicio import MiServicio

router = APIRouter(prefix="/mi-recurso", tags=["mi-recurso"])

@router.post("/accion", response_model=MiNuevoResponse)
def mi_accion(request: MiNuevoRequest) -> MiNuevoResponse:
    service = MiServicio()
    try:
        result = service.procesar(request.subject, request.parametro)
        return MiNuevoResponse(**result)
    finally:
        service.close()
```

### 4. Registrar el router en `api.py`

```python
from math_service.routes.mi_router import router as mi_router
app.include_router(mi_router)
```

### 5. Escribir tests

```python
# math_service/tests/test_api_mi_recurso.py
def test_mi_accion(client, mock_mongo):
    response = client.post("/mi-recurso/accion", json={"subject": "iv"})
    assert response.status_code == 200
```

---

## Linting y formateo

El proyecto usa `ruff`, `black` e `isort` (configurados en `pyproject.toml`):

```bash
# Verificar errores de estilo
ruff check math_service/

# Formatear código
black math_service/

# Ordenar imports
isort math_service/

# Todo a la vez (con pre-commit)
pre-commit run --all-files
```

---

## Depuración

### Logs estructurados

El servicio emite logs JSON. Para desarrollo, puede ser más legible desactivarlos:

```bash
LOG_LEVEL=DEBUG python -m math_service
```

### Depurar requests HTTP a Ollama/RAG

Usar `httpx` con logging habilitado:

```python
import logging
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

### Inspeccionar MongoDB directamente

```bash
# Con mongosh
mongosh "mongodb://localhost:27017/tfg_chatbot"

# Listar FAQs
db.faqs.find().pretty()

# Listar extracciones de tópicos
db.topic_results.find({}, {topics: 1, created_at: 1}).pretty()
```

### Probar algoritmos en modo interactivo

```python
# python o ipython desde la raíz del proyecto
from math_investigation.clustering.fcm import FuzzyCMeans
import numpy as np

X = np.random.rand(100, 50)
fcm = FuzzyCMeans(n_clusters=5, random_state=42)
fcm.fit(X)
print(fcm.labels_)
```

---

## Comandos útiles

```bash
# Arrancar el servicio
python -m math_service

# Ejecutar todos los tests con verbose
pytest math_service/tests/ -v

# Generar FAQs para una asignatura de prueba
curl -X POST http://localhost:8083/faqs/generate \
  -H "Content-Type: application/json" \
  -d '{"subject": "iv", "min_cluster_size": 2}'

# Extraer tópicos
curl -X POST http://localhost:8083/topics/extract \
  -H "Content-Type: application/json" \
  -d '{"subject": "iv"}'

# Listar FAQs generadas
curl http://localhost:8083/faqs/iv | python3 -m json.tool

# Health check
curl http://localhost:8083/health | python3 -m json.tool

# Ver métricas Prometheus
curl http://localhost:8083/metrics
```

---

## Integración con el stack completo

Para probar el Math Service integrado con todos los microservicios:

```bash
# Arrancar todos los servicios
docker compose up -d

# El Math Service estará en
curl http://localhost:8083/health
```

Ver [deployment.md](./deployment.md) para detalles de despliegue.
