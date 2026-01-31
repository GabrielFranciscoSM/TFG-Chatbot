#!/usr/bin/env python3
"""
FAQ Clustering with K-Means and Fuzzy C-Means.

This script implements clustering algorithms from scratch for academic demonstration,
following the mathematical theory from Chapter 3 of the TFG document.

Algorithms implemented:
- K-Means with K-Means++ initialization (Section 3.2.1.1)
- Fuzzy C-Means (FCM) with fuzziness parameter m (Section 3.2.2)

Metrics:
- SSE (Sum of Squared Errors)
- Silhouette Score
- Elbow Method for optimal k selection
"""

import argparse
import json
import logging
import re
import string
from collections import Counter
from pathlib import Path
from typing import cast

import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Common English stopwords (same as topic_modeling.py)
STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "as",
    "is",
    "was",
    "are",
    "were",
    "been",
    "be",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "i",
    "you",
    "he",
    "she",
    "we",
    "they",
    "what",
    "which",
    "who",
    "whom",
    "where",
    "when",
    "why",
    "how",
    "all",
    "each",
    "every",
    "both",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "not",
    "only",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "also",
    "into",
    "over",
    "after",
    "before",
    "between",
    "through",
    "during",
    "above",
    "below",
    "up",
    "down",
    "out",
    "off",
    "about",
    "against",
    "further",
    "then",
    "once",
    "here",
    "there",
    "any",
    "own",
    "being",
    "their",
    "them",
}


