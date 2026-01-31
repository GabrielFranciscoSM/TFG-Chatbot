"""K-Means clustering with K-Means++ initialization.

Algorithm from TFG Section 3.2.1.1:

Given X = {x_1, ..., x_n} ⊂ R^p, we minimize:

SSE(S, C) = Σ_{i=1}^{k} Σ_{x ∈ S_i} ||x - c_i||²

With monotonic convergence guaranteed by:
- Proposition 3.2: SSE sequence is non-increasing
- Proposition 3.3: Finite number of partitions
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class KMeans:
    """K-Means clustering with K-Means++ initialization."""

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
