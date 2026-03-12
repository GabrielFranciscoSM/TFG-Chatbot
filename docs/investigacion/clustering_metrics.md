# Clustering Validation Metrics

## Overview

This document provides a technical and scientific summary of the clustering validation metrics implemented in the `math_investigation/clustering/metrics.py` module. These metrics are essential for evaluating the quality of clustering algorithms (K-Means, Fuzzy C-Means) used in the TFG's question classification system.

Clustering validation metrics fall into two main categories:
- **Internal metrics**: Evaluate clustering quality using only the data and cluster assignments (no ground truth required)
- **External metrics**: Measure agreement with ground truth labels (require labeled data)

## Internal Validation Metrics

### 1. Silhouette Score

#### Mathematical Definition

The Silhouette Score measures how similar a point is to its own cluster compared to other clusters. For each point $i$, the silhouette coefficient is:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

where:
- $a(i)$ = mean distance from point $i$ to other points in the same cluster
- $b(i)$ = mean distance from point $i$ to points in the nearest neighboring cluster

The overall Silhouette Score is the mean of all individual coefficients:

$$S = \frac{1}{N} \sum_{i=1}^{N} s(i)$$

#### Interpretation

- **Range**: $[-1, 1]$
- **+1**: Point is well-matched to its cluster and poorly matched to neighboring clusters (ideal)
- **0**: Point is on the border between two clusters
- **-1**: Point may have been assigned to the wrong cluster

#### When to Use

- Comparing different clustering algorithms or parameter settings
- Determining optimal number of clusters
- Assessing overall clustering quality without ground truth labels
- Works with any distance metric

#### Implementation Notes

The implementation in `metrics.py` computes pairwise distances efficiently using NumPy's `linalg.norm`. For large datasets, consider using approximate methods or sampling.

**Computational Complexity**: $O(N^2)$ where $N$ is the number of samples

---

### 2. Fuzzy Partition Coefficient (FPC)

#### Mathematical Definition

The Fuzzy Partition Coefficient is specifically designed for Fuzzy C-Means (FCM) clustering. It measures the degree of fuzziness in the partition:

$$\text{FPC} = \frac{1}{N} \sum_{i=1}^{N} \sum_{j=1}^{k} \mu_{ji}^2$$

where:
- $\mu_{ji}$ = membership degree of point $i$ in cluster $j$
- $k$ = number of clusters
- $N$ = number of samples

#### Interpretation

- **Range**: $[\frac{1}{k}, 1]$
- **1**: Crisp partition (each point belongs to exactly one cluster with $\mu = 1$)
- **$\frac{1}{k}$**: Maximum fuzziness (uniform membership across all clusters)
- Higher values indicate clearer cluster boundaries

#### When to Use

- Evaluating FCM clustering quality
- Selecting fuzziness parameter $m$ in FCM
- Comparing FCM results with different initializations
- **Not applicable** to crisp clustering methods (K-Means)

#### Advantages

- Simple and intuitive
- Computationally efficient: $O(N \cdot k)$
- No parameters required

#### Limitations

- Monotonically decreases with increasing $k$ (not suitable for selecting optimal $k$)
- Only measures fuzziness, not actual clustering quality
- Doesn't account for cluster geometry

---

### 3. Elbow Method

#### Methodology

The Elbow Method plots the Sum of Squared Errors (SSE) or within-cluster variance against the number of clusters $k$:

$$\text{SSE}(k) = \sum_{j=1}^{k} \sum_{x_i \in C_j} \|x_i - \mu_j\|^2$$

where:
- $C_j$ = cluster $j$
- $\mu_j$ = centroid of cluster $j$

#### Interpretation

- As $k$ increases, SSE decreases (more clusters = better fit to data)
- The "elbow" point represents optimal $k$ where:
  - Adding more clusters provides diminishing returns
  - Balance between model complexity and fit quality

#### When to Use

- Determining optimal number of clusters for K-Means
- Exploratory data analysis
- When no ground truth labels are available

#### Implementation Notes

The `elbow_method()` function in `metrics.py` runs K-Means for multiple $k$ values and returns both SSE and Silhouette scores for comprehensive analysis.

