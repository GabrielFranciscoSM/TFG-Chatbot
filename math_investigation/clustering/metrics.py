"""Clustering validation metrics.

This module provides metrics for evaluating clustering quality:
- Silhouette Score: Internal validation metric
- Adjusted Rand Index (ARI): External validation metric
- Normalized Mutual Information (NMI): External validation metric
- Fuzzy Partition Coefficient (FPC): FCM-specific metric
"""

from collections import Counter
from math import log

import numpy as np


def evaluate_purity(W: np.ndarray, labels_true: list[str] | np.ndarray) -> float:
    """Compute Cluster Purity.

    Purity = (1/N) * Σ_k max_j |c_k ∩ l_j|
    where c_k is a cluster and l_j is a ground truth class.

    Args:
        W: Document-topic matrix (n_samples x n_topics) or labels
        labels_true: Ground truth labels

    Returns:
        Purity score [0, 1]
    """
    if W.ndim > 1:
        # Use strongest topic as assignment
        predicted_topics = np.argmax(W, axis=1)
    else:
        predicted_topics = W

    unique_labels = list(set(labels_true))
    n_topics = len(np.unique(predicted_topics))
    n_classes = len(unique_labels)

    label_to_int = {label: i for i, label in enumerate(unique_labels)}
    true_int = np.array([label_to_int[label] for label in labels_true])

    contingency = np.zeros(
        (max(n_topics, np.max(predicted_topics).item() + 1), n_classes)
    )
    for pred, true in zip(predicted_topics, true_int, strict=True):
        contingency[pred, true] += 1

    purity = np.sum(np.max(contingency, axis=1)) / len(labels_true)
    return float(purity)


def silhouette_score(X: np.ndarray, labels: np.ndarray) -> float:
    """Compute Silhouette Score for clustering quality.

    s(i) = (b(i) - a(i)) / max(a(i), b(i))

    where:
    - a(i) = mean distance to points in same cluster
    - b(i) = mean distance to points in nearest other cluster

    Returns:
        Mean silhouette coefficient (range: -1 to 1, higher is better)
    """
    n_samples = X.shape[0]
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)

    if n_clusters < 2:
        return 0.0

    silhouette_vals = np.zeros(n_samples)

    for i in range(n_samples):
        # a(i): mean distance to points in same cluster
        same_cluster = X[labels == labels[i]]
        if len(same_cluster) > 1:
            a_i = np.mean(
                [
                    np.linalg.norm(X[i] - x)
                    for x in same_cluster
                    if not np.array_equal(x, X[i])
                ]
            )
        else:
            a_i = 0

        # b(i): mean distance to points in nearest other cluster
        b_i = float("inf")
        for cluster in unique_labels:
            if cluster != labels[i]:
                other_cluster = X[labels == cluster]
                if len(other_cluster) > 0:
                    mean_dist = np.mean(
                        [np.linalg.norm(X[i] - x) for x in other_cluster]
                    )
                    b_i = min(b_i, mean_dist)

        if b_i == float("inf"):
            b_i = 0

        # Silhouette coefficient
        if max(a_i, b_i) > 0:
            silhouette_vals[i] = (b_i - a_i) / max(a_i, b_i)
        else:
            silhouette_vals[i] = 0

    return float(np.mean(silhouette_vals))


def adjusted_rand_index(labels_true: np.ndarray, labels_pred: np.ndarray) -> float:
    """Compute Adjusted Rand Index (ARI).

    ARI measures clustering agreement adjusted for chance.
    ARI = (RI - Expected_RI) / (max(RI) - Expected_RI)

    Range: [-1, 1], where 1 = perfect match, 0 = random clustering

    Args:
        labels_true: Ground truth cluster labels
        labels_pred: Predicted cluster labels

    Returns:
        ARI score
    """
    n = len(labels_true)
    if n != len(labels_pred):
        raise ValueError("labels_true and labels_pred must have the same length")

    # Build contingency table
    classes = np.unique(labels_true)
    clusters = np.unique(labels_pred)

    contingency = np.zeros((len(classes), len(clusters)), dtype=int)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    cluster_to_idx = {c: i for i, c in enumerate(clusters)}

    for i in range(n):
        contingency[class_to_idx[labels_true[i]], cluster_to_idx[labels_pred[i]]] += 1

    # Compute sums
    sum_comb_c = sum(_comb2(contingency[:, j].sum()) for j in range(len(clusters)))
    sum_comb_k = sum(_comb2(contingency[i, :].sum()) for i in range(len(classes)))
    sum_comb = sum(
        _comb2(contingency[i, j])
        for i in range(len(classes))
        for j in range(len(clusters))
    )

    n_comb2 = _comb2(n)

    # ARI formula
    if n_comb2 == 0:
        return 0.0

    expected_index = (sum_comb_c * sum_comb_k) / n_comb2
    max_index = (sum_comb_c + sum_comb_k) / 2
    denominator = max_index - expected_index

    if denominator == 0:
        return 0.0 if sum_comb == expected_index else 1.0

    return (sum_comb - expected_index) / denominator


