"""Integration example: clustering validation with GenericKMeans.

Demonstrates how to use metrics.py with clustering.py output.
"""

from __future__ import annotations

import logging

import numpy as np
from clustering import GenericKMeans

from validation.metrics.metrics import (
    ClusteringMetrics,
    evaluate_fuzzy_clustering,
    evaluate_hard_clustering,
    format_metrics,
)

logger = logging.getLogger(__name__)


def validate_kmeans_pipeline(
    X: np.ndarray,
    k_values: list[int],
    distance: str = "cosine",
    random_state: int | None = None,
) -> dict[int, ClusteringMetrics]:
    """Run K-Means clustering for multiple k and evaluate.

    Args:
        X: Data matrix (N × D)
        k_values: List of k to evaluate
        distance: Distance metric ('cosine' or 'euclidean')
        random_state: Random seed

    Returns:
        Dictionary mapping k -> ClusteringMetrics
    """
    results = {}

    for k in k_values:
        logger.info(f"Evaluating K-Means with k={k}, distance={distance}")

        model = GenericKMeans(
            n_clusters=k,
            algorithm="kmeans",
            distance=distance,
            random_state=random_state,
        )
        model.fit(X)

        metrics = evaluate_hard_clustering(X, model.labels_, metric=distance)
        results[k] = metrics
        logger.info(format_metrics(metrics, f"K-Means (k={k})"))

    return results


def validate_fcm_pipeline(
    X: np.ndarray,
    k_values: list[int],
    m: float = 2.0,
    distance: str = "cosine",
    random_state: int | None = None,
) -> dict[int, ClusteringMetrics]:
    """Run FCM clustering for multiple k and evaluate.

    Args:
        X: Data matrix (N × D)
        k_values: List of k to evaluate
        m: Fuzziness parameter
        distance: Distance metric ('cosine' or 'euclidean')
        random_state: Random seed

    Returns:
        Dictionary mapping k -> ClusteringMetrics
    """
    results = {}

    for k in k_values:
        logger.info(f"Evaluating FCM with k={k}, distance={distance}, m={m}")

        model = GenericKMeans(
            n_clusters=k,
            algorithm="fcm",
            distance=distance,
            m=m,
            random_state=random_state,
        )
        model.fit(X)

        metrics = evaluate_fuzzy_clustering(
            X,
            model.membership_,
            model.centroids_,
            m=m,
            distance=distance,
        )
        results[k] = metrics
        logger.info(format_metrics(metrics, f"FCM (k={k})"))

    return results


def find_optimal_k_by_asw(
    results: dict[int, ClusteringMetrics],
) -> tuple[int, float]:
    """Find optimal k based on maximum ASW.

    Args:
        results: Dictionary from validate_*_pipeline

    Returns:
        Tuple (optimal_k, max_asw)
    """
    k_asw = {k: m.asw for k, m in results.items()}
    optimal_k = max(k_asw, key=lambda k: k_asw[k])
    return optimal_k, k_asw[optimal_k]


def find_optimal_k_by_ch(
    results: dict[int, ClusteringMetrics],
) -> tuple[int, float]:
    """Find optimal k based on maximum CH.

    Args:
        results: Dictionary from validate_*_pipeline

    Returns:
        Tuple (optimal_k, max_ch)
    """
    k_ch = {k: m.ch for k, m in results.items()}
    optimal_k = max(k_ch, key=lambda k: k_ch[k])
    return optimal_k, k_ch[optimal_k]


def print_results_table(results: dict[int, ClusteringMetrics]) -> None:
    """Print results as a formatted table.

    Args:
        results: Dictionary from validate_*_pipeline
    """
    print("\nResults Summary:")
    print("-" * 80)
    print(f"{'k':>3} {'ASW':>10} {'CH':>12} {'PC':>10} {'PE':>10} {'XB':>10}")
    print("-" * 80)

    for k in sorted(results.keys()):
        m = results[k]
        pc_str = f"{m.pc:10.4f}" if m.pc is not None else "        N/A"
        pe_str = f"{m.pe:10.4f}" if m.pe is not None else "        N/A"
        xb_str = f"{m.xb:10.4f}" if m.xb is not None else "        N/A"

        print(f"{k:3d} {m.asw:10.4f} {m.ch:12.4f} {pc_str} {pe_str} {xb_str}")

    print("-" * 80)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s - %(levelname)s - %(message)s",
    )

    # Example: Generate synthetic embeddings
    np.random.seed(42)
    n_samples, n_features = 300, 50
    X = np.random.randn(n_samples, n_features)

    # Normalize for cosine metric
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X = X / norms

    # Cluster with different k values
    k_values = [2, 3, 4, 5, 6, 7, 8]

    # K-Means with cosine distance (Spherical K-Means)
    print("=" * 80)
    print("SPHERICAL K-MEANS (cosine distance)")
    print("=" * 80)
    kmeans_results = validate_kmeans_pipeline(
        X, k_values, distance="cosine", random_state=42
    )
    print_results_table(kmeans_results)

    optimal_k_asw, asw_value = find_optimal_k_by_asw(kmeans_results)
    optimal_k_ch, ch_value = find_optimal_k_by_ch(kmeans_results)
    print(f"\nOptimal k by ASW: {optimal_k_asw} (ASW={asw_value:.4f})")
    print(f"Optimal k by CH:  {optimal_k_ch} (CH={ch_value:.4f})")

    # FCM with cosine distance (Spherical FCM)
    print("\n" + "=" * 80)
    print("SPHERICAL FCM (cosine distance, m=2.0)")
    print("=" * 80)
    fcm_results = validate_fcm_pipeline(
        X, k_values, m=2.0, distance="cosine", random_state=42
    )
    print_results_table(fcm_results)

    optimal_k_asw, asw_value = find_optimal_k_by_asw(fcm_results)
    optimal_k_ch, ch_value = find_optimal_k_by_ch(fcm_results)
    print(f"\nOptimal k by ASW: {optimal_k_asw} (ASW={asw_value:.4f})")
    print(f"Optimal k by CH:  {optimal_k_ch} (CH={ch_value:.4f})")