# =============================================================================
# Vectorizers: TF-IDF and Bag of Words
# =============================================================================


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

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize and normalize text."""
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        tokens = re.findall(r"\b[a-z]{2,}\b", text)
        tokens = [t for t in tokens if t not in STOPWORDS]
        return tokens

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
        tokenized_docs = [self._tokenize(doc) for doc in documents]
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


class TFIDFVectorizer:
    """Manual TF-IDF implementation for academic demonstration.

    TF-IDF = Term Frequency × Inverse Document Frequency

    TF(t,d) = count(t,d) / len(d)
    IDF(t) = log(N / (1 + df(t)))
    """

    def __init__(self, max_features: int = 1000, min_df: int = 2):
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_: dict[str, int] = {}
        self.idf_: np.ndarray | None = None
        self.feature_names_: list[str] = []

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        tokens = re.findall(r"\b[a-z]{2,}\b", text)
        tokens = [t for t in tokens if t not in STOPWORDS]
        return tokens

    def _build_vocabulary(self, tokenized_docs: list[list[str]]) -> None:
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
        tokenized_docs = [self._tokenize(doc) for doc in documents]
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
        return self.feature_names_


class OllamaEmbeddings:
    """Embeddings using Ollama API with nomic-embed-text model.

    This provides dense semantic embeddings (768 dimensions) as an alternative
    to sparse TF-IDF/BoW representations.

    Requires Ollama running locally with nomic-embed-text model.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11435",
        batch_size: int = 10,
    ):
        """Initialize Ollama embeddings.

        Args:
            model: Ollama embedding model name
            base_url: Ollama API base URL
            batch_size: Number of documents to process per batch
        """
        self.model = model
        self.base_url = base_url
        self.batch_size = batch_size
        self.embedding_dim = 768  # nomic-embed-text dimension

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text using Ollama API."""
        import urllib.error
        import urllib.request

        url = f"{self.base_url}/api/embeddings"
        payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return np.array(result["embedding"])
        except urllib.error.URLError as e:
            logger.error(f"Failed to get embedding: {e}")
            raise

    def fit_transform(self, documents: list[str]) -> np.ndarray:
        """Transform documents to embedding matrix.

        Returns:
            Embedding matrix of shape (n_docs, 768), L2 normalized
        """
        n_docs = len(documents)
        embeddings = np.zeros((n_docs, self.embedding_dim))

        logger.info(
            f"Generating embeddings for {n_docs} documents with {self.model}..."
        )

        for i, doc in enumerate(documents):
            if (i + 1) % 50 == 0:
                logger.info(f"  Processed {i + 1}/{n_docs} documents")

            try:
                embeddings[i] = self._get_embedding(doc)
            except Exception as e:
                logger.warning(f"Failed to get embedding for doc {i}: {e}")
                # Use zero vector as fallback
                embeddings[i] = np.zeros(self.embedding_dim)

        # L2 normalize for clustering
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        embeddings = embeddings / norms

        logger.info(f"Embeddings matrix shape: {embeddings.shape}")
        return embeddings


# =============================================================================
# K-Means Clustering (TFG Section 3.2.1.1)
# =============================================================================


class KMeans:
    """K-Means clustering with K-Means++ initialization.

    Algorithm from TFG Section 3.2.1.1:

    Given X = {x_1, ..., x_n} ⊂ R^p, we minimize:

    SSE(S, C) = Σ_{i=1}^{k} Σ_{x ∈ S_i} ||x - c_i||²

    With monotonic convergence guaranteed by:
    - Proposition 3.2: SSE sequence is non-increasing
    - Proposition 3.3: Finite number of partitions
    """

    def __init__(
        self,
        n_clusters: int = 5,
        max_iter: int = 300,
        tol: float = 1e-4,
        random_state: int | None = None,
        init: str = "kmeans++",
    ):
        """Initialize K-Means.

        Args:
            n_clusters: Number of clusters (k)
            max_iter: Maximum iterations
            tol: Tolerance for convergence (based on SSE change)
            random_state: Random seed for reproducibility
            init: Initialization method ('kmeans++' or 'random')
        """
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.init = init

        self.centroids_: np.ndarray | None = None
        self.labels_: np.ndarray | None = None
        self.inertia_: float = 0.0  # Final SSE
        self.sse_history_: list[float] = []
        self.n_iter_: int = 0

    def _kmeans_plus_plus_init(self, X: np.ndarray) -> np.ndarray:
        """K-Means++ initialization: choose initial centroids with probability
        proportional to squared distance from nearest existing centroid.

        Reference: Arthur & Vassilvitskii (2007)
        """
        n_samples, n_features = X.shape
        centroids = np.zeros((self.n_clusters, n_features))

        # Choose first centroid uniformly at random
        rng = np.random.default_rng(self.random_state)
        first_idx = rng.integers(0, n_samples)
        centroids[0] = X[first_idx]

        # Choose remaining centroids
        for c in range(1, self.n_clusters):
            # Compute squared distances to nearest centroid
            distances = np.zeros(n_samples)
            for i in range(n_samples):
                min_dist = float("inf")
                for j in range(c):
                    dist = np.sum((X[i] - centroids[j]) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                distances[i] = min_dist

            # Choose next centroid with probability proportional to D(x)²
            prob_sum = distances.sum()
            if prob_sum == 0:
                # If all points are equally distant (or 0), choose randomly
                probabilities = np.ones(n_samples) / n_samples
            else:
                probabilities = distances / prob_sum

            next_idx = rng.choice(n_samples, p=probabilities)
            centroids[c] = X[next_idx]

        return centroids

    def _random_init(self, X: np.ndarray) -> np.ndarray:
        """Random initialization: choose k random samples as initial centroids."""
        rng = np.random.default_rng(self.random_state)
        indices = rng.choice(X.shape[0], size=self.n_clusters, replace=False)
        return X[indices].copy()

    def _assign_clusters(self, X: np.ndarray) -> np.ndarray:
        """Assignment step: assign each point to nearest centroid.

        S_i = {x ∈ X | ||x - c_i|| ≤ ||x - c_j|| ∀j ≠ i}
        """
        n_samples = X.shape[0]
        labels = np.zeros(n_samples, dtype=int)

        for i in range(n_samples):
            # Distance from x_i to all centroids
            assert self.centroids_ is not None
            dist = np.sum((X[i] - self.centroids_) ** 2, axis=1)
            labels[i] = np.argmin(dist)
        return labels

    def _update_centroids(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """Update step: recalculate centroids as mean of assigned points.

        c_i = (1/|S_i|) Σ_{x ∈ S_i} x
        """
        new_centroids = np.zeros_like(self.centroids_)

        for j in range(self.n_clusters):
            cluster_points = X[labels == j]
            if len(cluster_points) > 0:
                new_centroids[j] = cluster_points.mean(axis=0)
            else:
                # Empty cluster: reinitialize with random point
                new_centroids[j] = X[np.random.randint(0, X.shape[0])]

        return new_centroids

    def _compute_sse(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Compute Sum of Squared Errors (SSE).

        SSE(S, C) = Σ_{i=1}^{k} Σ_{x ∈ S_i} ||x - c_i||²
        """
        sse = 0.0
        for j in range(self.n_clusters):
            cluster_points = X[labels == j]
            if len(cluster_points) > 0:
                assert self.centroids_ is not None
                sse += np.sum((cluster_points - self.centroids_[j]) ** 2)
        return sse

    def fit(self, X: np.ndarray) -> "KMeans":
        """Fit K-Means to data.

        Args:
            X: Data matrix (n_samples, n_features)

        Returns:
            self
        """
        logger.info(f"Fitting K-Means with k={self.n_clusters}, init={self.init}")

        # Initialize centroids
        if self.init == "kmeans++":
            self.centroids_ = self._kmeans_plus_plus_init(X)
        else:
            self.centroids_ = self._random_init(X)

        self.sse_history_ = []
        prev_sse = float("inf")

        for iteration in range(self.max_iter):
            # Assignment step
            self.labels_ = self._assign_clusters(X)

            # Update step
            self.centroids_ = self._update_centroids(X, self.labels_)

            # Compute SSE
            sse = self._compute_sse(X, self.labels_)
            self.sse_history_.append(sse)

            # Check convergence (Proposition 3.2: SSE is monotonically non-increasing)
            if abs(prev_sse - sse) < self.tol:
                logger.info(f"K-Means converged at iteration {iteration + 1}")
                break

            prev_sse = sse
            self.n_iter_ = iteration + 1

        self.inertia_ = self.sse_history_[-1]
        logger.info(
            f"K-Means finished: SSE={self.inertia_:.4f}, iterations={self.n_iter_}"
        )

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict cluster labels for new data."""
        assert self.centroids_ is not None
        return self._assign_clusters(X)

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit and return cluster labels."""
        self.fit(X)
        assert self.labels_ is not None
        return self.labels_


