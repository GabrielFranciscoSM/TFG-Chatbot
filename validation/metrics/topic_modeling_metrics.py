"""Topic modeling validation metrics.

Implements:
- Coherence C_V - current SOTA, correlates well with human judgment
- Normalized Pointwise Mutual Information (NPMI) - complementary coherence metric
- U_Mass Coherence - intrinsic coherence metric based on the training corpus

This module avoids gensim and computes the metrics from tokenized texts using
sliding-window and document-level co-occurrence statistics.
"""

from __future__ import annotations

import logging
from collections import Counter
from itertools import combinations
from math import log
from typing import NamedTuple

import numpy as np

logger = logging.getLogger(__name__)


class TopicModelMetrics(NamedTuple):
    """Container for topic modeling validation metrics."""

    cv: float  # Coherence C_V
    npmi: float  # Normalized Pointwise Mutual Information coherence
    umass: float  # U_Mass coherence


def _normalize_topics(
    topics: list[list[str]],
    top_n: int | None = None,
) -> list[list[str]]:
    """Trim topics to the requested top-N words."""
    if top_n is None:
        return [list(topic) for topic in topics]
    return [list(topic[:top_n]) for topic in topics]


def _prepare_texts(texts: list[list[str]]) -> list[list[str]]:
    """Validate tokenized texts and normalize them to plain lists."""
    prepared_texts = [list(text) for text in texts]
    if not prepared_texts:
        raise ValueError("texts must contain at least one tokenized document")
    return prepared_texts


def _topic_pairs(words: list[str]) -> list[tuple[str, str]]:
    """Return all unique unordered word pairs for a topic."""
    return [(left, right) for left, right in combinations(words, 2)]


def _sliding_windows(text: list[str], window_size: int) -> list[list[str]]:
    """Generate overlapping sliding windows for a single document."""
    if window_size <= 0:
        raise ValueError("window_size must be greater than 0")

    if len(text) <= window_size:
        return [list(text)]

    return [
        list(text[index : index + window_size])
        for index in range(len(text) - window_size + 1)
    ]


def _build_window_statistics(
    texts: list[list[str]],
    window_size: int,
) -> tuple[int, Counter[str], Counter[tuple[str, str]]]:
    """Build sliding-window document frequencies for words and word pairs."""
    total_windows = 0
    word_window_counts: Counter[str] = Counter()
    pair_window_counts: Counter[tuple[str, str]] = Counter()

    for text in texts:
        for window in _sliding_windows(text, window_size):
            unique_words = sorted(set(window))
            if not unique_words:
                continue

            total_windows += 1
            word_window_counts.update(unique_words)
            pair_window_counts.update(combinations(unique_words, 2))

    return total_windows, word_window_counts, pair_window_counts


def _build_document_statistics(
    texts: list[list[str]],
) -> tuple[int, Counter[str], Counter[tuple[str, str]]]:
    """Build document frequencies for U_Mass coherence."""
    total_documents = 0
    word_document_counts: Counter[str] = Counter()
    pair_document_counts: Counter[tuple[str, str]] = Counter()

    for text in texts:
        unique_words = sorted(set(text))
        if not unique_words:
            continue

        total_documents += 1
        word_document_counts.update(unique_words)
        pair_document_counts.update(combinations(unique_words, 2))

    return total_documents, word_document_counts, pair_document_counts


def _safe_log_ratio(numerator: float, denominator: float, epsilon: float) -> float:
    """Compute a stable logarithmic ratio."""
    return log((numerator + epsilon) / (denominator + epsilon))


def _pair_npmi(
    word_left: str,
    word_right: str,
    total_windows: int,
    word_window_counts: Counter[str],
    pair_window_counts: Counter[tuple[str, str]],
    epsilon: float,
) -> float:
    """Compute NPMI for a pair of words from sliding-window statistics."""
    if total_windows == 0:
        return 0.0

    pair: tuple[str, str]
    if word_left <= word_right:
        pair = (word_left, word_right)
    else:
        pair = (word_right, word_left)
    pair_count = pair_window_counts.get(pair, 0)
    if pair_count == 0:
        return -1.0

    left_count = word_window_counts.get(word_left, 0)
    right_count = word_window_counts.get(word_right, 0)

    p_left = left_count / total_windows
    p_right = right_count / total_windows
    p_pair = pair_count / total_windows

    if p_left <= 0.0 or p_right <= 0.0 or p_pair <= 0.0:
        return -1.0

    pmi = log((p_pair + epsilon) / ((p_left * p_right) + epsilon))
    denom = -log(p_pair + epsilon)
    if denom == 0.0:
        return 0.0

    score = pmi / denom
    return float(np.clip(score, -1.0, 1.0))


