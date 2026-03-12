---
adr: 0038
title: "Math Service como Microservicio Independiente"
date: 2026-03-17
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 38
---

# ADR 0038 — Math Service como Microservicio Independiente

## Status

Accepted

## Context

Los algoritmos de clustering implementados en `math_investigation/` (K-Means, FCM, NMF) necesitan ser expuestos como capacidades del sistema para dos funcionalidades concretas:

1. **Generación de FAQs**: Agrupar preguntas históricas de estudiantes por similitud semántica y generar respuestas representativas para cada clúster.
2. **Extracción de tópicos**: Aplicar NMF sobre los documentos RAG para descubrir los temas principales de una asignatura y visualizarlos como un mapa conceptual.

### Opciones de integración disponibles

La funcionalidad de clustering puede integrarse en el sistema de tres formas distintas:

| Opción | Descripción | Pro | Contra |
|--------|-------------|-----|--------|
| **A** | Integrar directamente en el chatbot | Zero overhead de red | Acopla lógica matemática con el agente |
| **B** | Integrar en el gateway (`backend`) | Centralizado | Gateway se convierte en monolito |
| **C** | Nuevo microservicio `math_service` | Separación de responsabilidades | Añade un servicio más |

### Contexto del TFG

El TFG de Informática exige demostrar **competencias en arquitectura de microservicios**. Disponer de un servicio dedicado permite:
- Documentar patrones de diseño (STD, health checks, métricas Prometheus) de forma independiente.
- Demostrar la integración de un módulo de investigación matemática en un sistema de producción.
- Desplegar y escalar el servicio matemático de forma independiente.

### Restricciones

- `math_investigation/` ya implementa los algoritmos desde cero (sin scikit-learn), siguiendo la restricción del TFG de Matemáticas.
- El chatbot consume MongoDB para perfiles de estudiantes y sesiones conversacionales.
- El sistema RAG almacena los fragmentos de documentos en Qdrant.
- Los recursos de hardware son limitados (entorno TFG): no se justifican colas de mensajes o buses de eventos.

## Decision

Implementar `math_service` como un **microservicio FastAPI independiente** (puerto 8083) que:

1. Importa e invoca los algoritmos de `math_investigation/` en tiempo de ejecución.
2. Lee datos de MongoDB (`conversations` collection) para extraer preguntas históricas de estudiantes.
3. Consulta el `rag_service` vía HTTP para obtener los fragmentos de documentos de una asignatura.
4. Expone tres grupos de endpoints: `/` (general), `/faqs` (generación y CRUD de FAQs), `/topics` (extracción e historial de tópicos).
5. Se instrumenta con Prometheus, logging JSON y correlation IDs coherentes con el resto de servicios.

### Arquitectura interna del servicio

```
math_service/
├── api.py            # FastAPI app, middlewares, routers
├── config.py         # pydantic-settings: MongoDB, Ollama, RAG URL
├── models/           # Pydantic models (FAQ, TopicResult, HealthCheck…)
├── routes/
│   ├── general.py    # GET /, GET /health
│   ├── faqs.py       # CRUD + POST /faqs/generate
│   └── topics.py     # POST /topics/extract, GET /topics/{subject}
└── services/
    ├── faq_service.py     # Orquesta FCM + LLM para generar FAQs
    ├── topic_service.py   # Orquesta NMF + TF-IDF para tópicos
    ├── clustering.py      # Wrapper de math_investigation.clustering
    └── nlp_client.py      # Cliente HTTP al RAG service
```

### Dependencias entre servicios

```
math_service ──(HTTP GET /documents)──▶ rag_service
math_service ──(read)──────────────────▶ MongoDB (conversations, faqs, topics)
backend      ──(HTTP proxy)────────────▶ math_service (opcional, vía /math/*)
```

## Consequences

### Pros

1. **Separación de responsabilidades**: Los algoritmos matemáticos están completamente aislados del agent loop del chatbot.
2. **Escalabilidad independiente**: El microservicio puede escalarse o reiniciarse sin afectar las conversaciones activas.
3. **Demostración académica**: Muestra la integración real de investigación matemática (TFG Mates) en un sistema de producción (TFG Informática).
4. **Reusabilidad**: El endpoint `/topics/extract` puede ser consumido por el chatbot, el gateway o herramientas externas.
5. **Observabilidad**: Métricas Prometheus propias, logs JSON con correlation IDs, health check detallado.

### Cons

1. **Complejidad operacional**: Un servicio adicional que mantener, construir y desplegar.
2. **Latencia de red**: Llamadas HTTP entre `math_service` y `rag_service`/MongoDB añaden latencia frente a integración directa.
3. **Consistencia eventual**: Si el `rag_service` no está disponible, `math_service` regresa `status: degraded`.

### Mitigaciones

- Health check en `/health` verifica MongoDB, Ollama y RAG service, permitiendo alertas tempranas.
- Dependencias Docker Compose (`depends_on: mongo, ollama, rag_service`) garantizan orden de arranque correcto.
- Timeout razonable en cliente HTTP (`httpx`) para evitar bloqueos indefinidos.

## Alternatives Considered

### 1. Integrar clustering en el chatbot

**Rechazado**

- El chatbot ya tiene alta complejidad (LangGraph, herramientas, checkpointing).
- Mezclar lógica matemática con el agent loop dificulta el testing unitario de ambas partes.
- Los perfiles de estudiante son responsabilidad del chatbot; las FAQs son contenido editorial.

### 2. Integrar clustering en el backend gateway

**Rechazado**

- El gateway es responsable de autenticación, autorización y enrutamiento.
- Añadir lógica de negocio matemática viola el principio de responsabilidad única.
- Dificultaría testear independientemente los algoritmos de clustering.

### 3. Script batch (offline, sin API)

**Considerado para entornos de producción sin tiempo real**

- Los profesores requieren generación de FAQs bajo demanda desde el dashboard.
- No viable como arquitectura de microservicios interactiva.
- Candidato a implementación futura para pipelines de reentrenamiento programados.

## Implementation

### Archivos principales

| Archivo | Propósito |
|---------|-----------|
| `math_service/api.py` | Aplicación FastAPI con routers y middlewares |
| `math_service/config.py` | Configuración via `pydantic-settings` |
| `math_service/routes/faqs.py` | Endpoints CRUD + generación de FAQs |
| `math_service/routes/topics.py` | Extracción e historial de tópicos |
| `math_service/services/faq_service.py` | Lógica de orquestación FCM → LLM |
| `math_service/services/topic_service.py` | Lógica de orquestación NMF → mapa conceptual |
| `math_service/Dockerfile` | Imagen Docker basada en Python 3.13-slim |
| `docker-compose.yml` | Servicio `math_service` en puerto `8083` |

### Variables de entorno

| Variable | Default Docker | Descripción |
|----------|---------------|-------------|
| `MONGO_HOSTNAME` | `mongo` | Host MongoDB |
| `MONGO_PORT` | `27017` | Puerto MongoDB |
| `OLLAMA_HOST` | `ollama` | Host Ollama (embeddings) |
| `RAG_SERVICE_URL` | `http://rag_service:8081` | URL del servicio RAG |
| `API_PORT` | `8083` | Puerto del servicio |

## References

- [ADR 0003](0003-use-docker-for-containers.md) — Uso de Docker para contenedores
- [ADR 0029](0029-shared-mongodb-with-separate-collections.md) — MongoDB compartido con colecciones separadas
- [ADR 0036](0036-clustering-algorithms.md) — Algoritmos de clustering (FCM vs K-Means)
- [docs/services/math_service.md](../../services/math_service.md) — Documentación completa del servicio