# =============================================================================
# Fuzzy C-Means Clustering (TFG Section 3.2.2)
# =============================================================================


class FuzzyCMeans:
    """Fuzzy C-Means (FCM) clustering with fuzziness parameter m.

    Algorithm from TFG Section 3.2.2:

    Minimizes the generalized least squares functional:

    J_m(U, C) = Σ_{i=1}^{N} Σ_{j=1}^{k} (μ_ji)^m ||x_i - c_j||²

    Update rules:
    - Proposition 3.15: Membership update
      μ_ri = 1 / Σ_{j=1}^{k} (d(x_i, c_r) / d(x_i, c_j))^(2/(m-1))

    - Proposition 3.17: Centroid update
      c_r = Σ_{i=1}^{N} (μ_ri)^m x_i / Σ_{i=1}^{N} (μ_ri)^m
    """

    def __init__(
        self,
        n_clusters: int = 5,
        m: float = 2.0,
        max_iter: int = 300,
        tol: float = 1e-4,
        random_state: int | None = None,
    ):
        """Initialize FCM.

        Args:
            n_clusters: Number of clusters (k)
            m: Fuzziness parameter (m > 1). Higher m = fuzzier clusters.
               When m → 1: reduces to hard clustering (K-Means)
               When m → ∞: all memberships → 1/k
            max_iter: Maximum iterations
            tol: Tolerance for convergence (based on J_m change)
            random_state: Random seed for reproducibility
        """
        if m <= 1:
            raise ValueError("Fuzziness parameter m must be > 1")

        self.n_clusters = n_clusters
        self.m = m
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state

        self.centroids_: np.ndarray | None = None
        self.membership_: np.ndarray | None = None  # U matrix (k x N)
        self.labels_: np.ndarray | None = None  # Hard labels (argmax of membership)
        self.jm_: float = 0.0  # Final J_m value
        self.jm_history_: list[float] = []
        self.n_iter_: int = 0

    def _init_membership(self, n_samples: int) -> np.ndarray:
        """Initialize membership matrix U randomly.

        Constraint: Σ_j μ_ji = 1 for all i (Definition 3.11, condition C1)
        """
        rng = np.random.default_rng(self.random_state)
        U = rng.random((self.n_clusters, n_samples))
        # Normalize columns to sum to 1
        U = U / U.sum(axis=0, keepdims=True)
        return U

    def _update_centroids(self, X: np.ndarray, U: np.ndarray) -> np.ndarray:
        """Update centroids using Proposition 3.17.

        c_r = Σ_{i=1}^{N} (μ_ri)^m x_i / Σ_{i=1}^{N} (μ_ri)^m
        """
        Um = U**self.m  # Shape: (k, N)
        numerator = Um @ X  # Shape: (k, n_features)
        denominator = Um.sum(axis=1, keepdims=True)  # Shape: (k, 1)
        return numerator / (denominator + 1e-10)

    def _update_membership(self, X: np.ndarray, centroids: np.ndarray) -> np.ndarray:
        """Update membership matrix using Proposition 3.15.

        μ_ri = 1 / Σ_{j=1}^{k} (d(x_i, c_r) / d(x_i, c_j))^(2/(m-1))
        """
        n_samples = X.shape[0]
        exponent = 2 / (self.m - 1)

        # Compute distances: shape (k, N)
        distances = np.zeros((self.n_clusters, n_samples))
        for j in range(self.n_clusters):
            diff = X - centroids[j]  # Broadcasting: (N, features)
            distances[j] = np.sqrt(np.sum(diff**2, axis=1))

        # Handle zero distances (point exactly at centroid)
        distances = np.maximum(distances, 1e-10)

        # Update membership using formula from Proposition 3.15
        U = np.zeros((self.n_clusters, n_samples))
        for r in range(self.n_clusters):
            denominator = np.zeros(n_samples)
            for j in range(self.n_clusters):
                denominator += (distances[r] / distances[j]) ** exponent
            U[r] = 1 / denominator

        return U

    def _compute_jm(self, X: np.ndarray, U: np.ndarray, centroids: np.ndarray) -> float:
        """Compute the generalized least squares functional J_m.

        J_m(U, C) = Σ_{i=1}^{N} Σ_{j=1}^{k} (μ_ji)^m ||x_i - c_j||²
        """
        jm = 0.0
        Um = U**self.m

        for j in range(self.n_clusters):
            diff = X - centroids[j]
            distances_sq = np.sum(diff**2, axis=1)
            jm += np.sum(Um[j] * distances_sq)

        return jm

    def fit(self, X: np.ndarray) -> "FuzzyCMeans":
        """Fit FCM to data.

        Args:
            X: Data matrix (n_samples, n_features)

        Returns:
            self
        """
        n_samples = X.shape[0]
        logger.info(f"Fitting FCM with k={self.n_clusters}, m={self.m}")

        # Initialize membership matrix
        U = self._init_membership(n_samples)

        self.jm_history_ = []
        prev_jm = float("inf")

        for iteration in range(self.max_iter):
            # Update centroids (Proposition 3.17)
            centroids = self._update_centroids(X, U)

            # Update membership (Proposition 3.15)
            U = self._update_membership(X, centroids)

            # Compute J_m
            jm = self._compute_jm(X, U, centroids)
            self.jm_history_.append(jm)

            # Check convergence
            if abs(prev_jm - jm) < self.tol:
                logger.info(f"FCM converged at iteration {iteration + 1}")
                break

            prev_jm = jm
            self.n_iter_ = iteration + 1

        self.centroids_ = centroids
        self.membership_ = U
        self.labels_ = np.argmax(U, axis=0)  # Hard labels from max membership
        self.jm_ = self.jm_history_[-1]

        logger.info(f"FCM finished: J_m={self.jm_:.4f}, iterations={self.n_iter_}")

        return self

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Predict membership and labels for new data.

        Returns:
            Tuple of (membership_matrix, hard_labels)
        """
        assert self.centroids_ is not None
        U = self._update_membership(X, self.centroids_)
        labels = np.argmax(U, axis=0)
        return U, labels

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit and return hard cluster labels."""
        self.fit(X)
        assert self.labels_ is not None
        return self.labels_


