"""Topic coherence metrics: UCI and UMass.

Manual implementation for academic demonstration.
"""

import logging
from collections import Counter

import numpy as np

from math_investigation.nlp.stopwords import STOPWORDS

logger = logging.getLogger(__name__)


def uci_coherence(
    topics: dict[int, list[str]],
    documents: list[str],
    window_size: int = 10,
) -> dict[int, float]:
    """Compute UCI coherence using sliding window co-occurrence.

    C_UCI = (2 / (n*(n-1))) * Σ log((P(w_i, w_j) + ε) / (P(w_i) * P(w_j)))

    Args:
        topics: Dictionary of topic_idx -> top words
        documents: Original documents for co-occurrence
        window_size: Sliding window size

    Returns:
        Dictionary of topic_idx -> coherence score
    """
    import re
    import string

    def tokenize(text: str) -> list[str]:
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        tokens = re.findall(r"\b[a-z]{2,}\b", text)
        return [t for t in tokens if t not in STOPWORDS]

    # Build vocabulary from topics
    vocab = set()
    for words in topics.values():
        vocab.update(words)

    # Build co-occurrence counts from sliding windows
    word_counts: Counter = Counter()
    pair_counts: Counter = Counter()
    total_windows = 0

    for doc in documents:
        tokens = tokenize(doc)
        # Sliding window
        for i in range(len(tokens) - window_size + 1):
            window = tokens[i : i + window_size]
            unique_words = set(window) & vocab

            for word in unique_words:
                word_counts[word] += 1

            for w1 in unique_words:
                for w2 in unique_words:
                    if w1 < w2:  # Avoid duplicates
                        pair_counts[(w1, w2)] += 1

            total_windows += 1

    if total_windows == 0:
        return dict.fromkeys(topics, 0.0)

    # Compute coherence for each topic
    coherence_scores = {}
    eps = 1e-10

    for topic_idx, words in topics.items():
        words_in_vocab = [w for w in words if w in vocab]
        n = len(words_in_vocab)

        if n < 2:
            coherence_scores[topic_idx] = 0.0
            continue

        pmi_sum = 0.0
        pairs = 0

        for i, w1 in enumerate(words_in_vocab):
            for w2 in words_in_vocab[i + 1 :]:
                p_w1 = word_counts[w1] / total_windows
                p_w2 = word_counts[w2] / total_windows

                pair_key = tuple(sorted([w1, w2]))
                p_w1w2 = pair_counts[pair_key] / total_windows

                # Pointwise mutual information
                pmi = np.log((p_w1w2 + eps) / (p_w1 * p_w2 + eps))
                pmi_sum += pmi
                pairs += 1

        coherence_scores[topic_idx] = pmi_sum / pairs if pairs > 0 else 0.0

    return coherence_scores


def umass_coherence(
    topics: dict[int, list[str]],
    doc_term_matrix: np.ndarray,
    feature_names: list[str],
) -> dict[int, float]:
    """Compute UMass coherence using document co-occurrence.

    C_UMass = (2 / (n*(n-1))) * Σ log((D(w_i, w_j) + 1) / D(w_i))

    Args:
        topics: Dictionary of topic_idx -> top words
        doc_term_matrix: Document-term matrix (binary presence)
        feature_names: Vocabulary terms in order

    Returns:
        Dictionary of topic_idx -> coherence score
    """
    vocab_to_idx = {w: i for i, w in enumerate(feature_names)}

    # Convert to binary presence
    binary_matrix = (doc_term_matrix > 0).astype(int)

    # Document frequency
    doc_freq = binary_matrix.sum(axis=0)

    coherence_scores = {}

    for topic_idx, words in topics.items():
        n = len(words)
        if n < 2:
            coherence_scores[topic_idx] = 0.0
            continue

        score_sum = 0.0
        pairs = 0

        for i, w1 in enumerate(words):
            if w1 not in vocab_to_idx:
                continue
            idx1 = vocab_to_idx[w1]

            for w2 in words[i + 1 :]:
                if w2 not in vocab_to_idx:
                    continue
                idx2 = vocab_to_idx[w2]

                # D(w2) - documents containing w2
                d_w2 = doc_freq[idx2]

                # D(w1, w2) - documents containing both
                d_w1_w2 = np.sum(binary_matrix[:, idx1] * binary_matrix[:, idx2])

                # UMass score
                score = np.log((d_w1_w2 + 1) / (d_w2 + 1e-10))
                score_sum += score
                pairs += 1

        coherence_scores[topic_idx] = score_sum / pairs if pairs > 0 else 0.0

    return coherence_scores
