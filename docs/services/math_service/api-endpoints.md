# Math Service — API Endpoints

Referencia completa de todos los endpoints del Math Service con ejemplos de request/response.

**Base URL**: `http://localhost:8083` (local) / `http://math_service:8083` (Docker Compose)

**OpenAPI interactivo**: `http://localhost:8083/docs`

---

## General

### `GET /`

Información de la API y estado del servicio.

**Response `200 OK`:**

```json
{
  "name": "Math Service",
  "version": "0.1.0",
  "description": "Mathematical analysis service (FAQ generation, topic extraction)",
  "status": "running"
}
```

---

### `GET /health`

Health check detallado que verifica la conectividad con todos los servicios dependientes.

**Response `200 OK` (healthy):**

```json
{
  "status": "healthy",
  "mongo_connected": true,
  "ollama_connected": true,
  "rag_service_connected": true,
  "message": "MongoDB: OK, Ollama: OK, RAG: OK"
}
```

**Response `200 OK` (degraded):**

```json
{
  "status": "degraded",
  "mongo_connected": true,
  "ollama_connected": false,
  "rag_service_connected": true,
  "message": "MongoDB: OK, Ollama: FAIL, RAG: OK"
}
```

> El servicio arranca igualmente cuando algún componente no está disponible. El endpoint siempre devuelve `200` y refleja el estado real en el cuerpo.

---

### `GET /metrics`

Métricas Prometheus del servicio (instrumentación automática de FastAPI).

Incluye: número de requests, latencias por endpoint, etc.

---

## FAQs

### `POST /faqs/generate`

Genera FAQs para una asignatura agrupando preguntas históricas de estudiantes con Fuzzy C-Means.

**Request Body:**

```json
{
  "subject": "iv",
  "min_cluster_size": 3
}
```

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `subject` | `string \| null` | `null` | Código de la asignatura. `null` procesa todas. |
| `min_cluster_size` | `int` | `3` | Mínimo de preguntas para considerar un clúster válido. |

**Flujo interno:**
1. Lee `conversations` en MongoDB filtrando por `subject` y `was_test != true`.
2. Genera embeddings de las preguntas via Ollama (`nomic-embed-text`).
3. Determina el k óptimo con el método del codo.
4. Aplica `SphericalFuzzyCMeans` (variante coseno de FCM).
5. Para cada clúster válido (≥ `min_cluster_size`), selecciona la pregunta más cercana al centroide.
6. Persiste las FAQs en MongoDB con `status: "draft"`.

**Response `200 OK`:**

```json
{
  "status": "success",
  "subject": "iv",
  "questions_analyzed": 87,
  "clusters_formed": 6,
  "faqs_generated": 5,
  "faqs": [
    "¿Cómo funciona Docker Compose?",
    "¿Qué diferencia hay entre imagen y contenedor?",
    "¿Cómo configuro variables de entorno en Docker?",
    "¿Qué es un volumen en Docker?",
    "¿Cómo depuro un contenedor en ejecución?"
  ]
}
```

**Response `500` — Sin preguntas:**

```json
{
  "detail": "No questions found to generate FAQs from."
}
```

**Response `500` — Ollama no disponible:**

```json
{
  "detail": "NLP service error: ..."
}
```

**Ejemplo cURL:**

```bash
curl -X POST http://localhost:8083/faqs/generate \
  -H "Content-Type: application/json" \
  -d '{"subject": "iv", "min_cluster_size": 3}'
```

---

### `GET /faqs/{subject_id}`

Lista las FAQs existentes para una asignatura, ordenadas por `cluster_size` descendente.

**Path Parameters:**
- `subject_id` — Código de la asignatura (e.g., `"iv"`)

**Response `200 OK`:**