# =============================================================================
# Metrics
# =============================================================================


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
    # Average the scores
    return float(np.mean(silhouette_vals))


def elbow_method(X: np.ndarray, k_range: range, random_state: int = 42) -> dict:
    """Run Elbow Method to find optimal number of clusters.

    Args:
        X: Data matrix
        k_range: Range of k values to test
        random_state: Random seed

    Returns:
        Dictionary with k, sse, and silhouette scores
    """
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


# =============================================================================
# Visualization
# =============================================================================


def plot_elbow(results: dict, output_path: str) -> None:
    """Plot Elbow Method results."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # SSE plot
    ax1.plot(results["k"], results["sse"], "bo-", linewidth=2, markersize=8)
    ax1.set_xlabel("Number of clusters (k)", fontsize=12)
    ax1.set_ylabel("SSE (Sum of Squared Errors)", fontsize=12)
    ax1.set_title("Elbow Method - SSE", fontsize=14)
    ax1.grid(True, alpha=0.3)

    # Silhouette plot
    ax2.plot(results["k"], results["silhouette"], "ro-", linewidth=2, markersize=8)
    ax2.set_xlabel("Number of clusters (k)", fontsize=12)
    ax2.set_ylabel("Silhouette Score", fontsize=12)
    ax2.set_title("Silhouette Score vs k", fontsize=14)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Elbow plot saved to {output_path}")


def plot_fcm_membership_heatmap(
    membership: np.ndarray, output_path: str, sample_size: int = 50
) -> None:
    """Plot FCM membership heatmap."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return

    # Sample for better visualization
    n_samples = membership.shape[1]
    if n_samples > sample_size:
        indices = np.linspace(0, n_samples - 1, sample_size, dtype=int)
        membership_sample = membership[:, indices]
    else:
        membership_sample = membership

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(membership_sample, aspect="auto", cmap="YlOrRd")

    ax.set_xlabel("Documents (sampled)", fontsize=12)
    ax.set_ylabel("Cluster", fontsize=12)
    ax.set_title("FCM Membership Matrix (μ_ji)", fontsize=14)
    ax.set_yticks(range(membership.shape[0]))
    ax.set_yticklabels([f"Cluster {i}" for i in range(membership.shape[0])])

    plt.colorbar(im, ax=ax, label="Membership degree")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"FCM membership heatmap saved to {output_path}")


