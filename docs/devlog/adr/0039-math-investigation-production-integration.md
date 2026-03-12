---
adr: 0039
title: "Estrategia de Integración de math_investigation en Producción"
date: 2026-03-17
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 39
---

# ADR 0039 — Estrategia de Integración de math_investigation en Producción

## Status

Accepted

## Context

El módulo `math_investigation/` contiene implementaciones desde cero (sin scikit-learn) de los algoritmos de clustering para el TFG de Matemáticas:

- **K-Means** con inicialización K-Means++ y seguimiento de SSE
- **Fuzzy C-Means (FCM)** con parámetro de fuzziness _m_ y seguimiento de J_m
- **NMF** con reglas de actualización multiplicativas (Frobenius y KL-divergence)
- **Vectorizadores**: TF-IDF, BoW y wrapper de embeddings Ollama

El módulo fue diseñado inicialmente como herramienta de investigación (notebooks, CLI, experimentos comparativos). La pregunta que responde esta ADR es: **¿cómo integrarlo en el sistema de producción (math_service) manteniendo la separación entre código de investigación y código de servicio?**

### Restricciones del TFG de Matemáticas

- Los algoritmos **deben implementarse desde cero** (sin scikit-learn). Esta restricción tiene carácter académico y no puede negociarse.
- NumPy es la única dependencia numérica permitida.
- Cada clase debe tener docstrings que referencien la sección de la memoria del TFG.
- La convergencia debe ser rastreable: `sse_history_` (K-Means), `jm_history_` (FCM).

### Problema: dos ciclos de vida distintos

| Aspecto | math_investigation | math_service |
|---------|-------------------|-------------|
| Propósito | Investigación, comparación, notebooks | Servicio HTTP de producción |
| Interfaz | CLI, notebooks, Python directo | HTTP REST API |
| Ciclo de cambio | Frecuente (experimentos) | Estable (API pública) |
| Testing | Experimentos exploratorios | Tests unitarios e integración |
| Dependencias | numpy, matplotlib, tqdm | FastAPI, pymongo, httpx |

### Opciones de integración

| Opción | Descripción |
|--------|-------------|
| **A** | Copiar código de `math_investigation/` en `math_service/` |
| **B** | Instalar `math_investigation` como paquete Python (editable) |
| **C** | Reimplementar los algoritmos en `math_service/` usando scikit-learn |

## Decision

Usar la opción **B**: instalar `math_investigation` como **paquete Python editable** en el entorno del `math_service`.

### Mecanismo de integración

1. **Workspace dependency** en `pyproject.toml` raíz:
   ```toml
   [tool.uv.workspace]
   members = ["backend", "chatbot", "rag_service", "math_service", "math_investigation"]
   ```

2. **Importación directa** en `math_service/services/`:
   ```python
   # faq_service.py
   from math_investigation.clustering.fcm import FuzzyCMeans
   from math_investigation.nlp.tfidf import TFIDFVectorizer

   # topic_service.py
   from math_investigation.topic_modeling.nmf import NMF
   from math_investigation.nlp.tfidf import TFIDFVectorizer
   ```

3. **Wrapper de servicio** en `math_service/services/clustering.py` que adapta la interfaz de investigación a las necesidades del servicio:
   ```python
   class ClusteringService:
       """Adapta math_investigation.clustering para uso en math_service."""

       def cluster_questions(
           self,
           questions: list[str],
           n_clusters: int,
           algorithm: str = "fcm",
       ) -> dict:
           vectorizer = TFIDFVectorizer(max_features=500)
           X = vectorizer.fit_transform(questions)
           
           if algorithm == "fcm":
               model = FuzzyCMeans(n_clusters=n_clusters, m=2.0, max_iter=300)
           else:
               model = KMeans(n_clusters=n_clusters, max_iter=300)
           
           labels = model.fit_predict(X)
           return {"labels": labels.tolist(), "n_clusters": n_clusters}
   ```

4. **Dockerfile** instala el paquete desde el contexto de construcción:
   ```dockerfile
   COPY math_investigation/ ./math_investigation/
   RUN pip install -e ./math_investigation
   ```

### Contrato de estabilidad

Para evitar que los cambios experimentales en `math_investigation/` rompan `math_service/`, se establece el siguiente contrato:

| Clase/Módulo | Estado | Usado por math_service |
|---|---|---|
| `clustering.kmeans.KMeans` | Estable | Sí (fallback) |
| `clustering.fcm.FuzzyCMeans` | Estable | Sí (primario) |
| `topic_modeling.nmf.NMF` | Estable | Sí |
| `nlp.tfidf.TFIDFVectorizer` | Estable | Sí |
| `nlp.bow.BagOfWords` | Estable | Sí |
| `nlp.embeddings.OllamaEmbeddings` | Experimental | No (directo vía HTTP) |
| `cli.*` | Experimental | No |
| `visualization.*` | Experimental | No |

**Regla**: Los cambios a las clases marcadas como "Estable" requieren actualizar los tests de `math_service/tests/` antes de fusionar.

## Consequences

### Pros

1. **DRY**: Los algoritmos se implementan una sola vez; cambios en la investigación se propagan automáticamente al servicio.
2. **Trazabilidad académica**: El código de producción referencia directamente las implementaciones del TFG de Matemáticas.
3. **Sin duplicación**: No hay riesgo de que las versiones de investigación y producción diverjan.
4. **Testing multinivel**: Los algoritmos tienen tests en `math_investigation/` (corrección matemática) y en `math_service/tests/` (integración de servicio).

### Cons

1. **Acoplamiento entre TFGs**: Un cambio experimental en `math_investigation/` puede romper `math_service/` si afecta a las clases estables.
2. **Build más lenta**: El Dockerfile debe incluir el directorio `math_investigation/` en el contexto de construcción.
3. **Dependencias transitivas**: `math_investigation/` arrastra `matplotlib`, `tqdm` al entorno de producción (solo necesarios para investigación).

### Mitigaciones

- Tests de regresión en `math_service/tests/` cubren los flujos que dependen de `math_investigation/`.
- Las dependencias de visualización (`matplotlib`, `tqdm`) no se añaden al `pyproject.toml` de `math_service`, solo al de `math_investigation`.
- El contrato de estabilidad documenta explícitamente qué módulos son públicos para el servicio.

## Alternatives Considered

### Opción A: Copiar código en math_service

**Rechazado**

- Duplicación inmediata: dos versiones del mismo algoritmo que inevitablemente divergirían.
- Viola la motivación académica de conectar ambos TFGs.
- Mayor superficie de mantenimiento.

### Opción C: Reimplementar con scikit-learn en math_service

**Rechazado expresamente**

- Viola la restricción del TFG de Matemáticas (implementación desde cero).
- Elimina la conexión entre la investigación matemática y el sistema.
- No demuestra la aplicación práctica de los algoritmos implementados.

### Opción D: API inter-servicio (math_investigation como servicio)

**Considerado para futuro**

- `math_investigation/` expuesto como microservicio separado del `math_service`.
- Demasiado overhead para el ámbito del TFG.
- Viable si el módulo de investigación crece hasta requerir su propio ciclo de despliegue.

## Implementation

### Archivos clave

| Archivo | Cambio |
|---------|--------|
| `pyproject.toml` (raíz) | `math_investigation` añadido a workspace members |
| `math_service/Dockerfile` | `COPY math_investigation/` + `pip install -e ./math_investigation` |
| `math_service/services/clustering.py` | Wrapper `ClusteringService` sobre algoritmos de `math_investigation` |
| `math_service/services/faq_service.py` | Importa `FuzzyCMeans`, `TFIDFVectorizer` |
| `math_service/services/topic_service.py` | Importa `NMF`, `TFIDFVectorizer` |

### Tests que verifican la integración

```bash
# Unitarios: corrección matemática (en math_investigation/)
pytest math_investigation/tests/ -v

# Integración: servicio con algoritmos reales
pytest math_service/tests/ -v

# E2E: flujo completo desde endpoint HTTP
pytest tests/ -m integration -k "math" -v
```

## References

- [ADR 0036](0036-clustering-algorithms.md) — Selección de algoritmos (FCM vs K-Means)
- [ADR 0038](0038-math-service-microservice.md) — math_service como microservicio independiente
- [math_investigation/README.md](../../../math_investigation/README.md) — Documentación del módulo de investigación
- [docs/services/math_service.md](../../services/math_service.md) — Documentación del servicio
