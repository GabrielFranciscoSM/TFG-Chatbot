# Math Service — Algoritmos Matemáticos

Referencia de los algoritmos matemáticos del TFG que usa el Math Service. Todos están implementados **desde cero** en `math_investigation/`, sin dependencia de scikit-learn (propósito educativo/investigador).

## Visión general

| Algoritmo | Módulo | Uso en el servicio |
|-----------|--------|-------------------|
| Fuzzy C-Means (FCM) | `math_investigation/clustering/fcm.py` | Clustering de preguntas para FAQ |
| SphericalFuzzyCMeans | `math_service/services/fcm.py` | Variante coseno para embeddings |
| K-Means | `math_investigation/clustering/kmeans.py` | Determinación de k óptimo (elbow) |
| NMF | `math_service/services/nlp/nmf.py` | Topic modeling de documentos |
| TF-IDF | `math_service/services/nlp/tfidf.py` | Vectorización de texto |
| BoW | `math_service/services/nlp/bow.py` | Vectorización de texto (alternativa) |

---

## Fuzzy C-Means (FCM)

### Fundamentos matemáticos

FCM minimiza la función objetivo:

$$J_m(U, C) = \sum_{i=1}^{n} \sum_{j=1}^{k} (\mu_{ij})^m \| x_i - c_j \|^2$$

donde:
- $U = (\mu_{ij})$ es la matriz de pertenencia fuzzy ($n \times k$)
- $C = (c_j)$ son los centroides de los clústeres
- $m > 1$ es el parámetro de fuzziness (por defecto $m = 2$)
- $n$ = número de puntos, $k$ = número de clústeres

### Reglas de actualización iterativas

**Actualización de centroides:**

$$c_j = \frac{\sum_{i=1}^{n} (\mu_{ij})^m x_i}{\sum_{i=1}^{n} (\mu_{ij})^m}$$

**Actualización de membresías:**

$$\mu_{ij} = \left( \sum_{l=1}^{k} \left( \frac{\|x_i - c_j\|}{\|x_i - c_l\|} \right)^{\frac{2}{m-1}} \right)^{-1}$$

### Parámetros

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `n_clusters` | requerido | Número de clústeres $k$ |
| `m` | `2.0` | Fuzziness. $m=1$ → K-Means duro; $m \to \infty$ → distribución uniforme |
| `max_iter` | `300` | Máximo de iteraciones |
| `tol` | `1e-4` | Tolerancia de convergencia |
| `random_state` | `None` | Semilla para reproducibilidad |

### Interface

```python
from math_investigation.clustering.fcm import FuzzyCMeans

fcm = FuzzyCMeans(n_clusters=5, m=2.0, random_state=42)
fcm.fit(X)          # X: np.ndarray (n_samples, n_features)
labels = fcm.labels_        # Hard assignments: argmax por fila de U
centroids = fcm.centroids_  # (k, n_features)
U = fcm.membership_         # Fuzzy partition matrix (n, k)
```

---

## SphericalFuzzyCMeans

### Motivación

Los embeddings de texto (generados por `nomic-embed-text`) son vectores densos en alta dimensión. En estos espacios, la distancia euclidiana es menos informativa que la **similitud coseno**. La variante esférica normaliza todos los vectores a la esfera unitaria antes del clustering, de modo que la distancia euclidiana entre vectores normalizados equivale a usar similitud coseno.

### Diferencias con FCM estándar

1. **Normalización previa**: $\hat{x}_i = x_i / \|x_i\|_2$ para todo $i$
2. **Centroides normalizados**: tras cada actualización, los centroides se renormalizan
3. **Misma convergencia**: la función objetivo es equivalente pero con la métrica coseno

### Uso en el servicio

```python
from math_service.services.fcm import SphericalFuzzyCMeans

fcm = SphericalFuzzyCMeans(n_clusters=k, random_state=42)
fcm.fit(embeddings)
labels = fcm.labels_       # Asignación hard por argmax
centroids = fcm.centroids_ # Centroides normalizados
```

