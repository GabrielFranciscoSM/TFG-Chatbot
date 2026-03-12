---
layout: default
title: Sprint Planning 7 - Integración Matemática en Plataforma
parent: Sprints
grand_parent: DevLog
nav_order: 7
---

# Sprint Planning - Sprint 7 (Integración Matemática en Plataforma)

## Información General

- **Sprint:** Sprint 7
- **Fecha de inicio:** 25 de febrero de 2026
- **Fecha de finalización:** 18 de marzo de 2026
- **Duración:** 3 semanas
- **Equipo:** Gabriel Francisco

---

## Objetivo del Sprint (Sprint Goal)

> Integrar los componentes matemáticos desarrollados en `math_investigation/` (generación de FAQs y extracción de tópicos) como un nuevo microservicio productivo (`math_service/`), accesible para profesores y alumnos a través de la interfaz web.

En el Sprint 6 se implementaron y validaron algoritmos de clustering textual (NMF, K-Means, FCM) como módulos de investigación independientes. Este sprint los convierte en un microservicio integrado en la plataforma:

1. **Generación de FAQs:** El profesor puede generar preguntas frecuentes para cada asignatura a partir de las preguntas de sus alumnos, y estas se publican automáticamente para que los alumnos puedan consultarlas.
2. **Extracción y visualización de tópicos:** El profesor puede extraer los tópicos latentes de los documentos subidos a una asignatura, visualizar los clusters generados por NMF y explorar el mapa de conceptos de forma interactiva.

---

## Arquitectura

El nuevo servicio sigue el patrón de microservicios existente (API Gateway + Servicios):

```
Frontend → Backend (Gateway) → math_service (NMF, K-Means, FCM)
                              → chatbot (LangGraph/LLM)
                              → rag_service (Qdrant/Embeddings)
                              → MongoDB
```

El `math_service/` será un servicio independiente con su propio `Dockerfile`, `api.py`, dependencias y tests, análogo a `chatbot/` y `rag_service/`. El `backend/` actuará como proxy/gateway para las peticiones de FAQs y tópicos, añadiendo autenticación y autorización.

El `math_service/` consume del `rag_service` (para obtener chunks y embeddings) y de MongoDB (para obtener las preguntas de los alumnos). Los algoritmos provienen de `math_investigation/`, que se importa como dependencia interna.

---

## Alcance

### Nuevo Microservicio: `math_service/`
- **Estructura:** `math_service/api.py`, `math_service/config.py`, `math_service/Dockerfile`, `math_service/services/`, `math_service/models/`, `math_service/tests/`.
- **Docker:** Nuevo contenedor en `docker-compose.yml` con acceso a `rag_service`, `mongo` y `ollama`.
- **Dependencia interna:** Importa algoritmos de `math_investigation/` (NMF, K-Means, FCM, TF-IDF).

### Generación de FAQs (Profesor → Alumno)
- **Pipeline:** Recopilar preguntas de alumnos por asignatura (MongoDB) → Embeddings (vía `rag_service`/`ollama`) → Clustering (K-Means/FCM) → Centroides → LLM genera pregunta+respuesta representativa.
- **API `math_service`:** Endpoints para lanzar la generación y obtener FAQs.
- **API Gateway (`backend`):** Proxy con autenticación, endpoints para CRUD de FAQs (editar, publicar, eliminar).
- **Persistencia:** Colección MongoDB `faqs` vinculada a `subject_id`.
- **UI Profesor:** Panel para ejecutar la generación y revisar/editar las FAQs antes de publicarlas.
- **UI Alumno:** Sección de "Preguntas frecuentes" visible en cada asignatura.

### Extracción de Tópicos (Profesor)
- **Pipeline:** Obtener chunks del RAG por asignatura → TF-IDF → NMF → Tópicos con palabras clave → Mapa de conceptos.
- **API `math_service`:** Endpoints para lanzar la extracción y consultar resultados.
- **API Gateway (`backend`):** Proxy con autenticación.
- **Persistencia:** Colección MongoDB `topic_results` con resultados por asignatura.
- **UI Profesor:** Dashboard con lista de tópicos, heatmap documento-tópico y mapa de conceptos interactivo.

