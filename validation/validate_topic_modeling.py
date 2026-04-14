"""Integration example: topic modeling validation with NMF.

Demonstrates how to use topic_modeling_metrics.py with nmf.py output.
"""

from __future__ import annotations

import logging

import numpy as np
from nmf import NMF

from math_service.services.nlp.utils import tokenize
from validation.metrics.topic_modeling_metrics import (
    TopicModelMetrics,
    evaluate_topic_modeling,
    format_metrics,
)
from validation.representation.bow import BoWVectorizer
from validation.representation.tfidf import TFIDFVectorizer

logger = logging.getLogger(__name__)


def build_document_term_matrix(
    documents: list[str],
    representation: str = "tfidf",
    max_features: int = 1000,
    min_df: int = 2,
) -> tuple[np.ndarray, list[str]]:
    """Build a document-term matrix and return it with the vocabulary.

    Args:
        documents: Raw text documents.
        representation: "tfidf" or "bow".
        max_features: Maximum vocabulary size.
        min_df: Minimum document frequency.

    Returns:
        Tuple of (document-term matrix, feature names).
    """
    vectorizer: TFIDFVectorizer | BoWVectorizer
    if representation == "tfidf":
        vectorizer = TFIDFVectorizer(max_features=max_features, min_df=min_df)
    elif representation == "bow":
        vectorizer = BoWVectorizer(max_features=max_features, min_df=min_df)
    else:
        raise ValueError("representation must be 'tfidf' or 'bow'")

    matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names()
    return matrix, feature_names


def extract_topics(
    topic_term_matrix: np.ndarray,
    feature_names: list[str],
    top_n: int = 10,
) -> list[list[str]]:
    """Extract top words per topic from the NMF topic-term matrix."""
    topics: list[list[str]] = []

    for topic_weights in topic_term_matrix:
        top_indices = np.argsort(topic_weights)[::-1][:top_n]
        topics.append([feature_names[index] for index in top_indices])

    return topics


def validate_nmf_pipeline(
    documents: list[str],
    k_values: list[int],
    representation: str = "tfidf",
    max_features: int = 1000,
    min_df: int = 2,
    top_n_words: int = 10,
    cost: str = "frobenius",
    random_state: int | None = None,
) -> dict[int, TopicModelMetrics]:
    """Run NMF topic modeling for multiple k and evaluate.

    Args:
        documents: Raw text documents.
        k_values: List of k values to evaluate.
        representation: "tfidf" or "bow".
        max_features: Maximum vocabulary size.
        min_df: Minimum document frequency for a term.
        top_n_words: Number of top words to extract per topic.
        cost: NMF cost function ('frobenius' or 'kl').
        random_state: Random seed.

    Returns:
        Dictionary mapping k -> TopicModelMetrics.
    """
    results: dict[int, TopicModelMetrics] = {}
    tokenized_documents = [tokenize(document) for document in documents]

    matrix, feature_names = build_document_term_matrix(
        documents,
        representation=representation,
        max_features=max_features,
        min_df=min_df,
    )

    for k in k_values:
        logger.info(
            f"Evaluating NMF with k={k}, representation={representation}, cost={cost}"
        )

        model = NMF(
            n_components=k,
            max_iter=200,
            tol=1e-4,
            random_state=random_state,
            cost=cost,
        )
        model.fit(matrix)

        if model.H_ is None:
            raise RuntimeError("NMF model did not produce a topic-term matrix")

        topics = extract_topics(model.H_, feature_names, top_n=top_n_words)
        metrics = evaluate_topic_modeling(
            topics, tokenized_documents, top_n=top_n_words
        )
        results[k] = metrics
        logger.info(format_metrics(metrics, f"NMF (k={k})"))

    return results


def find_optimal_k_by_cv(
    results: dict[int, TopicModelMetrics],
) -> tuple[int, float]:
    """Find optimal k based on maximum C_V coherence."""
    k_cv = {k: metrics.cv for k, metrics in results.items()}
    optimal_k = max(k_cv, key=lambda k: k_cv[k])
    return optimal_k, k_cv[optimal_k]


def find_optimal_k_by_npmi(
    results: dict[int, TopicModelMetrics],
) -> tuple[int, float]:
    """Find optimal k based on maximum NPMI coherence."""
    k_npmi = {k: metrics.npmi for k, metrics in results.items()}
    optimal_k = max(k_npmi, key=lambda k: k_npmi[k])
    return optimal_k, k_npmi[optimal_k]


def find_optimal_k_by_umass(
    results: dict[int, TopicModelMetrics],
) -> tuple[int, float]:
    """Find optimal k based on maximum U_Mass coherence."""
    k_umass = {k: metrics.umass for k, metrics in results.items()}
    optimal_k = max(k_umass, key=lambda k: k_umass[k])
    return optimal_k, k_umass[optimal_k]


def print_results_table(results: dict[int, TopicModelMetrics]) -> None:
    """Print results as a formatted table."""
    print("\nResults Summary:")
    print("-" * 80)
    print(f"{'k':>3} {'C_V':>10} {'NPMI':>10} {'U_Mass':>12}")
    print("-" * 80)

    for k in sorted(results.keys()):
        metrics = results[k]
        print(f"{k:3d} {metrics.cv:10.4f} {metrics.npmi:10.4f} {metrics.umass:12.4f}")

    print("-" * 80)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s - %(levelname)s - %(message)s",
    )

    # Example: Generate synthetic documents
    np.random.seed(42)
    documents = [
        "machine learning models predict outcomes",
        "deep learning neural networks learn representations",
        "topic modeling coherence measures semantic relatedness",
        "document clustering groups similar texts",
        "neural networks improve text embeddings",
        "coherence metrics evaluate topic quality",
        "bayesian methods and probabilistic models",
        "tf idf and bag of words representations",
        "dimensionality reduction helps visualization",
        "latent topics emerge from corpora",
    ]

    k_values = [2, 3, 4, 5, 6, 7, 8]

    print("=" * 80)
    print("NMF TOPIC MODELING VALIDATION (TF-IDF)")
    print("=" * 80)
    nmf_results = validate_nmf_pipeline(
        documents,
        k_values,
        representation="tfidf",
        max_features=1000,
        min_df=1,
        top_n_words=10,
        cost="frobenius",
        random_state=42,
    )
    print_results_table(nmf_results)

    optimal_k_cv, cv_value = find_optimal_k_by_cv(nmf_results)
    optimal_k_npmi, npmi_value = find_optimal_k_by_npmi(nmf_results)
    optimal_k_umass, umass_value = find_optimal_k_by_umass(nmf_results)

    print(f"\nOptimal k by C_V:    {optimal_k_cv} (C_V={cv_value:.4f})")
    print(f"Optimal k by NPMI:   {optimal_k_npmi} (NPMI={npmi_value:.4f})")
    print(f"Optimal k by U_Mass: {optimal_k_umass} (U_Mass={umass_value:.4f})")

    print("\n" + "=" * 80)
    print("NMF TOPIC MODELING VALIDATION (BoW)")
    print("=" * 80)
    bow_results = validate_nmf_pipeline(
        documents,
        k_values,
        representation="bow",
        max_features=1000,
        min_df=1,
        top_n_words=10,
        cost="frobenius",
        random_state=42,
    )
    print_results_table(bow_results)