def _cosine_similarity(vector_left: np.ndarray, vector_right: np.ndarray) -> float:
    """Compute cosine similarity with zero-vector protection."""
    left_norm = float(np.linalg.norm(vector_left))
    right_norm = float(np.linalg.norm(vector_right))

    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    similarity = float(np.dot(vector_left, vector_right) / (left_norm * right_norm))
    return float(np.clip(similarity, -1.0, 1.0))


def _topic_context_vectors(
    words: list[str],
    total_windows: int,
    word_window_counts: Counter[str],
    pair_window_counts: Counter[tuple[str, str]],
    epsilon: float,
) -> list[np.ndarray]:
    """Build NPMI-based context vectors for indirect confirmation."""
    vectors: list[np.ndarray] = []

    for word in words:
        row = [
            _pair_npmi(
                word,
                other_word,
                total_windows,
                word_window_counts,
                pair_window_counts,
                epsilon,
            )
            for other_word in words
            if other_word != word
        ]
        vectors.append(np.asarray(row, dtype=float))

    return vectors


def coherence_c_v(
    topics: list[list[str]],
    texts: list[list[str]],
    top_n: int | None = 10,
    window_size: int = 110,
    epsilon: float = 1e-12,
) -> float:
    """Calculate Coherence C_V for a topic model.

    Args:
        topics: Topics as lists of words.
        texts: Tokenized documents used to estimate sliding-window statistics.
        top_n: Number of top words per topic to keep.
        window_size: Sliding window size for co-occurrence counting.
        epsilon: Numerical stability constant.

    Returns:
        C_V coherence score in range [0, 1]; higher is better.
    """
    prepared_topics = _normalize_topics(topics, top_n=top_n)
    prepared_texts = _prepare_texts(texts)
    total_windows, word_window_counts, pair_window_counts = _build_window_statistics(
        prepared_texts,
        window_size=window_size,
    )

    topic_scores: list[float] = []
    for topic in prepared_topics:
        if len(topic) < 2:
            continue

        context_vectors = _topic_context_vectors(
            topic,
            total_windows,
            word_window_counts,
            pair_window_counts,
            epsilon,
        )

        pair_scores: list[float] = []
        for index_left in range(len(context_vectors)):
            for index_right in range(index_left + 1, len(context_vectors)):
                similarity = _cosine_similarity(
                    context_vectors[index_left], context_vectors[index_right]
                )
                pair_scores.append((similarity + 1.0) / 2.0)

        if pair_scores:
            topic_scores.append(float(np.mean(pair_scores)))

    score = float(np.mean(topic_scores)) if topic_scores else 0.0
    logger.debug(f"C_V: {score:.4f}")
    return score


def normalized_pointwise_mutual_information(
    topics: list[list[str]],
    texts: list[list[str]],
    top_n: int | None = 10,
    window_size: int = 110,
    epsilon: float = 1e-12,
) -> float:
    """Calculate topic coherence using normalized PMI.

    Args:
        topics: Topics as lists of words.
        texts: Tokenized documents used to estimate co-occurrence statistics.
        top_n: Number of top words per topic to keep.
        window_size: Sliding window size for co-occurrence counting.
        epsilon: Numerical stability constant.

    Returns:
        NPMI coherence score in range [-1, 1]; higher is better.
    """
    prepared_topics = _normalize_topics(topics, top_n=top_n)
    prepared_texts = _prepare_texts(texts)
    total_windows, word_window_counts, pair_window_counts = _build_window_statistics(
        prepared_texts,
        window_size=window_size,
    )

    pair_scores: list[float] = []
    for topic in prepared_topics:
        for word_left, word_right in _topic_pairs(topic):
            pair_scores.append(
                _pair_npmi(
                    word_left,
                    word_right,
                    total_windows,
                    word_window_counts,
                    pair_window_counts,
                    epsilon,
                )
            )

    score = float(np.mean(pair_scores)) if pair_scores else 0.0
    logger.debug(f"NPMI: {score:.4f}")
    return score


