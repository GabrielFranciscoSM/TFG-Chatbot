"""TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer implementation."""

import logging
from collections import Counter

import numpy as np

from math_investigation.nlp.utils import tokenize

logger = logging.getLogger(__name__)


class TFIDFVectorizer:
    """Manual TF-IDF implementation for academic demonstration.

    TF-IDF = Term Frequency × Inverse Document Frequency

    TF(t,d) = count(t,d) / len(d)
    IDF(t) = log(N / (1 + df(t)))
    """

    def __init__(self, max_features: int = 1000, min_df: int = 2):
        """Initialize TF-IDF vectorizer.

        Args:
            max_features: Maximum vocabulary size
            min_df: Minimum document frequency for a term
        """
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_: dict[str, int] = {}
        self.idf_: np.ndarray | None = None
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
        logger.info(f"TF-IDF Vocabulary size: {len(self.vocabulary_)}")

    def _compute_tf(self, tokens: list[str]) -> np.ndarray:
        """Compute Term Frequency for a document.

        TF(t,d) = count(t,d) / len(d)
        """
        tf = np.zeros(len(self.vocabulary_))
        if not tokens:
            return tf
        token_counts = Counter(tokens)
        doc_len = len(tokens)
        for term, count in token_counts.items():
            if term in self.vocabulary_:
                idx = self.vocabulary_[term]
                tf[idx] = count / doc_len
        return tf

    def _compute_idf(self, tokenized_docs: list[list[str]]) -> np.ndarray:
        """Compute Inverse Document Frequency.

        IDF(t) = log(N / (1 + df(t)))
        """
        n_docs = len(tokenized_docs)
        df = np.zeros(len(self.vocabulary_))
        for doc in tokenized_docs:
            unique_terms = set(doc)
            for term in unique_terms:
                if term in self.vocabulary_:
                    df[self.vocabulary_[term]] += 1
        idf = np.log(n_docs / (1 + df))
        return idf

    def fit_transform(self, documents: list[str]) -> np.ndarray:
        """Fit vocabulary and transform documents to TF-IDF matrix.

        Returns:
            TF-IDF matrix of shape (n_docs, n_features), L2 normalized
        """
        tokenized_docs = [tokenize(doc) for doc in documents]
        self._build_vocabulary(tokenized_docs)
        self.idf_ = self._compute_idf(tokenized_docs)

        n_docs = len(documents)
        n_features = len(self.vocabulary_)
        tfidf_matrix = np.zeros((n_docs, n_features))

        for i, tokens in enumerate(tokenized_docs):
            tf = self._compute_tf(tokens)
            tfidf_matrix[i] = tf * self.idf_

        # L2 normalize for clustering
        norms = np.linalg.norm(tfidf_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        tfidf_matrix = tfidf_matrix / norms

        logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
        return tfidf_matrix

    def get_feature_names(self) -> list[str]:
        """Get feature names (vocabulary terms)."""
        return self.feature_names_