### Stack Tecnológico
- **Algoritmos:** `math_investigation/clustering/` (K-Means, FCM), `math_investigation/topic_modeling/` (NMF), `math_investigation/nlp/` (TF-IDF)
- **Embeddings:** Ollama `nomic-embed-text` (vía `rag_service` o acceso directo a Ollama)
- **Backend Gateway:** FastAPI (`backend/routers/`) — proxy + auth
- **Math Service:** FastAPI (`math_service/api.py`) — lógica de negocio
- **Frontend:** React + TypeScript (Vite, shadcn/ui)
- **Persistencia:** MongoDB (colecciones `faqs`, `topic_results`)
- **Visualización Frontend:** Recharts / D3.js para heatmaps y mapa de conceptos

---

## Historias de Usuario (HU) asociadas

- **HU #119** — [HU 020] Como profesor quiero generar preguntas frecuentes automáticamente a partir de las preguntas de mis alumnos para que estos puedan consultar las dudas más comunes de la asignatura.
- **HU #120** — [HU 021] Como alumno quiero consultar las preguntas frecuentes de mi asignatura para resolver dudas comunes sin esperar al profesor.
- **HU #121** — [HU 022] Como profesor quiero extraer y visualizar los tópicos de los documentos subidos a una asignatura para entender la estructura temática del material y detectar lagunas de contenido.

---

## Criterios de Aceptación

### Generación de FAQs (HU #20, #21)

