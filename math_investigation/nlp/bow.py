"""Bag of Words (BoW) vectorizer implementation."""

import logging
from collections import Counter

import numpy as np

from math_investigation.nlp.utils import tokenize

logger = logging.getLogger(__name__)


class BoWVectorizer:
    """Manual Bag of Words implementation for academic demonstration.

    BoW(t,d) = count(t,d) / len(d)  (normalized)

    Unlike TF-IDF, BoW does not weight by document frequency.
    """

    def __init__(self, max_features: int = 1000, min_df: int = 2):
        """Initialize BoW vectorizer.

        Args:
            max_features: Maximum vocabulary size
            min_df: Minimum document frequency for a term
        """
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_: dict[str, int] = {}
        self.feature_names_: list[str] = []

    def _build_vocabulary(self, tokenized_docs: list[list[str]]) -> None:
        """Build vocabulary from tokenized documents."""
        df_counts: Counter = Counter()
        for doc in tokenized_docs:
            unique_terms = set(doc)
            df_counts.update(unique_terms)

        filtered_terms = [
            (term, count) for term, count in df_counts.items() if count >= self.min_df
        ]
        filtered_terms.sort(key=lambda x: x[1], reverse=True)
        top_terms = filtered_terms[: self.max_features]

        self.vocabulary_ = {term: idx for idx, (term, _) in enumerate(top_terms)}
        self.feature_names_ = [term for term, _ in top_terms]
        logger.info(f"BoW Vocabulary size: {len(self.vocabulary_)}")

    def fit_transform(self, documents: list[str]) -> np.ndarray:
        """Fit vocabulary and transform documents to BoW matrix.

        Returns:
            BoW matrix of shape (n_docs, n_features), L2 normalized
        """
        tokenized_docs = [tokenize(doc) for doc in documents]
        self._build_vocabulary(tokenized_docs)

        n_docs = len(documents)
        n_features = len(self.vocabulary_)
        bow_matrix = np.zeros((n_docs, n_features))

        for i, tokens in enumerate(tokenized_docs):
            if not tokens:
                continue
            token_counts = Counter(tokens)
            doc_len = len(tokens)
            for term, count in token_counts.items():
                if term in self.vocabulary_:
                    idx = self.vocabulary_[term]
                    bow_matrix[i, idx] = count / doc_len

        # L2 normalize for clustering
        norms = np.linalg.norm(bow_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        bow_matrix = bow_matrix / norms

        logger.info(f"BoW matrix shape: {bow_matrix.shape}")
        return bow_matrix

    def get_feature_names(self) -> list[str]:
        """Get feature names (vocabulary terms)."""
        return self.feature_names_
