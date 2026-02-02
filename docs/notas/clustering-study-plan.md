# Estudio Exhaustivo de Métodos de Clustering

> **Estado**: Pendiente  
> **Prioridad**: Media  
> **Contexto**: Comparación de algoritmos de clustering vs topic modeling para análisis de FAQs educativas

---

## 🎯 Objetivo

Realizar un estudio comparativo exhaustivo de métodos de clustering y topic modeling para evaluar su aplicabilidad en la organización automática de preguntas frecuentes (FAQs) del chatbot educativo.

---

## 📊 Datasets Seleccionados

| Dataset | Descripción | Tamaño | Uso |
|---------|-------------|--------|-----|
| **20 Newsgroups** | Corpus estándar de clasificación de texto | ~18,000 docs | Benchmark establecido |
| **Education Dialogue** | Diálogos educativos estructurados | Variable | Dominio educativo |
| **Sciphi Textbooks** | Contenido de libros de texto científicos | Grande | Conocimiento técnico |

---

## 🔬 Algoritmos a Implementar

### 1. Hard Clustering

#### K-Means (Implementación Manual)
- [ ] Implementar algoritmo desde cero
- [ ] Inicialización inteligente de centroides (K-Means++)
- [ ] Actualización de centroides con distancia Euclídea
- [ ] Método del codo (Elbow Method) para selección de k
- [ ] Análisis de convergencia

#### Hierarchical Clustering
- [ ] Agglomerative clustering (bottom-up)
- [ ] Dendrograma para visualización
- [ ] Diferentes métricas de enlace (single, complete, average, Ward)

### 2. Soft/Fuzzy Clustering

#### FCM - Fuzzy C-Means (Implementación Manual)
- [ ] Implementar algoritmo difuso completo
- [ ] Matriz de pertenencia con parámetro de fuzziness (m=2)
- [ ] Centros de clúster ponderados
- [ ] Análisis de la "difusividad" de asignaciones
- [ ] Comparación teórica con K-Means

### 3. Topic Modeling (Comparativa)

#### NMF - Non-negative Matrix Factorization
- [ ] NMF con norma Frobenius (asume distribución Gaussiana)
- [ ] NMF con divergencia KL (asume distribución Poisson)
- [ ] Análisis de coherencia (UCI, UMass)
- [ ] Wordclouds por tópico

#### LDA - Latent Dirichlet Allocation
- [ ] Implementación con Gensim
- [ ] Comparación con NMF
- [ ] Análisis de perplexity

---

## 📐 Vectorización

| Método | Uso Principal | Características |
|--------|---------------|-----------------|
| **TF-IDF** | K-Means, FCM | Pesos por frecuencia inversa |
| **BoW** | Baseline, pruebas | Conteo simple |
| **Embeddings SOTA** | Comparativa avanzada | text-embedding-3-small o similar |

---

## 📈 Métricas de Evaluación

### Métricas Internas (sin etiquetas)
- **Silhouette Score**: Cohesión vs separación
- **Davies-Bouldin Index**: Ratio de dispersión intra/inter-cluster
- **Calinski-Harabasz**: Varianza entre clusters vs dentro

### Métricas Externas (con etiquetas ground truth)
- **Pureza (Purity)**: Proporción de elementos correctamente asignados
- **NMI (Normalized Mutual Information)**: Información compartida
- **ARI (Adjusted Rand Index)**: Similitud de particiones

### Métricas de Topic Modeling
- **Coherencia UCI**: Basada en co-ocurrencia
- **Coherencia UMass**: Basada en probabilidad condicional

---

## 📋 Tabla Comparativa Final

```
| Algoritmo        | Dataset          | Pureza | NMI   | Silhouette | Coherencia |
|------------------|------------------|--------|-------|------------|------------|
| K-Means          | 20 Newsgroups    |        |       |            |     -      |
| K-Means          | Education Dial.  |        |       |            |     -      |
| K-Means          | Sciphi           |        |       |            |     -      |
| FCM              | 20 Newsgroups    |        |       |            |     -      |
| FCM              | Education Dial.  |        |       |            |     -      |
| FCM              | Sciphi           |        |       |            |     -      |
| NMF-Frobenius    | 20 Newsgroups    |        |       |     -      |            |
| NMF-Frobenius    | Education Dial.  |        |       |     -      |            |
| NMF-Frobenius    | Sciphi           |        |       |     -      |            |
| NMF-KL           | 20 Newsgroups    |        |       |     -      |            |
| NMF-KL           | Education Dial.  |        |       |     -      |            |
| NMF-KL           | Sciphi           |        |       |     -      |            |
```

---

## 🗂️ Estructura de Código Propuesta

```
math_investigation/
├── clustering/
│   ├── __init__.py
│   ├── kmeans.py          # ManualKMeans class
│   ├── fcm.py             # ManualFCM class
│   ├── hierarchical.py    # Agglomerative clustering
│   └── evaluation.py      # Métricas y evaluación
├── topic_modeling/
│   ├── __init__.py
│   ├── nmf.py             # NMF Frobenius y KL
│   └── lda.py             # LDA wrapper
├── data/
│   ├── loaders.py         # Carga de los 3 datasets
│   └── preprocessors.py   # Vectorización TF-IDF, BoW
├── visualization/
│   ├── dendrograms.py
│   ├── wordclouds.py
│   └── cluster_plots.py
└── experiments/
    ├── run_comparison.py  # Script principal
    └── results/           # Outputs y gráficos
```

---

## ⚠️ Consideraciones

1. **Computación**: FCM manual puede ser costoso en Sciphi (dataset grande)
2. **Convergencia**: Validar implementaciones manuales vs scikit-learn
3. **Reproducibilidad**: Fijar semillas aleatorias para todos los experimentos
4. **Documentación**: Incluir fundamentación matemática de cada algoritmo

---

## 📚 Referencias

- MacQueen, J. (1967). "Some methods for classification and analysis of multivariate observations"
- Bezdek, J.C. (1981). "Pattern Recognition with Fuzzy Objective Function Algorithms"
- Lee, D.D. & Seung, H.S. (1999). "Learning the parts of objects by non-negative matrix factorization"
- Blei, D.M., Ng, A.Y., & Jordan, M.I. (2003). "Latent Dirichlet Allocation"

---

## 🔗 Relación con el Proyecto

Este estudio complementará el clasificador de dificultad implementado, proporcionando:
- Agrupación automática de FAQs por tema
- Detección de patrones en preguntas de usuarios
- Posible mejora del sistema RAG mediante clustering semántico