- **Math Service — Pipeline de FAQs (HU #20):**
  - [ ] Endpoint `POST /faqs/generate` recibe `subject_id`, ejecuta pipeline completo y devuelve FAQs generadas.
  - [ ] Endpoint `GET /faqs/{subject_id}` devuelve las FAQs almacenadas de una asignatura.
  - [ ] El pipeline recopila preguntas de MongoDB, genera embeddings, ejecuta clustering y genera FAQ representativa por cluster vía LLM.

- **Gateway — CRUD de FAQs (HU #20):**
  - [ ] Endpoint `POST /professor/subjects/{id}/faqs/generate` (proxy al `math_service` con autenticación de profesor).
  - [ ] Endpoint `GET /professor/subjects/{id}/faqs` devuelve las FAQs de la asignatura.
  - [ ] Endpoint `PUT /professor/subjects/{id}/faqs/{faq_id}` permite al profesor editar una FAQ.
  - [ ] Endpoint `DELETE /professor/subjects/{id}/faqs/{faq_id}` permite eliminar una FAQ.
  - [ ] Endpoint `PATCH /professor/subjects/{id}/faqs/{faq_id}/publish` toggle de publicación.

- **UI Profesor — Panel de FAQs (HU #20):**
  - [ ] Botón "Generar FAQs" en la vista de asignatura del profesor.
  - [ ] Indicador de progreso durante la generación.
  - [ ] Lista de FAQs generadas con opción de editar, eliminar o publicar.

- **UI Alumno — FAQs públicas (HU #21):**
  - [ ] Sección "Preguntas Frecuentes" visible en la interfaz del chat de cada asignatura.
  - [ ] Las FAQs se muestran como acordeón expandible con pregunta/respuesta.
  - [ ] Solo se muestran las FAQs marcadas como publicadas por el profesor.

### Extracción de Tópicos (HU #22)

- **Math Service — Pipeline de Tópicos (HU #22):**
  - [ ] Endpoint `POST /topics/extract` recibe `subject_id` y `n_components`, ejecuta pipeline NMF.
  - [ ] Endpoint `GET /topics/{subject_id}` devuelve tópicos extraídos con palabras clave, distribución y mapa de conceptos.

- **Gateway — Proxy de Tópicos (HU #22):**
  - [ ] Endpoint `POST /professor/subjects/{id}/topics/extract` (proxy con auth).
  - [ ] Endpoint `GET /professor/subjects/{id}/topics` devuelve resultados.

- **UI Profesor — Dashboard de Tópicos (HU #22):**
  - [ ] Vista de tópicos extraídos con las palabras clave de cada tópico (tags/chips).
  - [ ] Heatmap de distribución documento-tópico.
  - [ ] Mapa de conceptos interactivo (grafo de relaciones entre tópicos).
  - [ ] Selector de número de tópicos (k) con opción de re-ejecutar la extracción.

---

## Tareas (desglose)

### Semana 1: Microservicio `math_service/` + Pipelines

1. **Scaffolding del `math_service/`**
   - Crear estructura: `math_service/__init__.py`, `api.py`, `config.py`, `Dockerfile`, `pyproject.toml`.
   - Añadir contenedor a `docker-compose.yml` con acceso a `mongo`, `ollama`, `rag_service`.
   - Configurar logging estructurado y health check (`/health`).
   - Verificar que el contenedor arranca correctamente y se comunica con los demás servicios.

2. **Pipeline de FAQ Generation (`math_service/services/faq_service.py`)**
   - Implementar recopilación de preguntas de alumnos desde MongoDB (colección `conversations`).
   - Obtener embeddings de las preguntas vía Ollama (`nomic-embed-text`) o `rag_service`.
   - Adaptar `KMeans` y `FuzzyCMeans` de `math_investigation/clustering/` para producción.
   - Usar LLM para generar pregunta representativa + respuesta a partir del centroide de cada cluster.
   - Persistir FAQs en MongoDB (colección `faqs`).

3. **Pipeline de Extracción de Tópicos (`math_service/services/topic_service.py`)**
   - Obtener chunks del RAG por asignatura vía `rag_service` API.
   - Adaptar TF-IDF de `math_investigation/nlp/` y NMF de `math_investigation/topic_modeling/`.
   - Generar mapa de conceptos (`concept_map`) con estructura de grafo.
   - Persistir resultados en MongoDB (colección `topic_results`).

### Semana 2: Gateway + Frontend FAQs

4. **API Endpoints en `math_service/`**
   - Crear `math_service/routes/faqs.py` con endpoints de generación y consulta.
   - Crear `math_service/routes/topics.py` con endpoints de extracción y consulta.
   - Modelos Pydantic en `math_service/models/`.
   - Tests unitarios.

5. **Gateway — Proxy en Backend**
   - Crear `backend/routers/faqs.py` con proxy autenticado al `math_service`.
   - Extender `backend/routers/professor.py` o crear `backend/routers/topics.py` para proxy de tópicos.
   - Añadir `MATH_SERVICE_URL` a `backend/config.py`.
   - Tests unitarios del gateway.

6. **Frontend — Panel de FAQs del Profesor**
   - Crear componente `FaqManager` en la vista de asignatura del profesor.
   - Botón de generación con estado de carga.
   - Lista editable de FAQs con toggle de publicación.

7. **Frontend — FAQs Públicas del Alumno**
   - Crear componente `FaqSection` en la pantalla de chat por asignatura.
   - Acordeón expandible con pregunta/respuesta.
   - Diseño responsive y consistente con el sistema de diseño existente.

### Semana 3: Frontend Tópicos + Tests + Documentación

8. **Frontend — Dashboard de Tópicos del Profesor**
   - Crear componente `TopicsDashboard` en el panel del profesor.
   - Lista de tópicos con palabras clave (tags/chips).
   - Heatmap de distribución documento-tópico (Recharts o similar).
   - Mapa de conceptos interactivo (grafo con D3.js o react-force-graph).
   - Selector de parámetros (k, función de coste) para re-ejecutar.

9. **Tests de Integración y E2E**
   - Tests del `math_service` (pipelines FAQ y tópicos).
   - Tests del gateway (proxy autenticado).
   - Test E2E: profesor genera FAQs → alumno las consulta.
   - Test E2E: profesor extrae tópicos → visualiza resultados.

10. **Documentación y ADRs**
    - ADR: Decisión de crear `math_service` como microservicio independiente.
    - ADR: Integración de algoritmos `math_investigation/` en producción.
    - Documentación del servicio (`docs/services/math_service.md`).
    - Actualizar README con las nuevas funcionalidades.

---

## Estimaciones (puntos)

- Scaffolding `math_service/`: 3
- Pipeline FAQ Generation: 8
- Pipeline Extracción Tópicos: 8
- API Endpoints `math_service`: 5
- Gateway Proxy (Backend): 5
- Frontend FAQs Profesor: 5
- Frontend FAQs Alumno: 3
- Frontend Dashboard Tópicos: 8
- Tests de Integración/E2E: 5
- Documentación y ADRs: 3
- **Total aproximado:** 53 puntos

---

## Riesgos y dependencias

- **Rendimiento de clustering en producción:** Los algoritmos de `math_investigation/` están diseñados para análisis offline; pueden necesitar optimización para volúmenes grandes. Se debe implementar procesamiento asíncrono con indicadores de progreso.
- **Disponibilidad de datos reales:** Si no hay suficientes preguntas de alumnos acumuladas, la generación de FAQs puede dar resultados pobres. Se necesita un umbral mínimo de preguntas.
- **Nuevo contenedor Docker:** Incrementa el uso de recursos del sistema. Mitigación: el servicio solo se invoca bajo demanda.
- **Dependencia del RAG Service:** La extracción de tópicos depende de obtener los chunks del RAG service vía API.
- **Complejidad del frontend de tópicos:** La visualización interactiva del mapa de conceptos (grafo) puede ser técnicamente compleja.
- **Importación de `math_investigation/`:** El `math_service` necesita acceso a los módulos de `math_investigation/`. Se debe configurar como dependencia en `pyproject.toml` o montar como volumen en Docker.
- **Dependencia de Sprint 6:** Los módulos `math_investigation/` deben estar mergeados en `main`.

---

## Definition of Done

- El `math_service/` arranca como contenedor Docker y responde al health check.
- El profesor puede generar FAQs automáticas para cada asignatura con un clic.
- Las FAQs generadas son editables y publicables por el profesor.
- Los alumnos ven las FAQs publicadas en la interfaz de chat de su asignatura.
- El profesor puede extraer tópicos de los documentos subidos y visualizarlos.
- El dashboard de tópicos muestra palabras clave, heatmap y mapa de conceptos.
- Los tests unitarios y de integración verifican los pipelines completos.
- Los ADRs correspondientes están documentados.

---

## Backlog del sprint (prioridad)

- Issue #119 — [HU 020] Generación automática de FAQs para profesores. Enlace: [#119](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/119)
- Issue #120 — [HU 021] Consulta de FAQs públicas para alumnos. Enlace: [#120](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/120)
- Issue #121 — [HU 022] Extracción y visualización de tópicos para profesores. Enlace: [#121](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/121)

---

## GitHub Issues a crear

### Historias de Usuario

1. **[HU 020] Generación automática de FAQs** — [#119](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/119)
2. **[HU 021] Consulta de FAQs por alumnos** — [#120](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/120)
3. **[HU 022] Extracción y visualización de tópicos** — [#121](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/121)

### Tareas Técnicas

4. **[TASK] Scaffolding del microservicio `math_service/`** — [#122](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/122)
5. **[TASK] Pipeline de FAQ Generation** — [#123](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/123)
6. **[TASK] Pipeline de Extracción de Tópicos (NMF)** — [#124](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/124)
7. **[TASK] API REST del `math_service`** — [#125](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/125)
8. **[TASK] Gateway — Proxy autenticado en Backend** — [#126](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/126)
9. **[TASK] Frontend — Panel de FAQs del Profesor** — [#127](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/127)
10. **[TASK] Frontend — FAQs Públicas del Alumno** — [#128](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/128)
11. **[TASK] Frontend — Dashboard de Tópicos del Profesor** — [#129](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/129)
12. **[TASK] Tests de Integración y E2E** — [#130](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/130)
13. **[TASK] Documentación y ADRs** — [#131](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/131)

---

**Elaborado por:** Gabriel Francisco

**Fecha:** 25 de febrero de 2026

---