```json
[
  {
    "id": "65f1a2b3c4d5e6f7a8b9c0d1",
    "question": "¿Cómo funciona Docker Compose?",
    "answer": "Docker Compose permite definir y ejecutar aplicaciones multi-contenedor...",
    "subject": "iv",
    "cluster_size": 12,
    "status": "published",
    "created_at": "2026-03-10T14:30:00Z"
  },
  {
    "id": "65f1a2b3c4d5e6f7a8b9c0d2",
    "question": "¿Qué diferencia hay entre imagen y contenedor?",
    "answer": "",
    "subject": "iv",
    "cluster_size": 8,
    "status": "draft",
    "created_at": "2026-03-10T14:30:00Z"
  }
]
```

> Las FAQs con `status: "draft"` han sido generadas pero aún no revisadas por el profesor.

**Ejemplo cURL:**

```bash
curl http://localhost:8083/faqs/iv
```

---

### `PUT /faqs/{subject_id}/{faq_id}`

Actualiza los campos de una FAQ existente.

**Path Parameters:**
- `subject_id` — Código de la asignatura
- `faq_id` — ObjectId de la FAQ en MongoDB

**Request Body** (todos los campos son opcionales):

```json
{
  "question": "¿Cómo funciona Docker Compose y cuándo debo usarlo?",
  "answer": "Docker Compose es una herramienta para definir aplicaciones multi-contenedor...",
  "status": "published"
}
```

**Response `200 OK`:**

```json
{
  "status": "success",
  "message": "FAQ updated"
}
```

**Response `400`:**

```json
{
  "detail": "Invalid FAQ ID"
}
```

**Response `404`:**

```json
{
  "detail": "FAQ not found"
}
```

**Ejemplo cURL:**

```bash
curl -X PUT http://localhost:8083/faqs/iv/65f1a2b3c4d5e6f7a8b9c0d1 \
  -H "Content-Type: application/json" \
  -d '{"answer": "Docker Compose es una herramienta...", "status": "published"}'
```

---

### `PATCH /faqs/{subject_id}/{faq_id}/publish`

Cambia el estado de una FAQ a `"published"`.

**Response `200 OK`:**

```json
{
  "status": "success",
  "message": "FAQ published"
}
```

**Ejemplo cURL:**

```bash
curl -X PATCH http://localhost:8083/faqs/iv/65f1a2b3c4d5e6f7a8b9c0d1/publish
```

---

### `PATCH /faqs/{subject_id}/{faq_id}/unpublish`

Cambia el estado de una FAQ a `"draft"`.

**Response `200 OK`:**

```json
{
  "status": "success",
  "message": "FAQ unpublished"
}
```

---

### `DELETE /faqs/{subject_id}/{faq_id}`

Elimina una FAQ por su ObjectId.

**Response `200 OK`:**

```json
{
  "status": "success",
  "message": "FAQ deleted"
}
```

**Response `404`:**

```json
{
  "detail": "FAQ not found"
}
```

**Ejemplo cURL:**

```bash
curl -X DELETE http://localhost:8083/faqs/iv/65f1a2b3c4d5e6f7a8b9c0d1
```

---

## Topics

### `POST /topics/extract`

Extrae los tópicos principales de los documentos de una asignatura usando NMF sobre fragmentos del RAG Service.

**Request Body:**

```json
{
  "subject": "iv",
  "vectorizer_type": "tfidf",
  "k": null,
  "cost_function": "frobenius"
}
```

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `subject` | `string` | requerido | Código de la asignatura |
| `vectorizer_type` | `"tfidf" \| "bow"` | `"tfidf"` | Tipo de vectorizador de texto |
| `k` | `int \| null` | `null` | Número de tópicos. `null` → selección automática por método del codo |
| `cost_function` | `"frobenius" \| "kl"` | `"frobenius"` | Función de coste para NMF |

**Flujo interno:**
1. Obtiene fragmentos del RAG Service via `POST /search` con `top_k=500`.
2. Vectoriza con TF-IDF o BoW (`max_features=500, min_df=2`).
3. Determina k automáticamente o usa el valor proporcionado.
4. Aplica NMF → matrices W (doc-tópico) y H (tópico-término).
5. Para cada tópico: extrae los 5 términos con mayor peso y genera un título descriptivo via Mistral API.
6. Construye el mapa conceptual (nodos: asignatura, tópicos, términos; aristas ponderadas).
7. Persiste el resultado en MongoDB (`topics` collection).

