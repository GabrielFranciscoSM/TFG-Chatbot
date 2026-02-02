---
layout: default
title: Math Investigation
parent: Developer Guide
nav_order: 7
---

# Math Investigation Module

The `math_investigation/` module contains from-scratch implementations of clustering algorithms for the Mathematics TFG.

---

## Overview

This module implements clustering and topic modeling algorithms **from scratch** using only NumPy, as part of the educational objectives of the Mathematics TFG.

### Module Structure

```
math_investigation/
├── clustering/           # Clustering algorithms
│   ├── kmeans.py         # K-Means with K-Means++ initialization
│   ├── fcm.py            # Fuzzy C-Means
│   └── metrics.py        # Evaluation metrics
├── topic_modeling/       # Topic modeling
│   ├── nmf.py            # Non-negative Matrix Factorization
│   └── coherence.py      # Topic coherence metrics
├── nlp/                  # Text vectorization
│   ├── tfidf.py          # TF-IDF vectorizer
│   ├── bow.py            # Bag of Words vectorizer
│   └── embeddings.py     # Ollama embeddings wrapper
├── visualization/        # Plotting utilities
├── cli/                  # Command-line runners
└── data/                 # Datasets and results
```

---

## Running Experiments

### K-Means and FCM Clustering

```bash
# Basic clustering experiment
python -m math_investigation.cli.run_clustering --k 5 --vectorizer tfidf

# With Ollama embeddings
python -m math_investigation.cli.run_clustering --k 5 --vectorizer emb

# Custom parameters
python -m math_investigation.cli.run_clustering \
    --k 7 \
    --vectorizer tfidf \
    --max-iter 500 \
    --seed 42
```

### NMF Topic Modeling

```bash
# Basic topic modeling
python -m math_investigation.cli.run_topic_modeling --n-topics 5

# With custom parameters
python -m math_investigation.cli.run_topic_modeling \
    --n-topics 10 \
    --max-iter 500 \
    --output results/topics.json
```

### Algorithm Comparison

```bash
# Compare across different k values
python -m math_investigation.cli.compare \
    --k-range 3,10 \
    --output results/

# With specific vectorizers
python -m math_investigation.cli.compare \
    --k-range 3,10 \
    --vectorizers tfidf,bow,emb \
    --output results/
```

---

## Algorithm Interfaces

All algorithms follow scikit-learn-like interfaces for familiarity:

### K-Means

```python
from math_investigation.clustering import KMeans

# Initialize
kmeans = KMeans(k=5, init="kmeans++", max_iter=300, random_state=42)

# Fit and predict
labels = kmeans.fit_predict(X)

# Access results
print(kmeans.centroids_)       # Cluster centroids
print(kmeans.sse_history_)     # SSE per iteration
print(kmeans.n_iter_)          # Iterations until convergence
```

### Fuzzy C-Means

```python
from math_investigation.clustering import FuzzyCMeans

# Initialize with fuzziness parameter m
fcm = FuzzyCMeans(c=5, m=2.0, max_iter=300, random_state=42)

# Fit and get membership matrix
U = fcm.fit_predict(X)  # Returns membership degrees

# Access results
print(fcm.centroids_)      # Cluster centroids
print(fcm.jm_history_)     # J_m objective per iteration
print(fcm.membership_)     # Full membership matrix
```

### TF-IDF Vectorizer

```python
from math_investigation.nlp import TfidfVectorizer

# Initialize
vectorizer = TfidfVectorizer(max_features=1000, min_df=2)

# Fit and transform
X = vectorizer.fit_transform(documents)

# Transform new documents
X_new = vectorizer.transform(new_documents)

# Access vocabulary
print(vectorizer.vocabulary_)
print(vectorizer.idf_)
```

### NMF Topic Modeling

```python
from math_investigation.topic_modeling import NMF

# Initialize
nmf = NMF(n_components=10, max_iter=500, random_state=42)

# Fit and transform
W = nmf.fit_transform(X)  # Document-topic matrix
H = nmf.components_       # Topic-word matrix

# Get top words per topic
top_words = nmf.get_top_words(vectorizer.vocabulary_, n_words=10)
```

---

## Evaluation Metrics

### Internal Metrics (No Ground Truth)

```python
from math_investigation.clustering.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)

# Silhouette score (-1 to 1, higher is better)
sil = silhouette_score(X, labels)

# Davies-Bouldin index (lower is better)
db = davies_bouldin_score(X, labels)

# Calinski-Harabasz index (higher is better)
ch = calinski_harabasz_score(X, labels)
```

### External Metrics (With Ground Truth)

```python
from math_investigation.clustering.metrics import (
    adjusted_rand_score,
    normalized_mutual_info,
)

# Adjusted Rand Index (-1 to 1, higher is better)
ari = adjusted_rand_score(true_labels, predicted_labels)

# Normalized Mutual Information (0 to 1, higher is better)
nmi = normalized_mutual_info(true_labels, predicted_labels)
```

### FCM-Specific Metrics

```python
from math_investigation.clustering.metrics import (
    fuzzy_partition_coefficient,
)

# Fuzzy Partition Coefficient (0 to 1, higher is better)
fpc = fuzzy_partition_coefficient(membership_matrix)
```

---

## Mathematical Foundations

The algorithms implement the following mathematical formulations:

### K-Means

Minimizes the Sum of Squared Errors (SSE):

$$SSE(S,C) = \sum_{i=1}^{k} \sum_{x \in S_i} \|x - c_i\|^2$$

**K-Means++ Initialization**: Selects initial centroids with probability proportional to squared distance from nearest existing centroid.

### Fuzzy C-Means

Minimizes the weighted objective function:

$$J_m(U,C) = \sum_{j=1}^{c} \sum_{i=1}^{n} (\mu_{ji})^m \|x_i - c_j\|^2$$

Where:
- $\mu_{ji}$ is the membership degree of point $i$ to cluster $j$
- $m > 1$ is the fuzziness parameter (typically $m = 2$)

**Membership Update**:

$$\mu_{ji} = \frac{1}{\sum_{l=1}^{c} \left(\frac{\|x_i - c_j\|}{\|x_i - c_l\|}\right)^{\frac{2}{m-1}}}$$

### Non-negative Matrix Factorization

Factorizes matrix $V \approx WH$ with $W, H \geq 0$ using multiplicative update rules:

$$H \leftarrow H \odot \frac{W^T V}{W^T W H}$$

$$W \leftarrow W \odot \frac{V H^T}{W H H^T}$$

---

## Integration with Chatbot

The clustering algorithms enhance the chatbot in several ways:

### Question Difficulty Classification

```python
# Train centroids from labeled questions
from chatbot.logic.difficulty import DifficultyClassifier

classifier = DifficultyClassifier()
classifier.load_centroids("chatbot/data/difficulty_centroids.json")

# Predict difficulty
difficulty = classifier.predict("¿Qué es Docker?")
# Returns: DifficultyLevel.BASIC
```

### Training Centroids

```bash
# Use the training script
python scripts/train_difficulty_centroids.py \
    --data labeled_questions.json \
    --output chatbot/data/difficulty_centroids.json
```

---

## Running Tests

```bash
# All math investigation tests
uv run pytest math_investigation/ -v

# Specific module
uv run pytest math_investigation/clustering/ -v
uv run pytest math_investigation/nlp/ -v

# With coverage
uv run pytest math_investigation/ --cov=math_investigation
```

---

## Further Reading

Detailed mathematical derivations and proofs are available in the TFG Mathematics thesis document (see `docs/latex/`).
