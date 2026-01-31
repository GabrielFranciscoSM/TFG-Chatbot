#!/usr/bin/env python3
"""Comparison CLI for NMF variants.

Compares Frobenius-norm NMF on TF-IDF vs KL-divergence NMF on BoW.
"""

import argparse
import logging

from math_investigation.clustering.metrics import evaluate_purity
from math_investigation.nlp import BoWVectorizer, TFIDFVectorizer
from math_investigation.topic_modeling import NMF
from math_investigation.utils import load_synthetic_dataset

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_experiment(
    name: str,
    documents: list[str],
    labels: list[int],
    vectorizer_type: str,
    cost: str,
    n_topics: int,
):
    logger.info(f"\n--- Running Experiment: {name} ---")

    from typing import Any
    vec: Any
    if vectorizer_type == "tfidf":
        vec = TFIDFVectorizer(max_features=500)
    else:
        vec = BoWVectorizer(max_features=500)

    X = vec.fit_transform(documents)

    nmf = NMF(n_components=n_topics, cost=cost, max_iter=200, random_state=42)
    nmf.fit(X)

    purity = evaluate_purity(nmf.W_, labels)
    error = nmf.reconstruction_errors_[-1]

    print(f"Results for {name}:")
    print(f"  Final Error: {error:.4f}")
    print(f"  Purity: {purity:.4f}")

    feature_names = vec.get_feature_names()
    print("  Top words per topic:")
    top_n = 5 # Defined top_n for clarity
    if nmf.H_ is None:
        logger.warning("NMF components not found")
        return purity

    for i, topic_vec in enumerate(nmf.H_):
        top_indices = np.argsort(topic_vec)[::-1][:top_n]
        words = [feature_names[j] for j in top_indices]
        print(f"    Topic {i}: {', '.join(words)}")

    return purity


def main():
    parser = argparse.ArgumentParser(description="Compare NMF Configuration Variants")
    parser.add_argument("--n-topics", type=int, default=5, help="Number of topics")
    parser.add_argument(
        "--data", type=str, default="math_investigation/data/synthetic_dataset.json"
    )
    parser.add_argument("--test-mode", action="store_true")

    args = parser.parse_args()

    documents, labels = load_synthetic_dataset(args.data)
    if args.test_mode:
        documents = documents[:50]
        labels = labels[:50]

    # Exp 1: Baseline
    p1 = run_experiment(
        "TF-IDF + Frobenius", documents, labels, "tfidf", "frobenius", args.n_topics
    )

    # Exp 2: BoW + KL
    p2 = run_experiment(
        "BoW + KL-Divergence", documents, labels, "bow", "kl", args.n_topics
    )

    print("\n" + "=" * 40)
    print("COMPARISON SUMMARY")
    print("=" * 40)
    print(f"TF-IDF + Frobenius Purity: {p1:.4f}")
    print(f"BoW + KL-Divergence Purity: {p2:.4f}")
    diff = p2 - p1
    print(f"Difference: {diff:+.4f}")
    if diff > 0:
        print(">> KL Wins! (Matches count-data theory)")
    else:
        print(">> Frobenius Wins!")
    print("=" * 40)


if __name__ == "__main__":
    main()