**Computational Complexity**: $O(k_{\max} \cdot N \cdot k \cdot i)$ where $i$ is iterations per K-Means run

#### Limitations

- Subjective interpretation of "elbow" location
- May not have clear elbow for some datasets
- Only applicable to distance-based clustering

---

## External Validation Metrics

### 4. Purity

#### Mathematical Definition

Purity measures the extent to which clusters contain samples from a single class:

$$\text{Purity} = \frac{1}{N} \sum_{k=1}^{K} \max_j |c_k \cap l_j|$$

where:
- $c_k$ = set of points in cluster $k$
- $l_j$ = set of points with ground truth label $j$
- $|c_k \cap l_j|$ = number of points in cluster $k$ with label $j$

#### Interpretation

- **Range**: $[0, 1]$
- **1**: Perfect clustering (each cluster contains only one class)
- **0**: Worst clustering
- Intuitively: weighted average of most frequent class in each cluster

#### When to Use

- Evaluating clustering with respect to known class labels
- Topic modeling evaluation (documents per topic)
- Simple and interpretable metric for labeled data

#### Limitations

- Not adjusted for chance (favors large numbers of clusters)
- Doesn't penalize splitting a class across multiple clusters
- Asymmetric: doesn't consider cluster purity from class perspective

---

### 5. Adjusted Rand Index (ARI)

#### Mathematical Definition

ARI measures the similarity between two clusterings, adjusted for chance:

$$\text{ARI} = \frac{\text{RI} - \mathbb{E}[\text{RI}]}{\max(\text{RI}) - \mathbb{E}[\text{RI}]}$$

where:
- $\text{RI}$ = Rand Index (fraction of pairs correctly classified)
- $\mathbb{E}[\text{RI}]$ = expected RI under random clustering

The computation uses the contingency table:

$$\text{ARI} = \frac{\sum_{ij} \binom{n_{ij}}{2} - \left[\sum_i \binom{a_i}{2} \sum_j \binom{b_j}{2}\right] / \binom{n}{2}}{\frac{1}{2}\left[\sum_i \binom{a_i}{2} + \sum_j \binom{b_j}{2}\right] - \left[\sum_i \binom{a_i}{2} \sum_j \binom{b_j}{2}\right] / \binom{n}{2}}$$

where $n_{ij}$ is the contingency table entry, $a_i$ and $b_j$ are marginal sums.

#### Interpretation

- **Range**: $[-1, 1]$ (though typically $[0, 1]$ for realistic clusterings)
- **1**: Perfect agreement between clusterings
- **0**: Agreement equivalent to random chance
- **< 0**: Agreement worse than random

#### When to Use

- Comparing clustering results with ground truth
- Evaluating different clustering algorithms
- Comparing multiple clustering solutions
- Preferred over simple accuracy for clustering

#### Advantages

- Adjusted for chance (accounts for random agreement)
- Symmetric: $\text{ARI}(U, V) = \text{ARI}(V, U)$
- Doesn't assume specific cluster structure
- Maximum value 1 for any number of clusters

#### Computational Complexity

$O(N + k_1 \cdot k_2)$ where $k_1, k_2$ are numbers of clusters in each partition

---

### 6. Normalized Mutual Information (NMI)

#### Mathematical Definition

NMI measures the mutual information between two clusterings, normalized by their entropies:

$$\text{NMI}(U, V) = \frac{2 \cdot I(U, V)}{H(U) + H(V)}$$

where:

**Mutual Information**:
$$I(U, V) = \sum_{i=1}^{k_U} \sum_{j=1}^{k_V} P(i, j) \log \frac{P(i, j)}{P(i) \cdot P(j)}$$

**Entropy**:
$$H(U) = -\sum_{i=1}^{k_U} P(i) \log P(i)$$

where:
- $P(i, j)$ = joint probability of point being in cluster $i$ of $U$ and cluster $j$ of $V$
- $P(i)$, $P(j)$ = marginal probabilities

#### Interpretation

- **Range**: $[0, 1]$
- **1**: Perfect correlation between clusterings
- **0**: No mutual information (independent clusterings)
- Measures information shared between two partitions

#### When to Use

- Comparing clustering with ground truth labels
- Evaluating information-theoretic quality of clustering
- Comparing clusterings with different numbers of clusters
- Alternative to ARI when information-theoretic interpretation is preferred

