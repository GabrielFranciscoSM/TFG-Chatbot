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
        Optimized to compute distances incrementally rather than recomputing all.
        """
        n_samples, n_features = X.shape
        centroids = np.zeros((self.n_clusters, n_features))

        # Choose first centroid uniformly at random
        rng = np.random.default_rng(self.random_state)
        first_idx = rng.integers(0, n_samples)
        centroids[0] = X[first_idx]

        # Track minimum squared distance to any existing centroid for each point
        min_distances = np.full(n_samples, np.inf)

        # Choose remaining centroids
        for c in range(1, self.n_clusters):
            # Only compute distances to the newly added centroid
            new_centroid = centroids[c - 1]
            # More efficient: avoid intermediate diff array
            distances_to_new = np.sum((X - new_centroid) ** 2, axis=1)

            # Update minimum distances
            min_distances = np.minimum(min_distances, distances_to_new)

            # Choose next centroid with probability proportional to D(x)²
            prob_sum = min_distances.sum()
            if prob_sum == 0:
                # If all points are equally distant (or 0), choose randomly
                probabilities = np.ones(n_samples) / n_samples
            else:
                probabilities = min_distances / prob_sum

            next_idx = rng.choice(n_samples, p=probabilities)
            centroids[c] = X[next_idx]

        return centroids

    def _random_init(self, X: np.ndarray) -> np.ndarray:
        """Random initialization: choose k random samples as initial centroids."""
        rng = np.random.default_rng(self.random_state)
        indices = rng.choice(X.shape[0], size=self.n_clusters, replace=False)
        return X[indices].copy()

    def _assign_clusters(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Assignment step: assign each point to nearest centroid.

        S_i = {x ∈ X | ||x - c_i|| ≤ ||x - c_j|| ∀j ≠ i}

        Uses distance expansion: ||x-c||² = ||x||² + ||c||² - 2⟨x,c⟩
        This avoids creating large intermediate arrays and uses optimized BLAS.

        Returns:
            labels: Cluster assignment for each point
            distances: Distance matrix (n_samples, n_clusters) for reuse
        """
        assert self.centroids_ is not None
        # Compute ||x||² for each sample (n_samples,)
        x_squared = np.sum(X**2, axis=1, keepdims=True)
        # Compute ||c||² for each centroid (n_clusters,)
        c_squared = np.sum(self.centroids_**2, axis=1)
        # Compute -2⟨x,c⟩ using matrix multiplication (n_samples, n_clusters)
        cross_term = -2 * np.dot(X, self.centroids_.T)
        # Combine: ||x-c||² = ||x||² + ||c||² - 2⟨x,c⟩
        distances = x_squared + c_squared + cross_term
        # Get index of nearest centroid for each sample
        labels = np.argmin(distances, axis=1)
        return labels, distances

    def _update_centroids(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """Update step: recalculate centroids as mean of assigned points.

        c_i = (1/|S_i|) Σ_{x ∈ S_i} x

        Fully vectorized using np.add.at for optimal performance.
        """
        n_samples, n_features = X.shape
        new_centroids = np.zeros((self.n_clusters, n_features))

        # Count points per cluster
        counts = np.bincount(labels, minlength=self.n_clusters)

        # Sum all points for each cluster (vectorized accumulation)
        np.add.at(new_centroids, labels, X)

        # Divide by counts to get means (handle empty clusters)
        empty_clusters = counts == 0
        counts[empty_clusters] = 1  # Avoid division by zero
        new_centroids /= counts[:, np.newaxis]

        # Reinitialize empty clusters with random points
        if np.any(empty_clusters):
            rng = np.random.default_rng(self.random_state)
            for j in np.where(empty_clusters)[0]:
                new_centroids[j] = X[rng.integers(0, n_samples)]

        return new_centroids

    def _compute_sse(
        self, X: np.ndarray, labels: np.ndarray, distances: np.ndarray | None = None
    ) -> float:
        """Compute Sum of Squared Errors (SSE).

        SSE(S, C) = Σ_{i=1}^{k} Σ_{x ∈ S_i} ||x - c_i||²

        Args:
            X: Data matrix
            labels: Cluster assignments
            distances: Optional precomputed distance matrix from assignment step

        Fully vectorized for efficiency.
        """
        if distances is not None:
            # Use precomputed distances from assignment step
            return np.sum(distances[np.arange(len(labels)), labels])

        # Fallback: compute from scratch
        assert self.centroids_ is not None
        diffs = X - self.centroids_[labels]
        sse = np.sum(diffs**2)
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
            # Assignment step (returns labels and distances)
            self.labels_, distances = self._assign_clusters(X)

            # Update step
            self.centroids_ = self._update_centroids(X, self.labels_)

            # Compute SSE (reuse distances from assignment)
            sse = self._compute_sse(X, self.labels_, distances)
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
        labels, _ = self._assign_clusters(X)
        return labels

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit and return cluster labels."""
        self.fit(X)
        assert self.labels_ is not None
        return self.labels_
