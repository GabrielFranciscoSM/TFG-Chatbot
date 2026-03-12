"""Spherical K-Means clustering for text embeddings.

Uses Cosine Similarity (equivalent to Euclidean distance on L2-normalized vectors).
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class SphericalKMeans:
    """Spherical K-Means clustering with K-Means++ initialization.

    Optimized for high-dimensional L2-normalized text embeddings.
    Since ||x|| = ||c|| = 1, maximizing cosine similarity is equivalent
    to minimizing squared Euclidean distance.
    """

    def __init__(
        self,
        n_clusters: int = 5,
        max_iter: int = 300,
        tol: float = 1e-4,
        random_state: int | None = None,
    ):
        """Initialize Spherical K-Means.

        Args:
            n_clusters: Number of clusters (k)
            max_iter: Maximum iterations
            tol: Tolerance for convergence (based on centroid shift)
            random_state: Random seed for reproducibility
        """
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state

        self.centroids_: np.ndarray | None = None
        self.labels_: np.ndarray | None = None
        self.inertia_: float = 0.0  # Sum of squared distances to closest centroid
        self.n_iter_: int = 0

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        """L2 normalize vectors (handling zero vectors)."""
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1.0
        return v / norms

    def _kmeans_plus_plus_init(self, X: np.ndarray) -> np.ndarray:
        """Initialize centroids using k-means++ for spherical k-means."""
        n_samples, n_features = X.shape
        centroids = np.zeros((self.n_clusters, n_features))

        rng = np.random.default_rng(self.random_state)

        # 1. Choose first centroid uniformly at random
        first_idx = rng.integers(0, n_samples)
        centroids[0] = X[first_idx]

        # Distance squared from a point x to centroid c where ||x||=||c||=1
        # is given by ||x-c||^2 = 2 - 2*(x . c)
        min_sq_distances = np.full(n_samples, np.inf)

        for c in range(1, self.n_clusters):
            # Compute cosine similarities to the previously added centroid
            # X shape: (N, D), centroids[c-1] shape: (D,)
            cos_sims = np.dot(X, centroids[c - 1])

            # Convert cosine similarity to squared distance (for normalized vectors)
            # Clip to deal with floating point inaccuracies
            sq_distances = np.clip(2.0 - 2.0 * cos_sims, 0.0, None)

            # Update minimum distances
            min_sq_distances = np.minimum(min_sq_distances, sq_distances)

            # Choose next centroid with probability proportional to D(x)^2
            prob_sum = min_sq_distances.sum()
            if prob_sum > 0:
                probabilities = min_sq_distances / prob_sum
            else:
                probabilities = np.ones(n_samples) / n_samples

            next_idx = rng.choice(n_samples, p=probabilities)
            centroids[c] = X[next_idx]

        return centroids

    def _assign_clusters(self, X: np.ndarray) -> tuple[np.ndarray, float]:
        """Assign points to closest centroid and compute inertia.

        Returns:
            labels: Cluster assignments
            inertia: Sum of squared distances to closest centroids
        """
        assert self.centroids_ is not None

        # Cosine similarity matrix: (N, K)
        cos_sims = np.dot(X, self.centroids_.T)

        # Best matches
        labels = np.argmax(cos_sims, axis=1)
        max_sims = np.max(cos_sims, axis=1)

        # Inertia based on squared Euclidean distance: ||x-c||^2 = 2 - 2*(x.c)
        inertia = np.sum(np.clip(2.0 - 2.0 * max_sims, 0.0, None))

        return labels, inertia

    def _update_centroids(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """Update centroids to be the L2-normalized mean of assigned points."""
        n_samples, n_features = X.shape
        new_centroids = np.zeros((self.n_clusters, n_features))

        counts = np.bincount(labels, minlength=self.n_clusters)

        # Sum points in each cluster
        np.add.at(new_centroids, labels, X)

        # Note: We don't need to divide by count because we are going to L2-normalize anyway,
        # but we do need to handle empty clusters
        empty_clusters = counts == 0
        if np.any(empty_clusters):
            # Assign random points to empty clusters
            rng = np.random.default_rng(self.random_state)
            for j in np.where(empty_clusters)[0]:
                new_centroids[j] = X[rng.integers(0, n_samples)]

        # For spherical k-means, the centroid is the normalized mean
        return self._normalize(new_centroids)

    def fit(self, X: np.ndarray) -> "SphericalKMeans":
        """Compute spherical k-means clustering.

        Args:
            X: Data matrix (n_samples, n_features). Will be L2-normalized internally.

        Returns:
            self
        """
        logger.info(f"Fitting Spherical K-Means with k={self.n_clusters}")

        # Ensure input is L2 normalized
        X_norm = self._normalize(X.copy())

        n_samples = X_norm.shape[0]

        # If fewer samples than clusters, reduce k
        if n_samples < self.n_clusters:
            logger.warning(
                f"Number of samples ({n_samples}) < n_clusters ({self.n_clusters}). Reducing k."
            )
            self.n_clusters = n_samples

        self.centroids_ = self._kmeans_plus_plus_init(X_norm)

        for iteration in range(self.max_iter):
            # Assignment step
            self.labels_, current_inertia = self._assign_clusters(X_norm)

            # Update step
            new_centroids = self._update_centroids(X_norm, self.labels_)

            # Check convergence (based on centroid shift)
            # shift = 1 - cos(theta) between old and new centroids
            shifts = 1.0 - np.sum(self.centroids_ * new_centroids, axis=1)
            max_shift = np.max(shifts)

            self.centroids_ = new_centroids
            self.inertia_ = current_inertia
            self.n_iter_ = iteration + 1

            if max_shift < self.tol:
                logger.info(f"Spherical K-Means converged at iteration {self.n_iter_}")
                break

        logger.info(f"Spherical K-Means finished: inertia={self.inertia_:.4f}")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict cluster index for each sample in X."""
        assert self.centroids_ is not None
        X_norm = self._normalize(X.copy())
        labels, _ = self._assign_clusters(X_norm)
        return labels

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Compute clustering and predict cluster index for each sample."""
        self.fit(X)
        assert self.labels_ is not None
        return self.labels_


def get_optimal_k(
    X: np.ndarray, max_k: int = 15, random_state: int | None = None
) -> int:
    """Find optimal k using a simplified Elbow / Silhouette approach.

    Here we use a heuristic based on the rate of change of inertia (Elbow method).

    Args:
        X: Data matrix
        max_k: Maximum number of clusters to try
        random_state: Random seed

    Returns:
        Optimal number of clusters
    """
    n_samples = X.shape[0]
    if n_samples <= 3:
        return max(1, n_samples - 1)

    max_k = min(max_k, n_samples - 1)
    if max_k < 2:
        return 1

    inertias = []
    k_values = list(range(1, max_k + 1))

    for k in k_values:
        skm = SphericalKMeans(n_clusters=k, random_state=random_state)
        skm.fit(X)
        inertias.append(skm.inertia_)

    # Calculate first and second derivatives of inertia curve
    # We want to find the point where the rate of decrease slows down the most (the "elbow")

    # If inertia drops to 0 quickly, pick that k
    for i, inertia in enumerate(inertias):
        if inertia < 1e-5:
            return k_values[i]

    # Simple elbow calculation using distance to the line connecting first and last point
    p1 = np.array([k_values[0], inertias[0]])
    p2 = np.array([k_values[-1], inertias[-1]])

    distances = []
    for i in range(len(k_values)):
        p = np.array([k_values[i], inertias[i]])
        # Distance from point p to line segment p1-p2
        d = np.abs(np.cross(p2 - p1, p1 - p)) / np.linalg.norm(p2 - p1)
        distances.append(d)

    # The elbow is the point with the maximum distance to the line
    optimal_k_idx = np.argmax(distances)
    return k_values[optimal_k_idx]


def get_closest_to_centroid(
    X: np.ndarray, labels: np.ndarray, centroids: np.ndarray
) -> list[int]:
    """Find the index of the document closest to the centroid for each cluster.

    Returns:
        List of indices of the representative documents (one per cluster).
    """
    n_clusters = centroids.shape[0]
    representatives = []

    # Normalize X just in case
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X_norm = X / norms

    for k in range(n_clusters):
        # Indices of points in cluster k
        cluster_indices = np.where(labels == k)[0]

        if len(cluster_indices) == 0:
            continue

        if len(cluster_indices) == 1:
            representatives.append(cluster_indices[0])
            continue

        # Points in this cluster
        X_k = X_norm[cluster_indices]
        c_k = centroids[k]

        # Cosine similarity to centroid
        sims = np.dot(X_k, c_k)

        # Get index of maximum similarity
        best_local_idx = np.argmax(sims)

        # Map back to original index
        best_global_idx = cluster_indices[best_local_idx]
        representatives.append(best_global_idx)

    return representatives
