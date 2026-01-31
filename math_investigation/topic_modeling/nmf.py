"""Non-negative Matrix Factorization (NMF) using multiplicative update rules.

Decomposes V ≈ W @ H where:
- V: input matrix (m × n) - document-term matrix
- W: basis matrix (m × k) - document-topic affinities
- H: coefficient matrix (k × n) - topic-term distributions

Supports two cost functions:
- Frobenius: ||V - WH||²_F
- KL-divergence: D_KL(V || WH)

Reference: Lee & Seung (2001) "Algorithms for NMF"
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class NMF:
    """Non-negative Matrix Factorization using multiplicative update rules."""

    def __init__(
        self,
        n_components: int = 5,
        max_iter: int = 200,
        tol: float = 1e-4,
        random_state: int | None = None,
        cost: str = "frobenius",
    ):
        """Initialize NMF.

        Args:
            n_components: Number of topics (k)
            max_iter: Maximum iterations
            tol: Tolerance for convergence
            random_state: Random seed for reproducibility
            cost: Cost function ('frobenius' or 'kl')
        """
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.cost = cost.lower()
        self.W_: np.ndarray | None = None
        self.H_: np.ndarray | None = None
        self.reconstruction_errors_: list[float] = []

    def _initialize(self, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Initialize W and H matrices with random non-negative values."""
        if self.random_state is not None:
            np.random.seed(self.random_state)

        m, n = V.shape
        k = self.n_components

        # Initialize with small positive values
        avg = np.sqrt(np.abs(V).mean() / k)
        W = np.abs(np.random.randn(m, k)) * avg
        H = np.abs(np.random.randn(k, n)) * avg

        return W, H

    def _update_frobenius(
        self, V: np.ndarray, W: np.ndarray, H: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Multiplicative update for Frobenius norm.

        H_ij ← H_ij × (W^T V)_ij / (W^T W H)_ij
        W_ij ← W_ij × (V H^T)_ij / (W H H^T)_ij
        """
        eps = 1e-10

        numerator_H = W.T @ V
        denominator_H = (W.T @ W) @ H + eps
        H = H * (numerator_H / denominator_H)

        numerator_W = V @ H.T
        denominator_W = W @ (H @ H.T) + eps
        W = W * (numerator_W / denominator_W)

        return W, H

    def _update_kl(
        self, V: np.ndarray, W: np.ndarray, H: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Multiplicative update for KL-divergence."""
        eps = 1e-10
        WH = W @ H + eps

        # Update H
        H = H * ((W.T @ (V / WH)) / (W.sum(axis=0, keepdims=True).T + eps))

        # Recompute WH after H update
        WH = W @ H + eps

        # Update W
        W = W * (((V / WH) @ H.T) / (H.sum(axis=1, keepdims=True).T + eps))

        return W, H

    def _update(
        self, V: np.ndarray, W: np.ndarray, H: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Perform one multiplicative update step."""
        if self.cost == "kl":
            return self._update_kl(V, W, H)
        return self._update_frobenius(V, W, H)

    def reconstruction_error(
        self, V: np.ndarray, W: np.ndarray, H: np.ndarray
    ) -> float:
        """Compute reconstruction error based on cost function."""
        if self.cost == "kl":
            return self._kl_divergence(V, W, H)
        return self._frobenius_error(V, W, H)

    def _frobenius_error(self, V: np.ndarray, W: np.ndarray, H: np.ndarray) -> float:
        """Frobenius norm: ||V - WH||²_F"""
        diff = V - (W @ H)
        return np.sum(diff**2)

    def _kl_divergence(self, V: np.ndarray, W: np.ndarray, H: np.ndarray) -> float:
        """KL-divergence: D_KL(V || WH) = Σ(V log(V/WH) - V + WH)"""
        eps = 1e-10
        WH = W @ H + eps
        V_safe = V + eps
        return np.sum(V_safe * np.log(V_safe / WH) - V + WH)

    def fit(self, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Fit NMF model to input matrix.

        Args:
            V: Input matrix (n_docs × n_features)

        Returns:
            Tuple of (W, H) matrices
        """
        # Ensure non-negative input
        V = np.maximum(V, 0)

        # Initialize
        W, H = self._initialize(V)
        prev_error = float("inf")
        self.reconstruction_errors_ = []

        logger.info(
            f"Starting NMF with k={self.n_components}, max_iter={self.max_iter}"
        )

        for iteration in range(self.max_iter):
            # Update step
            W, H = self._update(V, W, H)

            # Compute error
            error = self.reconstruction_error(V, W, H)
            self.reconstruction_errors_.append(error)

            # Check convergence
            error_change = abs(prev_error - error)
            if error_change < self.tol:
                logger.info(f"Converged at iteration {iteration + 1}")
                break

            prev_error = error

            # Log progress every 50 iterations
            if (iteration + 1) % 50 == 0:
                logger.info(f"  Iteration {iteration + 1}: error = {error:.4f}")

        self.W_ = W
        self.H_ = H

        logger.info(f"Final reconstruction error: {error:.4f}")

        return W, H
