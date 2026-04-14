"""Generic clustering for embeddings.

Supports:
- Distance metrics: cosine and euclidean
- Algorithms: K-Means and Fuzzy C-Means (FCM)
"""

from __future__ import annotations

import logging
from typing import Literal

import numpy as np

logger = logging.getLogger(__name__)

DistanceType = Literal["cosine", "euclidean"]
AlgorithmType = Literal["kmeans", "fcm"]


class GenericKMeans:
    """Configurable clustering with K-Means and FCM backends."""

    def __init__(
        self,
        n_clusters: int = 5,
        algorithm: AlgorithmType = "kmeans",
        distance: DistanceType = "cosine",
        max_iter: int = 300,
        tol: float = 1e-4,
        random_state: int | None = None,
        m: float = 2.0,
    ):
        """Initialize clustering model.

        Args:
            n_clusters: Number of clusters.
            algorithm: Clustering algorithm ("kmeans" or "fcm").
            distance: Distance metric ("cosine" or "euclidean").
            max_iter: Maximum number of iterations.
            tol: Convergence tolerance.
            random_state: Random seed for reproducibility.
            m: Fuzziness parameter for FCM (must be > 1).
        """
        if n_clusters < 1:
            raise ValueError("n_clusters must be >= 1")
        if algorithm not in {"kmeans", "fcm"}:
            raise ValueError("algorithm must be 'kmeans' or 'fcm'")
        if distance not in {"cosine", "euclidean"}:
            raise ValueError("distance must be 'cosine' or 'euclidean'")
        if algorithm == "fcm" and m <= 1.0:
            raise ValueError("For FCM, m must be > 1")

        self.n_clusters = n_clusters
        self.algorithm = algorithm
        self.distance = distance
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.m = m

        self.centroids_: np.ndarray | None = None
        self.labels_: np.ndarray | None = None
        self.membership_: np.ndarray | None = None
        self.inertia_: float = 0.0
        self.n_iter_: int = 0

    @staticmethod
    def _normalize(v: np.ndarray) -> np.ndarray:
        """L2 normalize vectors row-wise (handling zero vectors)."""
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return v / norms

    def _prepare_X(self, X: np.ndarray) -> np.ndarray:
        """Preprocess input according to distance metric."""
        X = np.asarray(X, dtype=float)
        if X.ndim != 2:
            raise ValueError("X must be a 2D array")
        if self.distance == "cosine":
            return self._normalize(X.copy())
        return X.copy()

    def _pairwise_distances(self, X: np.ndarray, C: np.ndarray) -> np.ndarray:
        """Compute distance matrix between samples X and centroids C."""
        if self.distance == "cosine":
            Xn = self._normalize(X)
            Cn = self._normalize(C)
            cos_sims = np.dot(Xn, Cn.T)
            return np.clip(1.0 - cos_sims, 0.0, None)

        diff = X[:, None, :] - C[None, :, :]
        return np.linalg.norm(diff, axis=2)

    def _kmeans_plus_plus_init(self, X: np.ndarray) -> np.ndarray:
        """Initialize centroids using k-means++ strategy."""
        n_samples, n_features = X.shape
        centroids = np.zeros((self.n_clusters, n_features), dtype=float)
        rng = np.random.default_rng(self.random_state)

        first_idx = rng.integers(0, n_samples)
        centroids[0] = X[first_idx]

        min_sq_distances = np.full(n_samples, np.inf)

        for c in range(1, self.n_clusters):
            distances = self._pairwise_distances(X, centroids[c - 1 : c]).ravel()
            sq_distances = distances * distances
            min_sq_distances = np.minimum(min_sq_distances, sq_distances)

            prob_sum = min_sq_distances.sum()
            if prob_sum > 0:
                probabilities = min_sq_distances / prob_sum
            else:
                probabilities = np.ones(n_samples) / n_samples

            next_idx = rng.choice(n_samples, p=probabilities)
            centroids[c] = X[next_idx]

        # if self.distance == "cosine":
        #     centroids = self._normalize(centroids)
        return centroids

    def _assign_clusters(
        self, X: np.ndarray, C: np.ndarray
    ) -> tuple[np.ndarray, float]:
        """Assign points to nearest centroid and compute inertia."""
        distances = self._pairwise_distances(X, C)
        labels = np.argmin(distances, axis=1)
        min_distances = distances[np.arange(distances.shape[0]), labels]
        inertia = float(np.sum(min_distances * min_distances))
        return labels, inertia

    def _update_centroids_kmeans(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """Update centroids for K-Means."""
        n_samples, n_features = X.shape
        new_centroids = np.zeros((self.n_clusters, n_features), dtype=float)
        counts = np.bincount(labels, minlength=self.n_clusters)

        np.add.at(new_centroids, labels, X)

        non_empty = counts > 0
        new_centroids[non_empty] /= counts[non_empty, None]

        if np.any(~non_empty):
            rng = np.random.default_rng(self.random_state)
            for j in np.where(~non_empty)[0]:
                new_centroids[j] = X[rng.integers(0, n_samples)]

        if self.distance == "cosine":
            new_centroids = self._normalize(new_centroids)
        return new_centroids

    def _update_membership_fcm(self, distances: np.ndarray) -> np.ndarray:
        """Update membership matrix for FCM.

        Formula:
            u_ik = 1 / sum_j ((d_ik / d_ij) ** (2 / (m - 1)))
        """
        n_samples, n_clusters = distances.shape
        membership = np.zeros((n_samples, n_clusters), dtype=float)
        exponent = 2.0 / (self.m - 1.0)
        eps = 1e-12

        for i in range(n_samples):
            row = distances[i]
            zero_idx = np.where(row <= eps)[0]
            if len(zero_idx) > 0:
                membership[i, zero_idx] = 1.0 / len(zero_idx)
                continue

            ratios = (row[:, None] / row[None, :]) ** exponent
            membership[i] = 1.0 / np.sum(ratios, axis=1)

        return membership

    def _update_centroids_fcm(
        self, X: np.ndarray, membership: np.ndarray
    ) -> np.ndarray:
        """Update centroids for FCM using weighted means."""
        um = membership**self.m
        denominator = np.sum(um, axis=0, keepdims=True).T
        denominator[denominator == 0] = 1.0
        centroids = (um.T @ X) / denominator

        if self.distance == "cosine":
            centroids = self._normalize(centroids)
        return centroids

    def _fit_kmeans(self, X: np.ndarray) -> None:
        """Run K-Means optimization."""
        logger.info(
            "Fitting K-Means with k=%s, distance=%s", self.n_clusters, self.distance
        )
        self.centroids_ = self._kmeans_plus_plus_init(X)

        for iteration in range(self.max_iter):
            assert self.centroids_ is not None
            labels, inertia = self._assign_clusters(X, self.centroids_)
            new_centroids = self._update_centroids_kmeans(X, labels)

            shifts = self._pairwise_distances(self.centroids_, new_centroids)
            max_shift = float(np.max(np.diag(shifts)))

            self.centroids_ = new_centroids
            self.labels_ = labels
            self.inertia_ = inertia
            self.n_iter_ = iteration + 1

            if max_shift < self.tol:
                logger.info("K-Means converged at iteration %s", self.n_iter_)
                break

    def _fit_fcm(self, X: np.ndarray) -> None:
        """Run Fuzzy C-Means optimization."""
        logger.info(
            "Fitting FCM with k=%s, distance=%s, m=%.3f",
            self.n_clusters,
            self.distance,
            self.m,
        )

        rng = np.random.default_rng(self.random_state)
        membership = rng.random((X.shape[0], self.n_clusters))
        membership /= membership.sum(axis=1, keepdims=True)

        self.centroids_ = self._update_centroids_fcm(X, membership)

        for iteration in range(self.max_iter):
            assert self.centroids_ is not None
            distances = self._pairwise_distances(X, self.centroids_)
            membership = self._update_membership_fcm(distances)
            new_centroids = self._update_centroids_fcm(X, membership)

            shifts = self._pairwise_distances(self.centroids_, new_centroids)
            max_shift = float(np.max(np.diag(shifts)))

            self.centroids_ = new_centroids
            self.membership_ = membership
            self.labels_ = np.argmax(membership, axis=1)
            self.inertia_ = float(np.sum((membership**self.m) * (distances**2)))
            self.n_iter_ = iteration + 1

            if max_shift < self.tol:
                logger.info("FCM converged at iteration %s", self.n_iter_)
                break

    def fit(self, X: np.ndarray) -> GenericKMeans:
        """Compute clustering on X."""
        X_prep = self._prepare_X(X)
        n_samples = X_prep.shape[0]

        if n_samples == 0:
            raise ValueError("X must contain at least one sample")

        if n_samples < self.n_clusters:
            logger.warning(
                "Number of samples (%s) < n_clusters (%s). Reducing k.",
                n_samples,
                self.n_clusters,
            )
            self.n_clusters = n_samples

        if self.algorithm == "kmeans":
            self._fit_kmeans(X_prep)
        else:
            self._fit_fcm(X_prep)

        logger.info(
            "Clustering finished: algorithm=%s, distance=%s, inertia=%.4f",
            self.algorithm,
            self.distance,
            self.inertia_,
        )
        return self

    def predict_membership(self, X: np.ndarray) -> np.ndarray:
        """Predict soft membership for X.

        For K-Means, returns one-hot memberships.
        """
        if self.centroids_ is None:
            raise ValueError("Model has not been fitted yet")

        X_prep = self._prepare_X(X)
        distances = self._pairwise_distances(X_prep, self.centroids_)

        if self.algorithm == "fcm":
            return self._update_membership_fcm(distances)

        labels = np.argmin(distances, axis=1)
        membership = np.zeros((X_prep.shape[0], self.n_clusters), dtype=float)
        membership[np.arange(X_prep.shape[0]), labels] = 1.0
        return membership

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict cluster index for each sample in X."""
        membership = self.predict_membership(X)
        return np.argmax(membership, axis=1)

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit model and return hard labels."""
        self.fit(X)
        assert self.labels_ is not None
        return self.labels_


class SphericalKMeans(GenericKMeans):
    """Backward-compatible spherical K-Means wrapper."""

    def __init__(
        self,
        n_clusters: int = 5,
        max_iter: int = 300,
        tol: float = 1e-4,
        random_state: int | None = None,
    ):
        super().__init__(
            n_clusters=n_clusters,
            algorithm="kmeans",
            distance="cosine",
            max_iter=max_iter,
            tol=tol,
            random_state=random_state,
        )


class SphericalFuzzyCMeans(GenericKMeans):
    """Backward-compatible spherical FCM wrapper."""

    def __init__(
        self,
        n_clusters: int = 5,
        max_iter: int = 300,
        tol: float = 1e-4,
        random_state: int | None = None,
        m: float = 2.0,
    ):
        super().__init__(
            n_clusters=n_clusters,
            algorithm="fcm",
            distance="cosine",
            max_iter=max_iter,
            tol=tol,
            random_state=random_state,
            m=m,
        )


def get_optimal_k(
    X: np.ndarray,
    max_k: int = 15,
    random_state: int | None = None,
    algorithm: AlgorithmType = "kmeans",
    distance: DistanceType = "cosine",
    m: float = 2.0,
) -> int:
    """Find optimal k using a simplified Elbow / Silhouette approach.

    Here we use a heuristic based on the rate of change of inertia (Elbow method).

    Args:
        X: Data matrix
        max_k: Maximum number of clusters to try
        random_state: Random seed
        algorithm: Clustering algorithm ("kmeans" or "fcm")
        distance: Distance metric ("cosine" or "euclidean")
        m: Fuzziness parameter for FCM

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
        model = GenericKMeans(
            n_clusters=k,
            algorithm=algorithm,
            distance=distance,
            random_state=random_state,
            m=m,
        )
        model.fit(X)
        inertias.append(model.inertia_)

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
    X: np.ndarray,
    labels: np.ndarray,
    centroids: np.ndarray,
    distance: DistanceType = "cosine",
) -> list[int]:
    """Find the index of the document closest to the centroid for each cluster.

    Returns:
        List of indices of the representative documents (one per cluster).
    """
    n_clusters = centroids.shape[0]
    representatives = []

    if distance == "cosine":
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        X_proc = X / norms

        centroid_norms = np.linalg.norm(centroids, axis=1, keepdims=True)
        centroid_norms[centroid_norms == 0] = 1.0
        centroids_proc = centroids / centroid_norms
    elif distance == "euclidean":
        X_proc = X
        centroids_proc = centroids
    else:
        raise ValueError("distance must be 'cosine' or 'euclidean'")

    for k in range(n_clusters):
        # Indices of points in cluster k
        cluster_indices = np.where(labels == k)[0]

        if len(cluster_indices) == 0:
            continue

        if len(cluster_indices) == 1:
            representatives.append(cluster_indices[0])
            continue

        X_k = X_proc[cluster_indices]
        c_k = centroids_proc[k]

        if distance == "cosine":
            sims = np.dot(X_k, c_k)
            best_local_idx = np.argmax(sims)
        else:
            dists = np.linalg.norm(X_k - c_k, axis=1)
            best_local_idx = np.argmin(dists)

        # Map back to original index
        best_global_idx = cluster_indices[best_local_idx]
        representatives.append(best_global_idx)

    return representatives
