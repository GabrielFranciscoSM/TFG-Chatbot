"""Clustering validation metrics for hard and fuzzy clustering.

Implements:
- Silhouette Coefficient (ASW)
- Calinski-Harabasz Index (CH)
- Partition Coefficient (PC) - FCM only
- Partition Entropy (PE) - FCM only
- Xie-Beni Index (XB) - FCM only
"""

from __future__ import annotations

import logging
from typing import NamedTuple

import numpy as np

logger = logging.getLogger(__name__)


class ClusteringMetrics(NamedTuple):
    """Container for clustering validation metrics."""

    asw: float  # Average Silhouette Width
    ch: float  # Calinski-Harabasz Index
    pc: float | None = None  # Partition Coefficient (FCM only)
    pe: float | None = None  # Partition Entropy (FCM only)
    xb: float | None = None  # Xie-Beni Index (FCM only)


def _normalize_vectors(X: np.ndarray) -> np.ndarray:
    """L2 normalize vectors row-wise."""
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return X / norms


def _pairwise_cosine_distance(X: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Compute cosine distance matrix between samples X and centroids C.

    Args:
        X: Data matrix (N × D)
        C: Centroid matrix (K × D)

    Returns:
        Distance matrix: (N × K)
    """
    Xn = _normalize_vectors(X)
    Cn = _normalize_vectors(C)
    cos_sims = np.dot(Xn, Cn.T)
    return np.clip(1.0 - cos_sims, 0.0, None)


def _pairwise_distances(
    X: np.ndarray,
    metric: str = "cosine",
) -> np.ndarray:
    """Compute pairwise distance matrix for all points in X.

    Args:
        X: Data matrix (N × D)
        metric: Distance metric ('cosine' or 'euclidean')

    Returns:
        Distance matrix: (N × N)
    """
    n_samples = X.shape[0]
    distances = np.zeros((n_samples, n_samples))

    if metric == "cosine":
        X_norm = _normalize_vectors(X)
        cos_sims = np.dot(X_norm, X_norm.T)
        distances = np.clip(1.0 - cos_sims, 0.0, None)
    elif metric == "euclidean":
        diff = X[:, None, :] - X[None, :, :]
        distances = np.linalg.norm(diff, axis=2)
    else:
        raise ValueError(f"Unknown metric: {metric}")

    return distances


def silhouette_score(
    X: np.ndarray,
    labels: np.ndarray,
    metric: str = "cosine",
) -> float:
    """Calculate Silhouette Coefficient (average silhouette width).

    For each sample i:
    - a(i) = mean distance to other points in same cluster
    - b(i) = min mean distance to points in other clusters
    - s(i) = (b(i) - a(i)) / max(a(i), b(i))

    ASW = mean(s(i))

    Args:
        X: Data matrix (N × D)
        labels: Hard cluster assignments (N,)
        metric: Distance metric ('cosine' or 'euclidean')

    Returns:
        Silhouette score in range [-1, 1]
    """
    n_samples = X.shape[0]
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)

    if n_clusters == 1:
        return 0.0

    # Compute pairwise distances
    distances = _pairwise_distances(X, metric=metric)

    silhouettes = np.zeros(n_samples)

    for i in range(n_samples):
        # Cluster that sample i belongs to
        cluster_i = labels[i]

        # Indices of samples in the same cluster (excluding i)
        same_cluster_mask = (labels == cluster_i) & (np.arange(n_samples) != i)
        same_cluster_indices = np.where(same_cluster_mask)[0]

        # a(i): mean distance to other points in same cluster
        if len(same_cluster_indices) > 0:
            a_i = np.mean(distances[i, same_cluster_indices])
        else:
            a_i = 0.0

        # b(i): min mean distance to points in other clusters
        b_i = np.inf
        for cluster_j in unique_labels:
            if cluster_j == cluster_i:
                continue
            other_cluster_mask = labels == cluster_j
            other_cluster_indices = np.where(other_cluster_mask)[0]
            if len(other_cluster_indices) > 0:
                mean_dist = np.mean(distances[i, other_cluster_indices])
                b_i = min(b_i, mean_dist)

        # Silhouette coefficient for sample i
        if b_i == np.inf:
            # No other clusters (shouldn't happen if n_clusters > 1)
            silhouettes[i] = 0.0
        else:
            denom = max(a_i, b_i)
            if denom > 0:
                silhouettes[i] = (b_i - a_i) / denom
            else:
                silhouettes[i] = 0.0

    return float(np.mean(silhouettes))


def calinski_harabasz_score(
    X: np.ndarray,
    labels: np.ndarray,
) -> float:
    """Calculate Calinski-Harabasz Index.

    Ratio of between-cluster to within-cluster dispersion.
    CH = (BCSS / (k - 1)) / (WCSS / (n - k))

    Higher is better.

    Args:
        X: Data matrix (N × D)
        labels: Hard cluster assignments (N,)

    Returns:
        Calinski-Harabasz index (≥ 0)
    """
    n_samples, n_features = X.shape
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)

    if n_clusters == 1 or n_clusters == n_samples:
        return 0.0

    # Global centroid
    centroid_global = np.mean(X, axis=0)

    # Between-cluster sum of squares (BCSS)
    bcss = 0.0
    for cluster_label in unique_labels:
        cluster_mask = labels == cluster_label
        cluster_samples = X[cluster_mask]
        n_cluster = cluster_samples.shape[0]

        # Centroid of this cluster
        centroid_cluster = np.mean(cluster_samples, axis=0)

        # Sum of squared distances from cluster centroid to global centroid
        diff = centroid_cluster - centroid_global
        bcss += n_cluster * np.sum(diff**2)

    # Within-cluster sum of squares (WCSS)
    wcss = 0.0
    for cluster_label in unique_labels:
        cluster_mask = labels == cluster_label
        cluster_samples = X[cluster_mask]

        # Centroid of this cluster
        centroid_cluster = np.mean(cluster_samples, axis=0)

        # Sum of squared distances from cluster samples to cluster centroid
        diff = cluster_samples - centroid_cluster[None, :]
        wcss += np.sum(diff**2)

    # Avoid division by zero
    if wcss == 0:
        return 0.0

    # CH = (BCSS / (k - 1)) / (WCSS / (n - k))
    ch = (bcss / (n_clusters - 1)) / (wcss / (n_samples - n_clusters))

    return float(ch)


def average_silhouette_width(
    X: np.ndarray,
    labels: np.ndarray,
    metric: str = "cosine",
) -> float:
    """Calculate Average Silhouette Width (ASW).

    Measures cohesion and separation of clusters.
    Range: [-1, 1]
    - Close to 1: well-clustered
    - Close to 0: ambiguous
    - Close to -1: misclassified

    Args:
        X: Data matrix (N × D)
        labels: Hard cluster assignments (N,)
        metric: Distance metric ('cosine' or 'euclidean'). Default: 'cosine'

    Returns:
        ASW score
    """
    if len(np.unique(labels)) == 1:
        logger.warning("Only one cluster found; ASW is undefined. Returning 0.0")
        return 0.0

    asw = silhouette_score(X, labels, metric=metric)
    logger.debug(f"ASW: {asw:.4f}")
    return float(asw)


def calinski_harabasz_index(
    X: np.ndarray,
    labels: np.ndarray,
) -> float:
    """Calculate Calinski-Harabasz Index (CH).

    Ratio of between-cluster to within-cluster variance.
    Range: [0, ∞); higher is better
    Faster than Silhouette (no O(N²) complexity)

    Args:
        X: Data matrix (N × D)
        labels: Hard cluster assignments (N,)

    Returns:
        CH index
    """
    if len(np.unique(labels)) == 1:
        logger.warning("Only one cluster found; CH is undefined. Returning 0.0")
        return 0.0

    ch = calinski_harabasz_score(X, labels)
    logger.debug(f"CH: {ch:.4f}")
    return float(ch)


def partition_coefficient(membership: np.ndarray) -> float:
    """Calculate Partition Coefficient (PC) for FCM.

    Measures partition crispness; higher is better.
    Range: [1/K, 1]
    - 1/K: completely fuzzy (uniform distribution)
    - 1: completely crisp (hard assignments)

    Formula: PC = (1/N) * Σ Σ u_ji²

    Args:
        membership: Membership matrix (N × K), where sum(u_ij) = 1 per row

    Returns:
        PC score
    """
    N, K = membership.shape
    pc = (1.0 / N) * np.sum(membership**2)
    logger.debug(f"PC: {pc:.4f}")
    return float(pc)


def partition_entropy(membership: np.ndarray) -> float:
    """Calculate Partition Entropy (PE) for FCM.

    Measures partition fuzziness; lower is better.
    Range: [0, log(K)]
    - 0: completely crisp
    - log(K): completely fuzzy

    Formula: PE = -(1/N) * Σ Σ u_ji * log(u_ji)

    Args:
        membership: Membership matrix (N × K), where sum(u_ij) = 1 per row

    Returns:
        PE score
    """
    N, K = membership.shape
    eps = 1e-12

    # Handle u_ij = 0 case (0 * log(0) = 0)
    u_safe = np.where(membership > eps, membership, eps)
    pe = -(1.0 / N) * np.sum(membership * np.log(u_safe))

    logger.debug(f"PE: {pe:.4f}")
    return float(pe)


def xie_beni_index(
    X: np.ndarray,
    membership: np.ndarray,
    centroids: np.ndarray,
    m: float = 2.0,
    distance: str = "cosine",
) -> float:
    """Calculate Xie-Beni Index (XB) for FCM.

    Combines membership information with geometric separation.
    Range: [0, ∞); lower is better

    Formula: XB = Σ Σ u_ji^m ||x_i - c_j||² / (N * min ||c_i - c_j||²)

    Args:
        X: Data matrix (N × D)
        membership: Membership matrix (N × K), where sum(u_ij) = 1 per row
        centroids: Centroid matrix (K × D)
        m: Fuzziness parameter (default: 2.0)
        distance: Distance metric ('cosine' or 'euclidean'). Default: 'cosine'

    Returns:
        XB index
    """
    N, K = membership.shape

    # Compute distance matrix: (N × K)
    if distance == "cosine":
        distances = _pairwise_cosine_distance(X, centroids)
    else:
        diff = X[:, None, :] - centroids[None, :, :]
        distances = np.linalg.norm(diff, axis=2)

    # Numerator: Σ Σ u_ji^m * ||x_i - c_j||²
    numerator = np.sum((membership**m) * (distances**2))

    # Denominator: N * min ||c_i - c_j||²
    if distance == "cosine":
        centroid_distances = _pairwise_cosine_distance(centroids, centroids)
    else:
        diff = centroids[:, None, :] - centroids[None, :, :]
        centroid_distances = np.linalg.norm(diff, axis=2)

    # Exclude diagonal (self-distances)
    np.fill_diagonal(centroid_distances, np.inf)
    min_centroid_distance = np.min(centroid_distances)

    if min_centroid_distance == 0:
        logger.warning("Centroids coincide; XB is infinite. Returning np.inf")
        return float(np.inf)

    denominator = N * (min_centroid_distance**2)
    xb = numerator / denominator

    logger.debug(f"XB: {xb:.4f}")
    return float(xb)


def evaluate_hard_clustering(
    X: np.ndarray,
    labels: np.ndarray,
    metric: str = "cosine",
) -> ClusteringMetrics:
    """Evaluate hard clustering (K-Means, Spherical K-Means).

    Args:
        X: Data matrix (N × D)
        labels: Hard cluster assignments (N,)
        metric: Distance metric ('cosine' or 'euclidean'). Default: 'cosine'

    Returns:
        ClusteringMetrics with ASW and CH
    """
    asw = average_silhouette_width(X, labels, metric=metric)
    ch = calinski_harabasz_index(X, labels)

    return ClusteringMetrics(asw=asw, ch=ch)


def evaluate_fuzzy_clustering(
    X: np.ndarray,
    membership: np.ndarray,
    centroids: np.ndarray,
    m: float = 2.0,
    distance: str = "cosine",
) -> ClusteringMetrics:
    """Evaluate fuzzy clustering (FCM, Spherical FCM).

    Args:
        X: Data matrix (N × D)
        membership: Membership matrix (N × K), normalized per row
        centroids: Centroid matrix (K × D)
        m: Fuzziness parameter (default: 2.0)
        distance: Distance metric ('cosine' or 'euclidean'). Default: 'cosine'

    Returns:
        ClusteringMetrics with ASW, CH, PC, PE, XB
    """
    # Get hard labels for ASW and CH
    labels = np.argmax(membership, axis=1)

    asw = average_silhouette_width(X, labels, metric=distance)
    ch = calinski_harabasz_index(X, labels)
    pc = partition_coefficient(membership)
    pe = partition_entropy(membership)
    xb = xie_beni_index(X, membership, centroids, m=m, distance=distance)

    return ClusteringMetrics(asw=asw, ch=ch, pc=pc, pe=pe, xb=xb)


def format_metrics(metrics: ClusteringMetrics, name: str = "") -> str:
    """Format metrics for display.

    Args:
        metrics: ClusteringMetrics instance
        name: Optional name for the result set

    Returns:
        Formatted string representation
    """
    lines = []
    if name:
        lines.append(f"Metrics for {name}:")

    lines.append(f"  ASW (Silhouette):     {metrics.asw:8.4f}")
    lines.append(f"  CH (Calinski-Harabasz): {metrics.ch:8.4f}")

    if metrics.pc is not None:
        lines.append(f"  PC (Partition Coeff):  {metrics.pc:8.4f}")
    if metrics.pe is not None:
        lines.append(f"  PE (Partition Entropy): {metrics.pe:8.4f}")
    if metrics.xb is not None:
        lines.append(f"  XB (Xie-Beni):        {metrics.xb:8.4f}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage with synthetic data
    logging.basicConfig(level=logging.DEBUG)

    # Generate synthetic data
    np.random.seed(42)
    X = np.random.randn(100, 10)
    X = _normalize_vectors(X)  # Normalize for cosine metric

    # Example 1: Hard clustering (K-Means)
    print("=" * 60)
    print("Example 1: Hard Clustering (K-Means)")
    print("=" * 60)
    labels_hard = np.random.randint(0, 5, size=100)
    metrics_hard = evaluate_hard_clustering(X, labels_hard, metric="cosine")
    print(format_metrics(metrics_hard, "K-Means"))

    # Example 2: Fuzzy clustering (FCM)
    print("\n" + "=" * 60)
    print("Example 2: Fuzzy Clustering (FCM)")
    print("=" * 60)
    # Create synthetic membership matrix
    membership = np.random.dirichlet(np.ones(5), size=100)
    centroids = _normalize_vectors(np.random.randn(5, 10))

    metrics_fuzzy = evaluate_fuzzy_clustering(
        X, membership, centroids, m=2.0, distance="cosine"
    )
    print(format_metrics(metrics_fuzzy, "FCM"))