**Response `200 OK`:**

```json
{
  "status": "success",
  "subject": "iv",
  "clusters_formed": 5,
  "topics": [
    {
      "cluster": 0,
      "topic_name": "Contenedores Docker",
      "terms": ["docker", "contenedor", "imagen", "volumen", "compose"],
      "weight": 0.34
    },
    {
      "cluster": 1,
      "topic_name": "Redes y Comunicación",
      "terms": ["red", "puerto", "exposición", "bridge", "host"],
      "weight": 0.28
    }
  ],
  "concept_map": {
    "nodes": [
      {"id": "iv", "group": "subject", "label": "iv"},
      {"id": "Contenedores Docker", "group": "topic", "label": "Contenedores Docker"},
      {"id": "term_docker", "group": "term", "label": "docker"}
    ],
    "links": [
      {"source": "iv", "target": "Contenedores Docker", "value": 1.0},
      {"source": "Contenedores Docker", "target": "term_docker", "value": 0.85}
    ]
  },
  "doc_topic_matrix": [
    [0.8, 0.1, 0.05, 0.03, 0.02],
    [0.1, 0.7, 0.2, 0.0, 0.0]
  ],
  "created_at": "2026-03-12T10:30:00Z",
  "source_chunks": 142,
  "message": null
}
```

**Response `500` — Sin chunks:**

```json
{
  "detail": "No chunks found for subject"
}
```

**Response `500` — RAG no disponible:**

```json
{
  "detail": "RAG service unavailable: ..."
}
```

**Ejemplo cURL:**

```bash
curl -X POST http://localhost:8083/topics/extract \
  -H "Content-Type: application/json" \
  -d '{"subject": "iv", "vectorizer_type": "tfidf"}'
```

---

### `GET /topics/{subject_id}`

Lista las extracciones de tópicos históricas para una asignatura, ordenadas por `created_at` descendente.

**Path Parameters:**
- `subject_id` — Código de la asignatura

**Response `200 OK`:**

Lista de objetos `TopicResult` (misma estructura que el response de `POST /topics/extract`).

```json
[
  {
    "status": "success",
    "subject": "iv",
    "clusters_formed": 5,
    "topics": [...],
    "concept_map": {...},
    "doc_topic_matrix": [[...]],
    "created_at": "2026-03-12T10:30:00Z",
    "source_chunks": 142,
    "message": null
  }
]
```

**Ejemplo cURL:**

```bash
curl http://localhost:8083/topics/iv
```

---

## Resumen de endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información del servicio |
| `GET` | `/health` | Health check detallado |
| `GET` | `/metrics` | Métricas Prometheus |
| `POST` | `/faqs/generate` | Generar FAQs automáticas |
| `GET` | `/faqs/{subject_id}` | Listar FAQs de una asignatura |
| `PUT` | `/faqs/{subject_id}/{faq_id}` | Actualizar una FAQ |
| `PATCH` | `/faqs/{subject_id}/{faq_id}/publish` | Publicar una FAQ |
| `PATCH` | `/faqs/{subject_id}/{faq_id}/unpublish` | Despublicar una FAQ |
| `DELETE` | `/faqs/{subject_id}/{faq_id}` | Eliminar una FAQ |
| `POST` | `/topics/extract` | Extraer tópicos de una asignatura |
| `GET` | `/topics/{subject_id}` | Historial de extracciones de tópicos |

---

## Códigos de error comunes

| Código | Causa |
|--------|-------|
| `400` | ObjectId inválido en path |
| `404` | FAQ no encontrada (subject+id no existen en DB) |
| `500` | Error en pipeline (Ollama/RAG no disponible, sin datos) |
