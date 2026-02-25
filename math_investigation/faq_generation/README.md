# FAQ Generation via Clustering

This directory contains experiments for generating FAQs by clustering student questions and computing representative centroids.

## Overview

**Goal**: Automatically generate FAQ structures by:
1. Clustering similar student questions using K-Means and Fuzzy C-Means
2. Computing cluster centroids representing typical question patterns
3. Extracting representative questions closest to each centroid
4. Organizing questions into FAQ categories

**Applications**:
- **Question classification**: Route new questions to appropriate handlers
- **Difficulty estimation**: Predict question difficulty using labeled centroids
- **Automated FAQ generation**: Create FAQ entries for new subjects/topics
- **Chatbot integration**: Use centroids for real-time question classification

## Experiments

### CIMA Dataset
**Notebook**: `faq_clustering_cima.ipynb`  
**Dataset**: Italian language tutoring dialogues  
**Status**: Ready for execution

**Clustering Methods**:
- **K-Means**: Hard clustering with K-Means++ initialization
- **Fuzzy C-Means (FCM)**: Soft clustering with membership degrees

**Expected FAQ Categories**:
1. Vocabulary translation requests ("What is X in Italian?")
2. Grammar rule clarifications ("How do I say X?")
3. Verification questions ("Is X correct?")
4. Metacognitive help-seeking ("What's the answer?")

### Future Datasets
- `faq_clustering_<dataset_name>.ipynb` - Follow the same structure
- Ensure consistent naming: `{dataset}_faq_YYYYMMDD_HHMMSS`

## Mathematical Foundation

### K-Means Clustering

Minimizes within-cluster sum of squared errors (SSE):

$$SSE(S, C) = \sum_{i=1}^{k} \sum_{x \in S_i} ||x - c_i||^2$$

Where:
- $S_i$: Set of points in cluster $i$
- $c_i$: Centroid of cluster $i$
- $k$: Number of clusters

**Initialization**: K-Means++ for better convergence  
**Implementation**: `math_investigation/clustering/kmeans.py`

### Fuzzy C-Means (FCM)

Minimizes fuzzy objective function:

$$J_m(U, C) = \sum_{i=1}^{c} \sum_{j=1}^{n} u_{ij}^m ||x_j - c_i||^2$$

Where:
- $u_{ij} \in [0, 1]$: Membership of point $j$ to cluster $i$
- $m > 1$: Fuzziness parameter (typically 1.5-2.0)
- $\sum_{i=1}^{c} u_{ij} = 1$ (sum of memberships equals 1)

**Advantage**: Soft assignments allow questions to belong to multiple categories  
**Implementation**: `math_investigation/clustering/fcm.py`

## Evaluation Metrics

### Internal Metrics (no ground truth needed)
- **Silhouette Score**: Measures cluster cohesion and separation (-1 to 1, higher is better)
- **Davies-Bouldin Index**: Ratio of within-cluster to between-cluster distances (lower is better)
- **SSE/Inertia**: Within-cluster variance (lower is better, use elbow method)

### FCM-Specific Metrics
- **Fuzzy Partition Coefficient (FPC)**: Measures fuzziness of partition (0 to 1, higher is crisper)
- **Objective Function $J_m$**: Total weighted distance to centroids

## Usage

```bash
# Activate environment
source .venv/bin/activate

# Run Jupyter notebook
jupyter notebook faq_clustering_cima.ipynb

# Or use VS Code Jupyter extension
code faq_clustering_cima.ipynb
```

## Output Structure

Results are saved to `math_investigation/results/faq_generation/`:

```
results/faq_generation/
├── cima_faq_20260204_HHMMSS_centroids_k5.npy      # Cluster centroids
├── cima_faq_20260204_HHMMSS_labels_k5.npy         # Cluster assignments
├── cima_faq_20260204_HHMMSS_vocabulary.txt        # Feature names
├── cima_faq_20260204_HHMMSS_faq_structure.json    # FAQ entries by category
├── cima_faq_20260204_HHMMSS_analysis.json         # Cluster analysis
├── cima_faq_20260204_HHMMSS_question_lengths.png  # Question statistics
├── cima_faq_20260204_HHMMSS_clustering_metrics.png # Comparison plots
└── cima_faq_20260204_HHMMSS_cluster_distribution_k5.png
```

## Integration with TFG-Chatbot

### 1. Load Centroids for Classification

```python
# In chatbot/logic/tools/tools.py
import numpy as np
from math_investigation.nlp.tfidf import TFIDFVectorizer

# Load pre-trained centroids and vectorizer
centroids = np.load("results/faq_generation/cima_faq_..._centroids_k5.npy")
vectorizer = TFIDFVectorizer()
# Fit vectorizer with same vocabulary used during training

@tool
def classify_question_difficulty(question: str) -> dict:
    """
    Classify question difficulty using pre-trained cluster centroids.
    """
    q_vec = vectorizer.transform([question])
    distances = np.linalg.norm(q_vec - centroids, axis=1)
    cluster_id = np.argmin(distances)
    
    # Map cluster_id to difficulty level (from labeled centroids)
    difficulty_map = {0: "easy", 1: "medium", 2: "hard", ...}
    
    return {
        "cluster_id": int(cluster_id),
        "difficulty": difficulty_map.get(cluster_id, "unknown"),
        "confidence": float(1.0 / (distances[cluster_id] + 1e-6))
    }
```

### 2. Use FAQ Structure for Retrieval

```python
# Load FAQ structure into MongoDB or use in RAG
with open("results/faq_generation/cima_faq_..._faq_structure.json") as f:
    faq_data = json.load(f)

# Store in MongoDB
from chatbot.db.connection import get_database
db = get_database()
db.faqs.insert_one(faq_data)

# Retrieve similar FAQs in RAG tool
@tool
def search_faq(question: str) -> list:
    """Search FAQ entries similar to question."""
    # Classify question to cluster
    cluster_id = classify_question_difficulty(question)["cluster_id"]
    
    # Retrieve FAQ category
    faq = db.faqs.find_one({"faq_categories.category_id": cluster_id})
    return faq["faq_categories"][cluster_id]["faq_entries"]
```

### 3. Train Difficulty Centroids

See `scripts/train_difficulty_centroids.py` for labeling and training difficulty classifiers using these centroids.

## Comparison: Topic Modeling vs. FAQ Clustering

| Aspect | Topic Modeling (NMF) | FAQ Clustering (K-Means/FCM) |
|--------|---------------------|------------------------------|
| **Goal** | Discover latent themes in documents | Group similar questions for classification |
| **Output** | Topic-word distributions | Cluster centroids and assignments |
| **Use Case** | Content organization, document understanding | Question routing, difficulty prediction |
| **Method** | Matrix factorization ($V \approx WH$) | Distance-based clustering |
| **Interpretability** | Topics = word distributions | Clusters = representative questions |

Both approaches complement each other:
- **Topic modeling**: Understand *what* students talk about
- **Clustering**: Classify *how* students ask questions

## Dependencies

All implementations are from-scratch in `math_investigation/`:
- `nlp/tfidf.py` - TF-IDF vectorizer
- `clustering/kmeans.py` - K-Means with K-Means++
- `clustering/fcm.py` - Fuzzy C-Means
- `clustering/metrics.py` - Silhouette, Davies-Bouldin, ARI, NMI

## References

- TFG Mathematics thesis: Chapter on clustering algorithms
- K-Means paper: MacQueen (1967)
- FCM paper: Dunn (1973), Bezdek (1981)
- Integration: `scripts/train_difficulty_centroids.py`
