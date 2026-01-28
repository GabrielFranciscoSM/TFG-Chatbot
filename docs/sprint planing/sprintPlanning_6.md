---
layout: default
title: Sprint Planning 6 - Razonamiento, Adaptación y Clustering Textual
parent: Sprint Planning
grand_parent: DevLog
---

# Sprint Planning - Sprint 6 (Razonamiento, Adaptación y Clustering Textual)

## Información General

- **Sprint:** Sprint 6
- **Fecha de inicio:** 28 de enero de 2026
- **Fecha de finalización:** 18 de febrero de 2026
- **Duración:** 3 semanas
- **Equipo:** Gabriel Francisco

---

## Objetivo del Sprint (Sprint Goal)

> Implementar capacidades avanzadas de razonamiento y adaptación en el agente conversacional, integrando técnicas de clustering textual (NMF, K-Means, FCM) para el análisis de tópicos, generación de FAQs, y diversificación de resultados RAG.

Este sprint combina los objetivos del Milestone 7 (herramientas avanzadas del chatbot) con la integración matemática del TFG conjunto, validando algoritmos de clustering sobre datos sintéticos y mejorando la experiencia pedagógica del agente.

---

## Alcance

### Funcionalidades del Agente (HU #15, #16, #17)
- **Razonamiento visible:** Implementar Chain-of-Thought para mostrar el proceso de pensamiento.
- **Evaluación de dificultad:** Clasificar la complejidad de las preguntas del estudiante.
- **Adaptación de respuestas:** Ajustar el nivel de detalle según la dificultad detectada.

### Integración Matemática (Clustering Textual)
- **Topic Modeling (NMF):** Descubrimiento automático de tópicos latentes en la base de conocimiento.
- **FAQ Generation (K-Means + FCM):** Clustering de preguntas sintéticas para sugerir preguntas frecuentes.

### Stack Tecnológico

- **LLM Framework:** LangGraph + LangChain
- **Clustering:** scikit-learn (K-Means, NMF), scikit-fuzzy (FCM)
- **Embeddings:** Modelo de embeddings del RAG (text-embedding-3-small o local)
- **Vectorización:** TF-IDF para matriz documento-término
- **Visualización:** t-SNE / UMAP, matplotlib, seaborn
- **Métricas:** ARI, NMI, Silhouette Score, Coherencia Semántica
- **Persistencia:** MongoDB para perfiles de conocimiento
- **Backend:** FastAPI para nuevos endpoints

---

## Historias de Usuario (HU) asociadas

- **HU #15** — [HU 015] Como profesor me gustaría que el agente razonara sus respuestas y enseñara su proceso para que el alumno entienda el origen de estas.
- **HU #16** — [HU 016] Como profesor me gustaría que el chatbot guarde y evalúe el conocimiento del alumno para adaptar sus respuestas.
- **HU #17** — [HU 017] Como alumno me gustaría que el chatbot evaluase la dificultad de mi pregunta y respondiera en consonancia.

---

## Criterios de Aceptación

### Razonamiento y Adaptación (HU #15, #16, #17)