def _comb2(n: int) -> int:
    """Compute binomial coefficient C(n, 2) = n*(n-1)/2."""
    return n * (n - 1) // 2 if n >= 2 else 0


def normalized_mutual_information(
    labels_true: np.ndarray, labels_pred: np.ndarray
) -> float:
    """Compute Normalized Mutual Information (NMI).

    NMI = 2 * I(U,V) / (H(U) + H(V))

    where:
    - I(U,V) = mutual information
    - H(U), H(V) = entropy of each clustering

    Range: [0, 1], where 1 = perfect match

    Args:
        labels_true: Ground truth cluster labels
        labels_pred: Predicted cluster labels

    Returns:
        NMI score
    """
    n = len(labels_true)
    if n != len(labels_pred):
        raise ValueError("labels_true and labels_pred must have the same length")

    # Count occurrences
    true_counts = Counter(labels_true)
    pred_counts = Counter(labels_pred)

    # Joint counts
    joint_counts: Counter = Counter()
    for t, p in zip(labels_true, labels_pred, strict=True):
        joint_counts[(t, p)] += 1

    # Compute entropies
    h_true = _entropy(list(true_counts.values()), n)
    h_pred = _entropy(list(pred_counts.values()), n)

    # Compute mutual information
    mi = 0.0
    for (t, p), count in joint_counts.items():
        if count > 0:
            p_joint = count / n
            p_true = true_counts[t] / n
            p_pred = pred_counts[p] / n
            mi += p_joint * log(p_joint / (p_true * p_pred))

    # Normalize
    if h_true + h_pred == 0:
        return 0.0

    return 2 * mi / (h_true + h_pred)


def _entropy(counts: list[int], n: int) -> float:
    """Compute entropy from counts."""
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / n
            h -= p * log(p)
    return h


def fuzzy_partition_coefficient(membership: np.ndarray) -> float:
    """Compute Fuzzy Partition Coefficient (FPC) for FCM.

    FPC = (1/N) * Σ_i Σ_j (μ_ji)²

    Range: [1/k, 1], where:
    - 1 = crisp partition (each point belongs to exactly one cluster)
    - 1/k = maximum fuzziness (uniform membership)

    Args:
        membership: FCM membership matrix (k x N)

    Returns:
        FPC score
    """
    n_samples = membership.shape[1]
    fpc = np.sum(membership**2) / n_samples
    return float(fpc)


def elbow_method(X: np.ndarray, k_range: range, random_state: int = 42) -> dict:
    """Run Elbow Method to find optimal number of clusters.

    Args:
        X: Data matrix
        k_range: Range of k values to test
        random_state: Random seed

    Returns:
        Dictionary with k, sse, and silhouette scores
    """
    import logging

    from math_investigation.clustering.kmeans import KMeans

    logger = logging.getLogger(__name__)
    logger.info(f"Running Elbow Method for k in {k_range}")

    results: dict[str, list] = {"k": [], "sse": [], "silhouette": []}

    for k in k_range:
        logger.info(f"Elbow Method: testing k={k}")
        kmeans = KMeans(n_clusters=k, random_state=random_state)
        labels = kmeans.fit_predict(X)

        results["k"].append(k)
        results["sse"].append(kmeans.inertia_)

        if k >= 2:
            sil = silhouette_score(X, labels)
            results["silhouette"].append(sil)
        else:
            results["silhouette"].append(0)

    return results
