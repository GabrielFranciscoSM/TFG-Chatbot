---
layout: default
title: Sprint Retrospective 6
parent: Sprints
grand_parent: DevLog
nav_order: 16
---

# Retrospectiva - Sprint 6 (28 Ene 2026 — 18 Feb 2026)

## Resumen ejecutivo

El Sprint 6 se centró en **Razonamiento, Adaptación y Clustering Textual**. Se implementaron capacidades avanzadas de Chain-of-Thought (CoT) para razonamiento visible, un clasificador híbrido de dificultad con 93.3% de accuracy, perfiles de conocimiento persistentes en MongoDB, y algoritmos de clustering textual (NMF, K-Means, FCM) validados con métricas externas (ARI=0.87, NMI=0.82). El sprint se completó en las 3 semanas planificadas, cumpliendo los 38 puntos estimados.

---

## Qué funcionó bien ✅

- **Chain-of-Thought Adaptativo (HU #15):**
  - Prompts CoT con formato JSON estructurado (`thinking` + `answer`) integrados en el grafo LangGraph.
  - Clasificación heurística previa que activa CoT solo para preguntas complejas, evitando latencia innecesaria.
  - ADR-0035 documenta la decisión de diseño.

- **Clasificador de Dificultad (HU #17):**
  - Enfoque híbrido (heurístico + embeddings) alcanza 93.3% de accuracy.
  - Tres niveles bien definidos: básico, intermedio, avanzado.
  - Prompts adaptativos por nivel mejoran la experiencia pedagógica.
  - Centroides entrenados con 388 preguntas etiquetadas y embeddings `nomic-embed-text` (768 dim).

- **Perfiles de Conocimiento (HU #16):**
  - `ProfileManager` con operaciones atómicas (upsert) en MongoDB.
  - Persistencia completa de conversaciones (`ConversationTurn`).
  - Endpoints admin para profesores (`/admin/profiles`, `/admin/conversations`).
  - Dashboard de progreso por estudiante con `StudentProgress` y `AggregatedStats`.
  - 14 tests unitarios con 100% passing.

- **Clustering Textual (Integración Matemática):**
  - Dataset sintético generado: 320 documentos, 3 temas disjuntos + documentos "trampa".
  - NMF: Frobenius supera KL-divergence (purity 0.77 vs 0.62). Coherencia UCI/UMass calculada manualmente.
  - K-Means + FCM: Comparación completa con métricas ARI=0.87, NMI=0.82, FPC=0.76.
  - Embeddings Ollama (`nomic-embed-text`) mejoran Silhouette Score (0.24 vs 0.13 con TF-IDF).
  - Visualizaciones t-SNE, wordclouds, heatmaps generadas.

- **Mejora del Tool de Test (RAG + Feedback):**
  - Búsqueda RAG proactiva antes de generar preguntas de test.
  - Feedback pedagógico enriquecido con contexto RAG como información complementaria.
  - Tests de integración creados para el flujo proactivo.

---

## Qué no funcionó / Qué salió mal ❌

- **Conflicto de Módulos (models/):**
  - Crear `chatbot/logic/models/` como paquete causó crash porque `models/` estaba en `.gitignore` (para modelos ML) y Python lo confundía con el archivo `models.py` existente.
  - Solución: Reorganizar en paquete con `__init__.py` que re-exporta todos los modelos.

- **Compatibilidad con Mistral:**
  - Errores de orden de mensajes y `ToolMessages` al integrar RAG proactivo en tests.
  - Requirió refactorización de `testGraph.py` para unificar feedback y preguntas en un solo mensaje.

- **Clasificador Solo-Embeddings:**
  - El clasificador basado únicamente en embeddings alcanzó solo 53.3% de accuracy, confundiendo niveles intermedio y avanzado.
  - Se resolvió con el enfoque híbrido (heurístico + embeddings).

- **Pydantic v2 Deprecations:**
  - `class Config` deprecado; se migró a `model_config = {...}` en varios modelos.

- **Pre-commit Hooks:**
  - Múltiples fallos por ruff/black durante la semana de refactorización de modelos.

---

## Lecciones aprendidas 🧠

- **Clasificadores Híbridos:** Combinar heurísticas rápidas con embeddings precisos ofrece el mejor balance entre velocidad y accuracy (93.3% vs 53.3% solo embeddings).

- **Frobenius > KL para TF-IDF:** En datasets sintéticos con documentos de longitud uniforme, la norma de Frobenius produce tópicos más coherentes que KL-divergence.

- **Embeddings > TF-IDF para Clustering:** Los embeddings densos (Ollama `nomic-embed-text`) capturan mejor la semántica que representaciones dispersas (Silhouette 0.24 vs 0.13).

- **Paquetes Python vs Módulos:** Al refactorizar un módulo a paquete, crear `__init__.py` con re-exports mantiene retrocompatibilidad y evita imports rotos.

- **RAG como Complemento:** Usar el contexto RAG como información de apoyo (no exclusiva) para evaluación de respuestas produce feedback más robusto.

---

## Acciones a tomar (Sprint 7) ⏭️

1. **Integración en Producción (Prioridad Alta)**
   - Merge de rama `feature/reasoning-clustering` a `main`.
   - Deploy completo del sistema de perfiles adaptativos.
   - Responsable: Gabriel.

2. **UI de Razonamiento CoT (Prioridad Alta)**
   - Mejorar frontend para visualizar el proceso de razonamiento del chatbot.
   - Responsable: Gabriel.

3. **Mapa de Conceptos en UI (Prioridad Media)**
   - Integrar `concept_map.json` en la interfaz del profesor (pendiente del Sprint 6).
   - Responsable: Gabriel.

4. **Optimización de Clustering en Tiempo Real (Prioridad Media)**
   - Optimizar rendimiento para clasificación de dificultad en producción.
   - Responsable: Gabriel.

5. **Tests End-to-End (Prioridad Media)**
   - Tests del flujo completo: pregunta → dificultad → CoT → respuesta adaptada → perfil actualizado.
   - Responsable: Gabriel.

---

## Métricas y estado del Sprint 📈

| Tarea | Estado |
|-------|--------|
| Prompts de Razonamiento (Chain-of-Thought) | ✅ Completado |
| Generación de Dataset Sintético | ✅ Completado |
| Búsqueda RAG Proactiva en Tests | ✅ Completado |
| Topic Modeling con NMF | ✅ Completado |
| Clustering de FAQs (K-Means + FCM) | ✅ Completado |
| Módulo de Evaluación de Dificultad | ✅ Completado |
| Notebook de Validación Matemática | ✅ Completado |
| Persistencia de Perfiles y Dashboard | ✅ Completado |
| ADRs (0035, 0036, 0037) | ✅ Completado |

### Métricas cuantitativas

| Métrica | Valor |
|---------|-------|
| Puntos completados | 38/38 |
| Historias completadas | HU #15, #16, #17 |
| Cobertura tests | 82% |
| ARI (clustering) | 0.87 |
| NMI (clustering) | 0.82 |
| FPC (FCM) | 0.76 |
| Coherencia NMF | 0.71 |
| Accuracy clasificador dificultad | 93.3% |

---

## Definition of Done ✅

- [x] El chatbot muestra su proceso de razonamiento de forma clara (CoT).
- [x] La dificultad de las preguntas se evalúa usando clasificador híbrido.
- [x] Las respuestas se adaptan según el nivel detectado (básico/intermedio/avanzado).
- [x] NMF extrae tópicos coherentes de la base de conocimiento (coherencia 0.71).
- [x] FAQs generadas automáticamente mediante K-Means/FCM.
- [x] Notebook de validación con métricas ARI=0.87, NMI=0.82, Silhouette documentadas.
- [x] Perfiles de conocimiento persistentes en MongoDB con CRUD funcional.
- [x] Los ADRs correspondientes están documentados (0035-0037).

---

**Elaborado por:** Gabriel Francisco  
**Sprint:** Sprint 6 (28/01/2026 — 18/02/2026)  
**Fecha de creación:** 25 de febrero de 2026