- **Razonamiento Visible (HU #15):**
  - [ ] El chatbot muestra su proceso de razonamiento antes de dar una respuesta.
  - [ ] Los pasos de razonamiento son claros y comprensibles para el estudiante.
  - [ ] Se puede configurar el nivel de detalle del razonamiento mostrado.

- **Evaluación de Conocimiento (HU #16):**
  - [ ] El sistema almacena información sobre las interacciones del estudiante.
  - [ ] Se evalúa el nivel de conocimiento basado en el historial de preguntas.
  - [ ] Los profesores pueden visualizar el progreso de sus estudiantes.

- **Adaptación por Dificultad (HU #17):**
  - [ ] El chatbot evalúa la dificultad de cada pregunta recibida.
  - [ ] Las respuestas se adaptan en complejidad según la dificultad detectada.
  - [ ] El estudiante recibe respuestas apropiadas a su nivel.

### Integración Matemática (Clustering)

- **Generación de Datos Sintéticos:**
  - [ ] Script `scripts/math/generate_dataset.py` genera datos sintéticos con etiquetas conocidas.
  - [ ] Los datos se almacenan en `data/synthetic_dataset.json`.
  - [ ] Se incluyen documentos "trampa" que mezclan vocabulario de múltiples temas.

- **Topic Modeling (NMF):**
  - [ ] Pipeline NMF extrae tópicos latentes de los chunks del RAG.
  - [ ] Coherencia semántica (UCI/UMass) medida y documentada.
  - [ ] Mapa de conceptos generado automáticamente.

- **FAQ Generation (K-Means + FCM):**
  - [ ] Preguntas sintéticas generadas y clusterizadas.
  - [ ] Comparación K-Means vs FCM documentada con métricas (Silhouette, ARI).
  - [ ] Centroides convertidos en "Preguntas Sugeridas".


---

## Tareas (desglose)

### Semana 1: Razonamiento Visible + Generación de Datos Sintéticos

1. **Prompts de Razonamiento (Chain-of-Thought)**
   - Diseñar prompts que implementen CoT.
   - Crear estructura para separar razonamiento de respuesta final.
   - Implementar formato de salida estructurado (JSON/Markdown).
   - Modificar el grafo LangGraph para incluir paso de "thinking".

2. **Generación de Dataset Sintético**
   - Crear `scripts/math/generate_dataset.py`.
   - Implementar prompts para generar documentos y preguntas sintéticas.
   - Generar 100+ documentos por tema (3 temas disjuntos).
   - Incluir documentos "trampa" con vocabulario mixto.
   - Almacenar en `data/synthetic_dataset.json` con etiquetas reales.

### Semana 2: Clustering y Topic Modeling

3. **Topic Modeling con NMF**
   - Construir matriz TF-IDF a partir de chunks de Qdrant.
   - Implementar pipeline NMF con scikit-learn.
   - Probar diferentes funciones de coste (Frobenius vs KL-divergence).
   - Calcular coherencia semántica (UCI/UMass).
   - Generar visualizaciones de tópicos.

4. **Clustering de FAQs (K-Means + FCM)**
   - Generar preguntas sintéticas desde chunks muestreados.
   - Obtener embeddings de las preguntas.
   - Implementar K-Means con inicialización K-Means++.
   - Implementar FCM con scikit-fuzzy.
   - Comparar algoritmos: Silhouette Score, ARI, NMI.
   - Justificar elección de k con Elbow Method.

### Semana 3: Evaluación de Dificultad + Validación Matemática

6. **Módulo de Evaluación de Dificultad**
   - Implementar clasificador de dificultad basado en clustering de preguntas.
   - Definir niveles de dificultad (básico, intermedio, avanzado).
   - Integrar evaluación en el flujo del agente.
   - Crear prompts adaptativos según nivel detectado.

7. **Notebook de Validación Matemática**
   - Crear `notebooks/math_clustering.ipynb`.
   - Ejecutar experimento "ciego" sobre datos sintéticos.
   - Calcular métricas de validación externa (ARI, NMI).
   - Calcular coeficiente de partición (FCM).
   - Generar visualizaciones t-SNE/UMAP de clústeres.
   - Documentar resultados numéricos para memoria del TFG.

8. **Persistencia de Perfiles y Visualización**
   - Diseñar modelo de datos para perfil de conocimiento.
   - Implementar persistencia en MongoDB.
   - Añadir sección de progreso de estudiantes en dashboard.
   - Integrar mapa de conceptos (tópicos NMF) en interfaz de profesor.

---

## Estimaciones (puntos)

- Razonamiento Chain-of-Thought: 5
- Generación Dataset Sintético: 5
- Topic Modeling (NMF): 5
- Clustering FAQs (K-Means + FCM): 8
- Evaluación de Dificultad: 5
- Notebook Validación Matemática: 5
- Persistencia y Dashboard: 5
- **Total aproximado:** 38 puntos

---

## Riesgos y dependencias

- **Latencia de respuesta:** El razonamiento paso a paso puede incrementar el tiempo de respuesta.
- **Calidad de datos sintéticos:** La validación depende de la calidad de los datos generados por el LLM.
- **Precisión del clustering:** FCM puede no converger correctamente con datos muy dispersos.
- **Complejidad técnica:** Múltiples algoritmos nuevos (NMF, FCM) requieren testing exhaustivo.
- **Dependencias:** scikit-fuzzy puede tener conflictos de versión con otras dependencias.
- **Dependencia de Sprint 5:** Stack de observabilidad requerido para métricas de uso.

---

## Definition of Done

- El chatbot muestra su proceso de razonamiento de forma clara.
- La dificultad de las preguntas se evalúa usando clustering de embeddings.
- Las respuestas se adaptan según el nivel detectado.
- NMF extrae tópicos coherentes de la base de conocimiento.
- FAQs generadas automáticamente mediante K-Means/FCM.
- Notebook de validación con métricas ARI, NMI, Silhouette documentadas.
- Los ADRs correspondientes están documentados.

---

## Backlog del sprint (prioridad)

- Issue #15 — [HU 015] Razonamiento visible del agente. Enlace: [#15](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/15)
- Issue #16 — [HU 016] Evaluación y persistencia del conocimiento. Enlace: [#16](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/16)
- Issue #17 — [HU 017] Adaptación por dificultad de pregunta. Enlace: [#17](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/17)

---

## Referencias

- [Propuesta de Integración Matemática](../notas/integracion_matematica_clustering.md) — Documento base para la integración de clustering textual.

---

**Elaborado por:** Gabriel Francisco

**Fecha:** 28 de enero de 2026

---
