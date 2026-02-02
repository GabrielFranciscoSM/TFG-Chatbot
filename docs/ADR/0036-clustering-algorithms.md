---
adr: 0036
title: "K-Means vs Fuzzy C-Means for Question Clustering"
date: 2026-02-16
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 36
---

# ADR 0036 — K-Means vs Fuzzy C-Means for Question Clustering

## Status

Accepted

## Context

El sistema necesita agrupar preguntas de estudiantes para:
1. **Análisis de FAQs**: Identificar preguntas frecuentes y patrones temáticos
2. **Clasificación de dificultad**: Agrupar preguntas por nivel de complejidad semántica
3. **Personalización**: Adaptar respuestas según el tipo de pregunta

Disponemos de dos algoritmos implementados según TFG Sección 3.2:
- **K-Means** (Sección 3.2.1): Clustering particional "duro" con asignación única
- **Fuzzy C-Means (FCM)** (Sección 3.2.2): Clustering "difuso" con membresía parcial

### Requisitos

| Requisito | Prioridad |
|-----------|-----------|
| Identificar preguntas que pertenecen a múltiples categorías | Alta |
| Detectar preguntas ambiguas o en fronteras temáticas | Alta |
| Rendimiento computacional aceptable | Media |
| Interpretabilidad de resultados | Media |

## Decision

**Usar FCM como algoritmo principal para clustering de preguntas**, con K-Means como fallback para análisis rápido.

### Configuración recomendada

```python
# FCM para análisis detallado
fcm = FuzzyCMeans(
    n_clusters=k,      # Determinado por Elbow Method
    m=2.0,             # Fuzziness estándar
    max_iter=300,
    tol=1e-4
)

# Umbral para identificar preguntas "fuzzy"
FUZZY_THRESHOLD = 0.3  # Membresía mínima para considerar pertenencia
```

### Justificación matemática

FCM minimiza el funcional generalizado (Proposición 3.15):

$$J_m(U, C) = \sum_{i=1}^{N} \sum_{j=1}^{k} (\mu_{ji})^m \|x_i - c_j\|^2$$

Donde:
- $\mu_{ji} \in [0,1]$: Grado de pertenencia del punto $x_i$ al cluster $j$
- $m > 1$: Parámetro de fuzziness (controla suavidad de transiciones)

A diferencia de K-Means que asigna cada punto a exactamente un cluster, FCM permite expresar:
- **Preguntas claras**: Alta membresía en un cluster ($\mu_{ji} > 0.8$)
- **Preguntas ambiguas**: Membresía distribuida entre varios clusters

## Consequences

### Pros

1. **Mejor manejo de ambigüedad**: Preguntas como "¿Cómo funciona Docker y por qué es mejor que VMs?" pueden pertenecer tanto a "conceptos básicos" como a "análisis comparativo"
2. **Información adicional**: El grado de membresía indica confianza en la clasificación
3. **Detección de outliers**: Puntos con membresía uniforme ($\approx 1/k$) son candidatos a nuevas categorías
4. **Análisis pedagógico**: Identificar qué conceptos se confunden frecuentemente

### Cons

1. **Mayor complejidad computacional**: $O(n \cdot k \cdot d \cdot i)$ vs $O(n \cdot k \cdot d \cdot i)$ similar pero con más operaciones por iteración
2. **Parámetro adicional** ($m$): Requiere tuning para cada caso de uso
3. **Interpretación menos directa**: Resultados requieren análisis de matriz de membresía

### Mitigaciones

- Usar K-Means para análisis exploratorio rápido
- Pre-calcular centroides FCM offline y reusar para clasificación online
- Establecer umbrales claros para interpretación de membresía

## Alternatives Considered

### 1. Solo K-Means

**Rechazado**

- No captura la naturaleza ambigua de preguntas en educación
- Pérdida de información sobre fronteras entre categorías
- Una pregunta sobre "diferencias entre REST y GraphQL" podría abordar múltiples temas

### 2. DBSCAN / Clustering jerárquico

**Rechazado**

- DBSCAN no produce centroides para clasificación de nuevas preguntas
- Clustering jerárquico tiene complejidad $O(n^2)$ o peor
- Ninguno ofrece membresía parcial

### 3. Gaussian Mixture Models (GMM)

**Considerado para futuro**

- Similar a FCM pero con modelado probabilístico completo
- Mayor complejidad de implementación
- Podría ser útil para análisis avanzado

## Implementation

### Archivos modificados/creados

| Archivo | Propósito |
|---------|-----------|
| `math_investigation/clustering/kmeans.py` | Implementación K-Means con K-Means++ |
| `math_investigation/clustering/fcm.py` | Implementación FCM según Proposiciones 3.15 y 3.17 |
| `math_investigation/clustering/metrics.py` | Métricas: Silhouette, ARI, NMI, FPC |
| `chatbot/logic/difficulty.py` | Usa centroides pre-entrenados para clasificación |

### Flujo de uso

```
1. Entrenamiento (offline):
   - Embeddings de preguntas etiquetadas → FCM → Centroides por dificultad

2. Clasificación (online):
   - Nueva pregunta → Embedding → Distancia a centroides → Nivel de dificultad
```

### Métricas de validación

- **Silhouette Score**: Validación interna de separación de clusters
- **Fuzzy Partition Coefficient (FPC)**: Calidad de partición difusa (1 = crisp, 1/k = máxima fuzziness)
- **ARI/NMI**: Validación externa contra etiquetas manuales

## References

- TFG Sección 3.2.1: "Algoritmo K-Means"
- TFG Sección 3.2.2: "Fuzzy C-Means y el parámetro de fuzziness m"
- Bezdek, J.C. (1981). "Pattern Recognition with Fuzzy Objective Function Algorithms"
- [ADR 0035](0035-adaptive-chain-of-thought.md): Usa clasificación de dificultad para CoT adaptativo
