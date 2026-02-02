#!/usr/bin/env python3
"""CLI for running clustering experiments with K-Means and FCM.

Usage:
    python -m math_investigation.cli.run_clustering --k 5 --vectorizer tfidf
    python -m math_investigation.cli.run_clustering --k 5 --vectorizer emb --data data/synthetic_dataset.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

from math_investigation.clustering import (
    FuzzyCMeans,
    KMeans,
    adjusted_rand_index,
    fuzzy_partition_coefficient,
    normalized_mutual_information,
    silhouette_score,
)
from math_investigation.clustering.fcm import analyze_fuzzy_documents
from math_investigation.clustering.metrics import elbow_method
from math_investigation.nlp import BoWVectorizer, OllamaEmbeddings, TFIDFVectorizer
from math_investigation.utils.data import (
    find_nearest_to_centroids,
    load_synthetic_dataset,
)
from math_investigation.visualization import plot_elbow, plot_fcm_membership_heatmap

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_clustering(
    documents: list[str],
    true_labels: list[int] | None,
    k: int,
    vectorizer_type: str,
    output_dir: str,
    m: float = 2.0,
    random_state: int = 42,
) -> dict:
    """Run K-Means and FCM clustering with comprehensive metrics.

    Args:
        documents: List of document texts
        true_labels: Ground truth labels (for external validation)
        k: Number of clusters
        vectorizer_type: 'tfidf', 'bow', or 'emb'
        output_dir: Output directory for results and plots
        m: FCM fuzziness parameter
        random_state: Random seed

    Returns:
        Dictionary with all metrics and results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Step 1: Vectorization
    from typing import Any

    vectorizer: Any
    if vectorizer_type == "tfidf":
        vectorizer = TFIDFVectorizer(max_features=1000)
    elif vectorizer_type == "bow":
        vectorizer = BoWVectorizer(max_features=1000)
    elif vectorizer_type == "embeddings":
        vectorizer = OllamaEmbeddings()
    else:
        raise ValueError(f"Unknown vectorizer: {vectorizer_type}")

    X = vectorizer.fit_transform(documents)

    results: dict = {
        "vectorizer": vectorizer_type,
        "n_documents": len(documents),
        "n_features": X.shape[1],
        "n_clusters": k,
        "kmeans": {},
        "fcm": {},
    }

    # Step 2: K-Means clustering
    logger.info(f"Running K-Means with k={k}...")
    kmeans = KMeans(n_clusters=k, random_state=random_state)
    kmeans_labels = kmeans.fit_predict(X)

    results["kmeans"]["sse"] = float(kmeans.inertia_)
    results["kmeans"]["n_iter"] = kmeans.n_iter_
    results["kmeans"]["sse_history"] = kmeans.sse_history_
    results["kmeans"]["silhouette"] = silhouette_score(X, kmeans_labels)

    if true_labels is not None:
        true_labels_arr = np.array(true_labels)
        results["kmeans"]["ari"] = adjusted_rand_index(true_labels_arr, kmeans_labels)
        results["kmeans"]["nmi"] = normalized_mutual_information(
            true_labels_arr, kmeans_labels
        )

    # Step 3: FCM clustering
    logger.info(f"Running FCM with k={k}, m={m}...")
    fcm = FuzzyCMeans(n_clusters=k, m=m, random_state=random_state)
    fcm_labels = fcm.fit_predict(X)

    assert fcm.membership_ is not None
    results["fcm"]["jm"] = float(fcm.jm_)
    results["fcm"]["n_iter"] = fcm.n_iter_
    results["fcm"]["jm_history"] = fcm.jm_history_
    results["fcm"]["silhouette"] = silhouette_score(X, fcm_labels)
    results["fcm"]["fpc"] = fuzzy_partition_coefficient(fcm.membership_)

    if true_labels is not None:
        results["fcm"]["ari"] = adjusted_rand_index(true_labels_arr, fcm_labels)
        results["fcm"]["nmi"] = normalized_mutual_information(
            true_labels_arr, fcm_labels
        )

    # Step 4: Analyze fuzzy documents (documents with membership in multiple clusters)
    fuzzy_docs = analyze_fuzzy_documents(fcm.membership_, documents)
    results["fcm"]["fuzzy_documents_count"] = len(fuzzy_docs)
    results["fcm"]["fuzzy_documents"] = fuzzy_docs[:10]  # Top 10 for report

    # Step 5: Generate FAQs from centroids
    assert kmeans.centroids_ is not None
    nearest_indices = find_nearest_to_centroids(X, kmeans.centroids_)
    faqs = [
        {"cluster": i, "question": documents[idx]}
        for i, idx in enumerate(nearest_indices)
    ]
    results["faqs"] = faqs

    # Step 6: Save FAQs to file
    faqs_path = output_path / "faqs.json"
    with open(faqs_path, "w", encoding="utf-8") as f:
        json.dump(
            {"faqs": faqs, "vectorizer": vectorizer_type, "k": k},
            f,
            indent=2,
            ensure_ascii=False,
        )
    logger.info(f"FAQs saved to {faqs_path}")

    # Step 7: Save visualizations
    plot_fcm_membership_heatmap(
        fcm.membership_, str(output_path / "fcm_membership_heatmap.png")
    )

    # Step 8: Save full results
    results_path = output_path / "results.json"
    # Convert numpy types for JSON serialization
    serializable_results = json.loads(
        json.dumps(
            results, default=lambda x: float(x) if isinstance(x, np.floating) else x
        )
    )
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    logger.info(f"Results saved to {results_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Run clustering experiments")
    parser.add_argument("--k", type=int, default=5, help="Number of clusters")
    parser.add_argument(
        "--vectorizer",
        type=str,
        default="tfidf",
        choices=["tfidf", "bow", "emb"],
        help="Vectorization method",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="math_investigation/data/synthetic_dataset.json",
        help="Path to dataset",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="math_investigation/results/clustering",
        help="Output directory",
    )
    parser.add_argument("--m", type=float, default=2.0, help="FCM fuzziness parameter")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--elbow",
        action="store_true",
        help="Run elbow method to find optimal k",
    )
    parser.add_argument(
        "--elbow-range",
        type=str,
        default="2,10",
        help="Range for elbow method (min,max)",
    )

    args = parser.parse_args()

    # Load data
    try:
        documents, true_labels = load_synthetic_dataset(args.data)
    except FileNotFoundError:
        logger.error(f"Dataset not found: {args.data}")
        sys.exit(1)

    # Run elbow method if requested
    if args.elbow:
        min_k, max_k = map(int, args.elbow_range.split(","))
        logger.info(f"Running Elbow Method for k in range({min_k}, {max_k + 1})")

        vectorizer = TFIDFVectorizer(max_features=1000)
        X = vectorizer.fit_transform(documents)

        elbow_results = elbow_method(X, range(min_k, max_k + 1), random_state=args.seed)
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        plot_elbow(elbow_results, str(output_path / "elbow_method.png"))

        # Find optimal k (highest silhouette)
        best_idx = np.argmax(elbow_results["silhouette"])
        best_k = elbow_results["k"][best_idx]
        logger.info(f"Optimal k by Silhouette Score: {best_k}")

    # Run clustering
    results = run_clustering(
        documents=documents,
        true_labels=true_labels,
        k=args.k,
        vectorizer_type=args.vectorizer,
        output_dir=args.output,
        m=args.m,
        random_state=args.seed,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("CLUSTERING RESULTS SUMMARY")
    print("=" * 60)
    print(f"Documents: {results['n_documents']}")
    print(f"Features: {results['n_features']}")
    print(f"Clusters: {results['n_clusters']}")
    print(f"Vectorizer: {results['vectorizer']}")
    print()
    print("K-MEANS:")
    print(f"  SSE: {results['kmeans']['sse']:.4f}")
    print(f"  Silhouette Score: {results['kmeans']['silhouette']:.4f}")
    if "ari" in results["kmeans"]:
        print(f"  Adjusted Rand Index: {results['kmeans']['ari']:.4f}")
        print(f"  Normalized Mutual Information: {results['kmeans']['nmi']:.4f}")
    print()
    print("FUZZY C-MEANS:")
    print(f"  J_m: {results['fcm']['jm']:.4f}")
    print(f"  Silhouette Score: {results['fcm']['silhouette']:.4f}")
    print(f"  Fuzzy Partition Coefficient: {results['fcm']['fpc']:.4f}")
    print(f"  Fuzzy Documents: {results['fcm']['fuzzy_documents_count']}")
    if "ari" in results["fcm"]:
        print(f"  Adjusted Rand Index: {results['fcm']['ari']:.4f}")
        print(f"  Normalized Mutual Information: {results['fcm']['nmi']:.4f}")
    print()
    print("GENERATED FAQs:")
    for faq in results["faqs"]:
        print(f"  Cluster {faq['cluster']}: {faq['question'][:80]}...")
    print("=" * 60)


if __name__ == "__main__":
    main()