---

## Non-negative Matrix Factorization (NMF)

### Fundamentos matemáticos

NMF factoriza la matriz de documentos-términos $V \in \mathbb{R}_{\geq 0}^{n \times m}$ como:

$$V \approx W H$$

donde:
- $W \in \mathbb{R}_{\geq 0}^{n \times k}$ es la matriz documento-tópico
- $H \in \mathbb{R}_{\geq 0}^{k \times m}$ es la matriz tópico-término
- $k$ = número de tópicos (componentes)

La no-negatividad de ambas matrices permite una interpretación partes-del-todo: cada documento es una suma ponderada de tópicos, y cada tópico es una combinación de términos.

### Funciones de coste disponibles

**Frobenius (por defecto):**

$$\mathcal{L}_F = \| V - WH \|_F^2 = \sum_{ij} (V_{ij} - (WH)_{ij})^2$$

**Divergencia KL:**

$$\mathcal{L}_{KL} = \sum_{ij} \left[ V_{ij} \log \frac{V_{ij}}{(WH)_{ij}} - V_{ij} + (WH)_{ij} \right]$$

La divergencia KL es más adecuada cuando la matriz de entrada modela frecuencias (como TF-IDF o BoW con valores enteros).

### Reglas de actualización multiplicativa

Para Frobenius:

$$H \leftarrow H \odot \frac{W^T V}{W^T W H + \epsilon}$$
$$W \leftarrow W \odot \frac{V H^T}{W H H^T + \epsilon}$$

Para KL:

$$H \leftarrow H \odot \frac{W^T (V / WH)}{\sum_i W_{ik} + \epsilon}$$
$$W \leftarrow W \odot \frac{(V / WH) H^T}{\sum_j H_{kj} + \epsilon}$$

### Parámetros

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `n_components` | requerido | Número de tópicos $k$ |
| `cost` | `"frobenius"` | Función de coste: `"frobenius"` o `"kl"` |
| `max_iter` | `200` | Máximo de iteraciones |
| `tol` | `1e-4` | Tolerancia de convergencia |
| `random_state` | `None` | Semilla para reproducibilidad |

### Interface

```python
from math_service.services.nlp.nmf import NMF

nmf = NMF(n_components=5, random_state=42, cost="frobenius")
W, H = nmf.fit(feature_matrix)  # feature_matrix: (n_docs, n_terms)
# W: (n_docs, k) — distribución doc-tópico
# H: (k, n_terms) — peso tópico-término
```

**Extracción de términos principales de un tópico:**

```python
for i, topic_row in enumerate(H):
    top_indices = topic_row.argsort()[-5:][::-1]
    top_terms = [vocabulary[idx] for idx in top_indices]
```

---

## Vectorizadores de texto

### TF-IDF

Pondera cada término por su frecuencia en el documento (TF) e inversa de la frecuencia en el corpus (IDF):

$$\text{tfidf}(t, d) = \text{tf}(t, d) \cdot \log \frac{n}{1 + \text{df}(t)}$$

donde $n$ = número de documentos y $\text{df}(t)$ = documentos que contienen $t$.

**Parámetros disponibles:**

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `max_features` | `500` | Máximo de términos en el vocabulario |
| `min_df` | `2` | Frecuencia mínima de documento para incluir un término |
| `stop_words` | español+inglés | Lista de palabras vacías a excluir |

```python
from math_service.services.nlp.tfidf import TFIDFVectorizer

vec = TFIDFVectorizer(max_features=500, min_df=2)
matrix = vec.fit_transform(documents)  # (n_docs, n_terms)
vocab = vec.get_feature_names()
```

### Bag of Words (BoW)

Cada término se representa por su frecuencia de aparición (sin normalización IDF):

$$\text{bow}(t, d) = \text{count}(t, d)$$

Adecuado cuando se quiere preservar la importancia absoluta de los términos frecuentes.

```python
from math_service.services.nlp.bow import BoWVectorizer

vec = BoWVectorizer(max_features=500, min_df=2)
matrix = vec.fit_transform(documents)
```