#### Advantages

- Information-theoretic foundation
- Normalized to $[0, 1]$ range
- Accounts for different numbers of clusters
- Symmetric metric

#### Relationship to Other Metrics

- NMI is related to variation of information (VI): $\text{VI} = H(U) + H(V) - 2I(U,V)$
- More sensitive to cluster fragmentation than ARI
- Often correlates highly with ARI but not identical

**Computational Complexity**: $O(N + k_1 \cdot k_2)$

---

## Metric Selection Guidelines

### For Model Selection (without ground truth)

| Task | Primary Metric | Secondary Metrics |
|------|---------------|-------------------|
| Optimal $k$ selection | Elbow Method + Silhouette | SSE decrease rate |
| K-Means quality | Silhouette Score | Within/between cluster variance |
| FCM fuzziness | FPC | Partition entropy |

### For Evaluation (with ground truth)

| Task | Primary Metric | Secondary Metrics |
|------|---------------|-------------------|
| General clustering quality | ARI | NMI, Purity |
| Topic modeling | Purity | NMI |
| Class separation | NMI | ARI |

### Combining Metrics

For robust evaluation, use multiple metrics:

```python
from math_investigation.clustering.metrics import (
    silhouette_score,
    adjusted_rand_index,
    normalized_mutual_information,
    evaluate_purity
)

# Internal evaluation
silhouette = silhouette_score(X, labels_pred)

# External evaluation (if ground truth available)
ari = adjusted_rand_index(labels_true, labels_pred)
nmi = normalized_mutual_information(labels_true, labels_pred)
purity = evaluate_purity(labels_pred, labels_true)

print(f"Silhouette: {silhouette:.3f}")
print(f"ARI: {ari:.3f}, NMI: {nmi:.3f}, Purity: {purity:.3f}")
```

---

## Implementation Details

### Module: `math_investigation/clustering/metrics.py`

All metrics are implemented from scratch using only NumPy, following educational principles of the TFG:

- **No scikit-learn dependencies** for core algorithms
- Optimized for clarity and educational value
- Efficient NumPy vectorization where possible
- Type hints and comprehensive docstrings

### Testing

Unit tests for all metrics are located in `math_investigation/tests/` and verify:
- Mathematical correctness with known examples
- Edge cases (single cluster, uniform assignment)
- Consistency with theoretical properties
- Numerical stability

---

## References

### Academic Sources

1. **Silhouette Score**: Rousseeuw, P.J. (1987). "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis". *Journal of Computational and Applied Mathematics*, 20, 53-65.

2. **ARI**: Hubert, L., & Arabie, P. (1985). "Comparing partitions". *Journal of Classification*, 2(1), 193-218.

3. **NMI**: Strehl, A., & Ghosh, J. (2002). "Cluster ensembles—a knowledge reuse framework for combining multiple partitions". *Journal of Machine Learning Research*, 3, 583-617.

4. **FPC**: Bezdek, J.C. (1974). "Numerical taxonomy with fuzzy sets". *Journal of Mathematical Biology*, 1(1), 57-71.

### Related Documentation

- [K-Means Implementation](./kmeans_algorithm.md) *(to be created)*
- [Fuzzy C-Means Implementation](./fcm_algorithm.md) *(to be created)*
- [Clustering Experiments](./clustering_experiments.md) *(to be created)*

---

## Appendix: Metric Comparison Table

| Metric | Type | Ground Truth Required | Range | Optimal Value | Complexity |
|--------|------|----------------------|-------|---------------|------------|
| Silhouette | Internal | No | [-1, 1] | 1 | $O(N^2)$ |
| FPC | Internal | No | [1/k, 1] | 1 | $O(N \cdot k)$ |
| Elbow | Internal | No | [0, ∞) | "Elbow" | $O(k \cdot N \cdot k \cdot i)$ |
| Purity | External | Yes | [0, 1] | 1 | $O(N)$ |
| ARI | External | Yes | [-1, 1] | 1 | $O(N + k^2)$ |
| NMI | External | Yes | [0, 1] | 1 | $O(N + k^2)$ |

---

*Last updated: February 5, 2026*