def plot_comparison(kmeans_results: dict, fcm_results: dict, output_path: str) -> None:
    """Plot comparison between K-Means and FCM."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Silhouette comparison
    methods = ["K-Means (TF-IDF)", "K-Means (BoW)"]
    silhouettes = [
        kmeans_results["tfidf"]["silhouette"],
        kmeans_results["bow"]["silhouette"],
    ]
    colors = ["#2ecc71", "#27ae60"]

    if "emb" in kmeans_results:
        methods.append("K-Means (Emb)")
        silhouettes.append(kmeans_results["emb"]["silhouette"])
        colors.append("#1e8449")

    methods.extend(["FCM (TF-IDF)", "FCM (BoW)"])
    silhouettes.extend(
        [
            fcm_results["tfidf"]["silhouette"],
            fcm_results["bow"]["silhouette"],
        ]
    )
    colors.extend(["#e74c3c", "#c0392b"])

    if "emb" in fcm_results:
        methods.append("FCM (Emb)")
        silhouettes.append(fcm_results["emb"]["silhouette"])
        colors.append("#922b21")

    axes[0].bar(methods, silhouettes, color=colors)
    axes[0].set_ylabel("Silhouette Score", fontsize=12)
    axes[0].set_title("Clustering Quality Comparison", fontsize=14)
    axes[0].tick_params(axis="x", rotation=45, labelsize=10)

    # Convergence comparison
    axes[1].plot(
        kmeans_results["tfidf"]["sse_history"],
        "g-",
        label="K-Means (TF-IDF)",
        linewidth=2,
    )
    axes[1].plot(
        kmeans_results["bow"]["sse_history"], "g--", label="K-Means (BoW)", linewidth=2
    )
    if "emb" in kmeans_results:
        axes[1].plot(
            kmeans_results["emb"]["sse_history"],
            "g:",
            label="K-Means (Emb)",
            linewidth=2,
        )

    axes[1].plot(
        fcm_results["tfidf"]["jm_history"], "r-", label="FCM (TF-IDF)", linewidth=2
    )
    axes[1].plot(
        fcm_results["bow"]["jm_history"], "r--", label="FCM (BoW)", linewidth=2
    )
    if "emb" in fcm_results:
        axes[1].plot(
            fcm_results["emb"]["jm_history"], "r:", label="FCM (Emb)", linewidth=2
        )

    axes[1].set_xlabel("Iteration", fontsize=12)
    axes[1].set_ylabel("Objective Function", fontsize=12)
    axes[1].set_title("Convergence Comparison", fontsize=14)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Comparison plot saved to {output_path}")


# =============================================================================
# Main
# =============================================================================


def load_dataset(path: str) -> tuple[list[str], list[str]]:
    """Load synthetic dataset."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    documents = [item["text"] for item in data]
    labels = [item.get("label", "Unknown") for item in data]
    return documents, labels