---

## Determinación del K óptimo

### Método del codo (Elbow Method)

Para determinar automáticamente el número de clústeres $k$, el servicio aplica K-Means con distintos valores de $k$ y calcula el SSE (Sum of Squared Errors):

$$\text{SSE}(k) = \sum_{i=1}^{k} \sum_{x \in S_i} \| x - c_i \|^2$$

El $k$ óptimo es el punto donde la reducción marginal del SSE empieza a disminuir (el "codo" de la curva).

**Implementación en el servicio:**

```python
from math_service.services.clustering import get_optimal_k

k = get_optimal_k(X, max_k=15)
```

El algoritmo calcula SSE para $k \in [2, \text{max\_k}]$ con K-Means (inicializado con K-Means++) y detecta el codo usando diferencias de segundo orden.

### K-Means++ (inicialización)

Para evitar mínimos locales deficientes, se usa inicialización K-Means++:

1. Elegir el primer centroide uniformemente al azar.
2. Para cada punto $x_i$, calcular $d_i = \min_j \| x_i - c_j \|^2$ (distancia al centroide más cercano).
3. Elegir el siguiente centroide con probabilidad proporcional a $d_i$.
4. Repetir hasta tener $k$ centroides.

---

## Selección de pregunta representativa

Para cada clúster en la generación de FAQs, se selecciona la pregunta más cercana al centroide como representante del clúster:

```python
from math_service.services.clustering import get_closest_to_centroid

indices = get_closest_to_centroid(X, labels, centroids)
# indices[i] = índice en X del punto más cercano al centroide i
```

Para cada clúster $i$:

$$\text{repr}_i = \arg\min_{j : \text{label}(j) = i} \| x_j - c_i \|$$

---

## Proceso completo de generación de FAQs

```
preguntas (texto) 
    → OllamaClient.get_embeddings_batch()   [nomic-embed-text, 768 dim]
    → normalización a esfera unitaria        [SphericalFCM]
    → get_optimal_k()                        [K-Means++ + elbow]
    → SphericalFuzzyCMeans.fit()             [FCM con distancia coseno]
    → get_closest_to_centroid()              [pregunta representativa]
    → filtro min_cluster_size                [descartar clústeres pequeños]
    → MongoDB faqs (status: "draft")
```

## Proceso completo de extracción de tópicos

```
chunks RAG (texto)
    → TFIDFVectorizer / BoWVectorizer        [max_features=500, min_df=2]
    → get_optimal_k()                        [sobre feature matrix]
    → NMF.fit()                              [W: doc-topic, H: topic-term]
    → H.argsort()[-5:]                       [top-5 términos por tópico]
    → MistralClient.generate_text()          [título descriptivo]
    → ConceptMap (nodos + aristas)           [grafo para dashboard]
    → W normalizada fila a fila              [doc_topic_matrix]
    → MongoDB topics
```

---

## Guías de uso y ajuste

### ¿FCM o K-Means para FAQs?

FCM es preferible porque:
- Permite membresía parcial: una pregunta puede pertenecer a varios tópicos
- Más robusto a outliers que K-Means duro
- Mejor para clustering de texto semántico donde las fronteras son difusas

### ¿TF-IDF o BoW para topics?

- **TF-IDF** (por defecto): reduce el peso de términos muy frecuentes pero poco informativos; mejor para corpus con mucha variedad léxica
- **BoW**: preserva frecuencias absolutas; útil cuando la repetición de un término es significativa

### ¿Frobenius o KL para NMF?

- **Frobenius** (por defecto): más rápido, adecuado para TF-IDF (valores continuos)
- **KL**: más adecuado para matrices de conteo (BoW); produce tópicos más dispersos

### Ajustar el número de tópicos manualmente

Si el resultado automático no es satisfactorio, proporcionar `k` explícitamente en el request:

```json
{"subject": "iv", "k": 7}
```

Valores típicos: 3-8 tópicos para asignaturas de grado.