def u_mass_coherence(
    topics: list[list[str]],
    texts: list[list[str]],
    top_n: int | None = 10,
    epsilon: float = 1e-12,
) -> float:
    """Calculate U_Mass coherence for a topic model.

    Args:
        topics: Topics as lists of words.
        texts: Tokenized documents used to build the document co-occurrence counts.
        top_n: Number of top words per topic to keep.
        epsilon: Numerical stability constant.

    Returns:
        U_Mass coherence score in range (-∞, 0]; closer to 0 is better.
    """
    prepared_topics = _normalize_topics(topics, top_n=top_n)
    prepared_texts = _prepare_texts(texts)
    total_documents, word_document_counts, pair_document_counts = (
        _build_document_statistics(prepared_texts)
    )

    if total_documents == 0:
        return 0.0

    topic_scores: list[float] = []
    for topic in prepared_topics:
        if len(topic) < 2:
            continue

        pair_scores: list[float] = []
        for word_left, word_right in _topic_pairs(topic):
            left, right = sorted((word_left, word_right))
            pair_count = pair_document_counts.get((left, right), 0)
            right_count = word_document_counts.get(right, 0)

            score = _safe_log_ratio(pair_count, right_count, epsilon)
            pair_scores.append(score)

        if pair_scores:
            topic_scores.append(float(np.mean(pair_scores)))

    score = float(np.mean(topic_scores)) if topic_scores else 0.0
    logger.debug(f"U_Mass: {score:.4f}")
    return score


def evaluate_topic_modeling(
    topics: list[list[str]],
    texts: list[list[str]],
    top_n: int | None = 10,
    window_size: int = 110,
    epsilon: float = 1e-12,
) -> TopicModelMetrics:
    """Evaluate a topic model with the main coherence metrics.

    Args:
        topics: Topics as lists of words.
        texts: Tokenized documents used to estimate topic coherence.
        top_n: Number of top words per topic to keep.
        window_size: Sliding window size for co-occurrence counting.
        epsilon: Numerical stability constant.

    Returns:
        TopicModelMetrics with C_V, NPMI, and U_Mass.
    """
    cv = coherence_c_v(
        topics,
        texts,
        top_n=top_n,
        window_size=window_size,
        epsilon=epsilon,
    )
    npmi = normalized_pointwise_mutual_information(
        topics,
        texts,
        top_n=top_n,
        window_size=window_size,
        epsilon=epsilon,
    )
    umass = u_mass_coherence(
        topics,
        texts,
        top_n=top_n,
        epsilon=epsilon,
    )

    return TopicModelMetrics(cv=cv, npmi=npmi, umass=umass)


def format_metrics(metrics: TopicModelMetrics, name: str = "") -> str:
    """Format topic-modeling metrics for display.

    Args:
        metrics: TopicModelMetrics instance.
        name: Optional name for the result set.

    Returns:
        Formatted string representation.
    """
    lines = []
    if name:
        lines.append(f"Metrics for {name}:")

    lines.append(f"  C_V Coherence:        {metrics.cv:8.4f}")
    lines.append(f"  NPMI Coherence:       {metrics.npmi:8.4f}")
    lines.append(f"  U_Mass Coherence:     {metrics.umass:8.4f}")

    return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Toy corpus and topics for a runnable example.
    texts = [
        ["machine", "learning", "models", "predict"],
        ["deep", "learning", "neural", "networks"],
        ["topic", "modeling", "coherence", "words"],
        ["clustering", "documents", "topics", "embeddings"],
        ["neural", "networks", "representations", "learning"],
    ]

    topics = [
        ["learning", "neural", "models", "network", "predict"],
        ["topic", "modeling", "coherence", "words", "documents"],
    ]

    metrics = evaluate_topic_modeling(
        topics,
        texts,
        top_n=5,
    )
    print(format_metrics(metrics, "Topic Model"))