def main():
    parser = argparse.ArgumentParser(description="FAQ Clustering with K-Means and FCM")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/synthetic_dataset.json",
        help="Path to dataset JSON file",
    )
    parser.add_argument("--n-clusters", type=int, default=5, help="Number of clusters")
    parser.add_argument(
        "--fuzziness", type=float, default=2.0, help="FCM fuzziness parameter (m)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/clustering",
        help="Output directory for results",
    )
    parser.add_argument(
        "--elbow", action="store_true", help="Run Elbow Method to find optimal k"
    )
    parser.add_argument(
        "--k-range", type=str, default="2,10", help="Range for Elbow Method (min,max)"
    )
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for embeddings generation",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load dataset
    logger.info(f"Loading dataset from {args.dataset}")
    documents, true_labels = load_dataset(args.dataset)
    logger.info(
        f"Loaded {len(documents)} documents with {len(set(true_labels))} unique labels"
    )

    # Vectorize with TF-IDF and BoW
    logger.info("Vectorizing documents with TF-IDF...")
    tfidf_vectorizer = TFIDFVectorizer(max_features=500, min_df=2)
    X_tfidf = tfidf_vectorizer.fit_transform(documents)

    logger.info("Vectorizing documents with BoW...")
    bow_vectorizer = BoWVectorizer(max_features=500, min_df=2)
    X_bow = bow_vectorizer.fit_transform(documents)

    # Vectorize with Ollama Embeddings
    logger.info("Vectorizing documents with Ollama Embeddings...")
    X_emb = None
    try:
        ollama_vectorizer = OllamaEmbeddings(batch_size=args.batch_size)
        X_emb = ollama_vectorizer.fit_transform(documents)
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        logger.warning("Continuing without embeddings...")

    # Run Elbow Method if requested
    if args.elbow:
        k_min, k_max = map(int, args.k_range.split(","))
        k_range = range(k_min, k_max + 1)

        logger.info(f"Running Elbow Method for k in {list(k_range)}")
        elbow_results_tfidf = elbow_method(X_tfidf, k_range, args.random_state)
        elbow_results_bow = elbow_method(X_bow, k_range, args.random_state)
        plot_elbow(elbow_results_tfidf, str(output_dir / "elbow_tfidf.png"))
        plot_elbow(elbow_results_bow, str(output_dir / "elbow_bow.png"))

        optimal_k_tfidf = elbow_results_tfidf["k"][
            np.argmax(elbow_results_tfidf["silhouette"])
        ]
        optimal_k_bow = elbow_results_bow["k"][
            np.argmax(elbow_results_bow["silhouette"])
        ]
        logger.info(f"Optimal k (TF-IDF): {optimal_k_tfidf}")
        logger.info(f"Optimal k (BoW): {optimal_k_bow}")

        if X_emb is not None:
            elbow_results_emb = elbow_method(X_emb, k_range, args.random_state)
            plot_elbow(elbow_results_emb, str(output_dir / "elbow_embeddings.png"))
            optimal_k_emb = elbow_results_emb["k"][
                np.argmax(elbow_results_emb["silhouette"])
            ]
            logger.info(f"Optimal k (Embeddings): {optimal_k_emb}")

    # K-Means clustering
    logger.info(f"\n{'='*50}")
    logger.info("K-MEANS CLUSTERING")
    logger.info(f"{'='*50}")

    kmeans_tfidf = KMeans(n_clusters=args.n_clusters, random_state=args.random_state)
    kmeans_tfidf.fit(X_tfidf)

    kmeans_bow = KMeans(n_clusters=args.n_clusters, random_state=args.random_state)
    kmeans_bow.fit(X_bow)

    kmeans_emb = None
    if X_emb is not None:
        kmeans_emb = KMeans(n_clusters=args.n_clusters, random_state=args.random_state)
        kmeans_emb.fit(X_emb)

    kmeans_results = {
        "tfidf": {
            "sse": kmeans_tfidf.inertia_,
            "sse_history": kmeans_tfidf.sse_history_,
        },
        "bow": {"sse": kmeans_bow.inertia_, "sse_history": kmeans_bow.sse_history_},
    }
    logger.info("Evaluating K-Means performance...")
    assert kmeans_tfidf.labels_ is not None
    kmeans_results["tfidf"]["silhouette"] = silhouette_score(
        X_tfidf, kmeans_tfidf.labels_
    )

    assert kmeans_bow.labels_ is not None
    kmeans_results["bow"]["silhouette"] = silhouette_score(X_bow, kmeans_bow.labels_)

    if X_emb is not None:
        assert kmeans_emb is not None and kmeans_emb.labels_ is not None
        kmeans_results["emb"] = {
            "sse": kmeans_emb.inertia_,
            "sse_history": kmeans_emb.sse_history_,
            "silhouette": silhouette_score(X_emb, kmeans_emb.labels_),
        }

    logger.info(
        f"K-Means TF-IDF: SSE={kmeans_tfidf.inertia_:.4f}, Silhouette={kmeans_results['tfidf']['silhouette']:.4f}"
    )
    logger.info(
        f"K-Means BoW: SSE={kmeans_bow.inertia_:.4f}, Silhouette={kmeans_results['bow']['silhouette']:.4f}"
    )
    if X_emb is not None and kmeans_emb is not None:
        logger.info(
            f"K-Means Emb: SSE={kmeans_emb.inertia_:.4f}, Silhouette={kmeans_results['emb']['silhouette']:.4f}"
        )

    # FCM clustering
    logger.info(f"\n{'='*50}")
    logger.info("FUZZY C-MEANS CLUSTERING")
    logger.info(f"{'='*50}")

    fcm_tfidf = FuzzyCMeans(
        n_clusters=args.n_clusters, m=args.fuzziness, random_state=args.random_state
    )
    fcm_tfidf.fit(X_tfidf)

    fcm_bow = FuzzyCMeans(
        n_clusters=args.n_clusters, m=args.fuzziness, random_state=args.random_state
    )
    fcm_bow.fit(X_bow)

    fcm_emb = None
    if X_emb is not None:
        fcm_emb = FuzzyCMeans(
            n_clusters=args.n_clusters, m=args.fuzziness, random_state=args.random_state
        )
        fcm_emb.fit(X_emb)

    fcm_results = {
        "tfidf": {"jm": fcm_tfidf.jm_, "jm_history": fcm_tfidf.jm_history_},
        "bow": {"jm": fcm_bow.jm_, "jm_history": fcm_bow.jm_history_},
    }
    logger.info("Evaluating FCM performance...")
    assert fcm_tfidf.labels_ is not None
    fcm_results["tfidf"]["silhouette"] = silhouette_score(X_tfidf, fcm_tfidf.labels_)

    assert fcm_bow.labels_ is not None
    fcm_results["bow"]["silhouette"] = silhouette_score(X_bow, fcm_bow.labels_)

    if X_emb is not None:
        assert fcm_emb is not None and fcm_emb.labels_ is not None
        fcm_results["emb"] = {
            "jm": fcm_emb.jm_,
            "jm_history": fcm_emb.jm_history_,
            "silhouette": silhouette_score(X_emb, fcm_emb.labels_),
        }

    logger.info(
        f"FCM TF-IDF (m={args.fuzziness}): J_m={fcm_tfidf.jm_:.4f}, Silhouette={fcm_results['tfidf']['silhouette']:.4f}"
    )
    logger.info(
        f"FCM BoW (m={args.fuzziness}): J_m={fcm_bow.jm_:.4f}, Silhouette={fcm_results['bow']['silhouette']:.4f}"
    )
    if X_emb is not None and fcm_emb is not None:
        logger.info(
            f"FCM Emb (m={args.fuzziness}): J_m={fcm_emb.jm_:.4f}, Silhouette={fcm_results['emb']['silhouette']:.4f}"
        )

    # Plot FCM membership heatmaps
    if fcm_tfidf.membership_ is not None:
        plot_fcm_membership_heatmap(
            fcm_tfidf.membership_, str(output_dir / "fcm_membership_tfidf.png")
        )
    if fcm_bow.membership_ is not None:
        plot_fcm_membership_heatmap(
            fcm_bow.membership_, str(output_dir / "fcm_membership_bow.png")
        )

    if X_emb is not None:
        if fcm_emb is not None and fcm_emb.membership_ is not None:
            plot_fcm_membership_heatmap(
                fcm_emb.membership_, str(output_dir / "fcm_membership_embeddings.png")
            )

    # Comparison plot

    plot_comparison(kmeans_results, fcm_results, str(output_dir / "comparison.png"))

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("SUMMARY")
    logger.info(f"{'='*50}")

    results_summary = {
        "dataset": args.dataset,
        "n_documents": len(documents),
        "n_clusters": args.n_clusters,
        "fuzziness_m": args.fuzziness,
        "results": {
            "kmeans_tfidf": {
                "sse": kmeans_results["tfidf"]["sse"],
                "silhouette": kmeans_results["tfidf"]["silhouette"],
            },
            "kmeans_bow": {
                "sse": kmeans_results["bow"]["sse"],
                "silhouette": kmeans_results["bow"]["silhouette"],
            },
            "fcm_tfidf": {
                "jm": fcm_results["tfidf"]["jm"],
                "silhouette": fcm_results["tfidf"]["silhouette"],
            },
            "fcm_bow": {
                "jm": fcm_results["bow"]["jm"],
                "silhouette": fcm_results["bow"]["silhouette"],
            },
        },
    }
    if X_emb is not None and "emb" in kmeans_results and "emb" in fcm_results:
        results_summary["results"]["kmeans_emb"] = {
            "sse": kmeans_results["emb"]["sse"],
            "silhouette": kmeans_results["emb"]["silhouette"],
        }
        results_summary["results"]["fcm_emb"] = {
            "jm": fcm_results["emb"]["jm"],
            "silhouette": fcm_results["emb"]["silhouette"],
        }

    # Save results
    results_path = output_dir / "results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)
    logger.info(f"Results saved to {results_path}")

    # Print comparison table
    print("\n" + "=" * 60)
    print("CLUSTERING COMPARISON RESULTS")
    print("=" * 60)
    print(f"{'Method':<20} {'Representation':<15} {'Silhouette':<12}")
    print("-" * 60)
    print(
        f"{'K-Means':<20} {'TF-IDF':<15} {kmeans_results['tfidf']['silhouette']:<12.4f}"
    )
    print(f"{'K-Means':<20} {'BoW':<15} {kmeans_results['bow']['silhouette']:<12.4f}")
    if "emb" in kmeans_results:
        print(
            f"{'K-Means':<20} {'Embeddings':<15} {kmeans_results['emb']['silhouette']:<12.4f}"
        )
    print(
        f"{'FCM (m=2)':<20} {'TF-IDF':<15} {fcm_results['tfidf']['silhouette']:<12.4f}"
    )
    print(f"{'FCM (m=2)':<20} {'BoW':<15} {fcm_results['bow']['silhouette']:<12.4f}")
    if "emb" in fcm_results:
        print(
            f"{'FCM (m=2)':<20} {'Embeddings':<15} {fcm_results['emb']['silhouette']:<12.4f}"
        )
    print("=" * 60)

    # Find best method
    all_methods: list[tuple[str, float]] = [
        ("K-Means TF-IDF", cast(float, kmeans_results["tfidf"]["silhouette"])),
        ("K-Means BoW", cast(float, kmeans_results["bow"]["silhouette"])),
        ("FCM TF-IDF", cast(float, fcm_results["tfidf"]["silhouette"])),
        ("FCM BoW", cast(float, fcm_results["bow"]["silhouette"])),
    ]
    if "emb" in kmeans_results and "emb" in fcm_results:
        all_methods.extend(
            [
                ("K-Means Emb", cast(float, kmeans_results["emb"]["silhouette"])),
                ("FCM Emb", cast(float, fcm_results["emb"]["silhouette"])),
            ]
        )

    best_method = max(all_methods, key=lambda x: x[1])
    print(f"\nBest method: {best_method[0]} (Silhouette: {best_method[1]:.4f})")


if __name__ == "__main__":
    main()
