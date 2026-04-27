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

import logging

import numpy as np

logger = logging.getLogger(__name__)


class SphericalFuzzyCMeans:
    """Spherical Fuzzy C-Means (FCM) clustering for L2-normalized text embeddings.

    Using the equivalence: ||x_i - c_j||^2 = 2 - 2*(x_i . c_j) for normalized vectors.
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

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        """L2 normalize vectors (handling zero vectors)."""
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return v / norms

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

        # For Spherical FCM, the centroid must be L2-normalized so it stays on the unit sphere
        return self._normalize(numerator)

    def _update_membership(self, X: np.ndarray, centroids: np.ndarray) -> np.ndarray:
        """Update membership matrix using Proposition 3.15.

        μ_ri = 1 / Σ_{j=1}^{k} (d(x_i, c_r) / d(x_i, c_j))^(2/(m-1))
        """
        n_samples = X.shape[0]

        # Compute squared differences representing spherical distances: 2 - 2(X . c_j)
        # Using squared distances for FCM update rule calculation when m is generalized.
        # Often with Spherical FCM, the "distance" used inside the exponent is just 2-2(X.C)
        # Shape (k, N)
        distances_sq = np.zeros((self.n_clusters, n_samples))
        for j in range(self.n_clusters):
            # X shape (N, D), centroids[j] shape (D,)
            cos_sims = np.dot(X, centroids[j])
            distances_sq[j] = np.clip(2.0 - 2.0 * cos_sims, 0.0, None)

        # Handle zero distances (point exactly at centroid)
        distances_sq = np.maximum(distances_sq, 1e-10)

        # Update membership using formula from Proposition 3.15, modified for squared distances
        # Original: / d(x,c) ) ^ (2/(m-1)) -> we already have squared distance
        # So it becomes ( d^2(x,c) / d^2(x,c') ) ^ (1/(m-1))
        U = np.zeros((self.n_clusters, n_samples))
        for r in range(self.n_clusters):
            denominator = np.zeros(n_samples)
            for j in range(self.n_clusters):
                denominator += (distances_sq[r] / distances_sq[j]) ** (1 / (self.m - 1))
            U[r] = 1 / denominator

        return U

    def _compute_jm(self, X: np.ndarray, U: np.ndarray, centroids: np.ndarray) -> float:
        """Compute the generalized least squares functional J_m.

        J_m(U, C) = Σ_{i=1}^{N} Σ_{j=1}^{k} (μ_ji)^m ||x_i - c_j||²
        """
        jm = 0.0
        Um = U**self.m

        for j in range(self.n_clusters):
            cos_sims = np.dot(X, centroids[j])
            distances_sq = np.clip(2.0 - 2.0 * cos_sims, 0.0, None)
            jm += np.sum(Um[j] * distances_sq)

        return jm

    def fit(self, X: np.ndarray) -> "SphericalFuzzyCMeans":
        """Fit Spherical FCM to data.

        Args:
            X: Data matrix (n_samples, n_features). Will be L2-normalized internally.

        Returns:
            self
        """
        # Ensure input is L2 normalized
        X_norm = self._normalize(X.copy())

        n_samples = X_norm.shape[0]
        logger.info(f"Fitting Spherical FCM with k={self.n_clusters}, m={self.m}")

        # Initialize membership matrix
        U = self._init_membership(n_samples)

        self.jm_history_ = []
        prev_jm = float("inf")

        for iteration in range(self.max_iter):
            # Update centroids
            centroids = self._update_centroids(X_norm, U)

            # Update membership
            U = self._update_membership(X_norm, centroids)

            # Compute J_m
            jm = self._compute_jm(X_norm, U, centroids)
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
        X_norm = self._normalize(X.copy())
        U = self._update_membership(X_norm, self.centroids_)
        labels = np.argmax(U, axis=0)
        return U, labels

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit and return hard cluster labels."""
        self.fit(X)
        assert self.labels_ is not None
        return self.labels_


def analyze_fuzzy_documents(
    membership: np.ndarray,
    documents: list[str],
    threshold: float = 0.3,
) -> list[dict]:
    """Identify documents with diffuse membership (belonging to multiple clusters).

    A document is considered "fuzzy" if it has membership > threshold for
    more than one cluster.

    Args:
        membership: FCM membership matrix (k x N)
        documents: List of document texts
        threshold: Minimum membership to consider (default: 0.3)

    Returns:
        List of dicts with document info and their multi-cluster memberships
    """
    _, n_samples = membership.shape
    fuzzy_docs = []

    for i in range(n_samples):
        doc_membership = membership[:, i]
        clusters_above_threshold = np.where(doc_membership > threshold)[0]

        if len(clusters_above_threshold) > 1:
            fuzzy_docs.append(
                {
                    "doc_index": i,
                    "text_preview": (
                        documents[i][:100] + "..."
                        if len(documents[i]) > 100
                        else documents[i]
                    ),
                    "memberships": {
                        f"cluster_{j}": float(doc_membership[j])
                        for j in clusters_above_threshold
                    },
                    "max_cluster": int(np.argmax(doc_membership)),
                }
            )

    return fuzzy_docs


def get_optimal_k_fcm(
    X: np.ndarray, max_k: int = 15, random_state: int | None = None, m: float = 2.0
) -> int:
    """Find optimal k using a simplified Elbow method with Spherical FCM.

    Uses the same elbow heuristic as get_optimal_k in clustering.py,
    but fits SphericalFuzzyCMeans for each k instead of SphericalKMeans.

    Args:
        X: Data matrix
        max_k: Maximum number of clusters to try
        random_state: Random seed
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
        sfcm = SphericalFuzzyCMeans(n_clusters=k, m=m, random_state=random_state)
        sfcm.fit(X)
        inertias.append(sfcm.jm_)

    # If J_m drops to 0 quickly, pick that k
    for i, jm in enumerate(inertias):
        if jm < 1e-5:
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
