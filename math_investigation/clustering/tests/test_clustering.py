"""
Tests for K-Means and Fuzzy C-Means clustering implementations.

These tests verify the clustering algorithms implemented in
math_investigation/clustering/, based on TFG Section 3.2.
"""

import numpy as np
import pytest

from math_investigation.clustering.fcm import FuzzyCMeans, analyze_fuzzy_documents
from math_investigation.clustering.kmeans import KMeans
from math_investigation.clustering.metrics import (
    adjusted_rand_index,
    elbow_method,
    fuzzy_partition_coefficient,
    normalized_mutual_information,
    silhouette_score,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def simple_data():
    """Simple 2D clusterable dataset with 3 well-separated clusters."""
    np.random.seed(42)
    cluster1 = np.random.randn(20, 2) + np.array([0, 0])
    cluster2 = np.random.randn(20, 2) + np.array([10, 0])
    cluster3 = np.random.randn(20, 2) + np.array([5, 10])
    return np.vstack([cluster1, cluster2, cluster3])


@pytest.fixture
def simple_labels():
    """Ground truth labels for simple_data fixture."""
    return np.array([0] * 20 + [1] * 20 + [2] * 20)


@pytest.fixture
def overlapping_data():
    """Dataset with overlapping clusters for fuzzy membership testing."""
    np.random.seed(42)
    # Two clusters that slightly overlap
    cluster1 = np.random.randn(30, 2) + np.array([0, 0])
    cluster2 = np.random.randn(30, 2) + np.array([2, 0])  # Close overlap
    return np.vstack([cluster1, cluster2])


# =============================================================================
# K-Means Tests
# =============================================================================


class TestKMeans:
    """Tests for K-Means clustering implementation."""

    def test_init_default_parameters(self):
        """KMeans initializes with correct default parameters."""
        kmeans = KMeans()
        assert kmeans.n_clusters == 5
        assert kmeans.max_iter == 300
        assert kmeans.tol == 1e-4
        assert kmeans.init == "kmeans++"

    def test_init_custom_parameters(self):
        """KMeans accepts custom initialization parameters."""
        kmeans = KMeans(n_clusters=3, max_iter=100, tol=1e-6, random_state=42)
        assert kmeans.n_clusters == 3
        assert kmeans.max_iter == 100
        assert kmeans.tol == 1e-6
        assert kmeans.random_state == 42

    def test_fit_produces_centroids(self, simple_data):
        """fit() should produce k centroids."""
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(simple_data)

        assert kmeans.centroids_ is not None
        assert kmeans.centroids_.shape == (3, 2)

    def test_fit_produces_labels(self, simple_data):
        """fit() should assign labels to all samples."""
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(simple_data)

        assert kmeans.labels_ is not None
        assert len(kmeans.labels_) == len(simple_data)
        assert set(kmeans.labels_) <= {0, 1, 2}

    def test_fit_convergence(self, simple_data):
        """K-Means should converge (SSE decreases monotonically)."""
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(simple_data)

        # Proposition 3.2: SSE sequence is non-increasing
        sse_history = kmeans.sse_history_
        for i in range(1, len(sse_history)):
            assert sse_history[i] <= sse_history[i - 1] + 1e-10

    def test_fit_predict(self, simple_data):
        """fit_predict() returns labels."""
        kmeans = KMeans(n_clusters=3, random_state=42)
        labels = kmeans.fit_predict(simple_data)

        assert labels is not None
        assert len(labels) == len(simple_data)

    def test_predict_new_data(self, simple_data):
        """predict() assigns labels to new data using trained centroids."""
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(simple_data)

        # Predict on new point close to cluster 1 centroid
        new_point = np.array([[10.0, 0.0]])
        label = kmeans.predict(new_point)

        assert len(label) == 1
        assert label[0] in {0, 1, 2}

    def test_reproducibility(self, simple_data):
        """Same random_state should produce same results."""
        kmeans1 = KMeans(n_clusters=3, random_state=42)
        kmeans2 = KMeans(n_clusters=3, random_state=42)

        labels1 = kmeans1.fit_predict(simple_data)
        labels2 = kmeans2.fit_predict(simple_data)

        np.testing.assert_array_equal(labels1, labels2)

    def test_random_init(self, simple_data):
        """Random initialization should also work."""
        kmeans = KMeans(n_clusters=3, init="random", random_state=42)
        labels = kmeans.fit_predict(simple_data)

        assert labels is not None
        assert len(labels) == len(simple_data)

    def test_inertia_computed(self, simple_data):
        """Final SSE (inertia) should be computed and stored."""
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(simple_data)

        assert kmeans.inertia_ > 0
        assert kmeans.inertia_ == kmeans.sse_history_[-1]


# =============================================================================
# Fuzzy C-Means Tests
# =============================================================================


class TestFuzzyCMeans:
    """Tests for Fuzzy C-Means (FCM) clustering implementation."""

    def test_init_default_parameters(self):
        """FCM initializes with correct default parameters."""
        fcm = FuzzyCMeans()
        assert fcm.n_clusters == 5
        assert fcm.m == 2.0
        assert fcm.max_iter == 300
        assert fcm.tol == 1e-4

    def test_init_rejects_invalid_fuzziness(self):
        """FCM should reject m <= 1."""
        with pytest.raises(ValueError, match="m must be > 1"):
            FuzzyCMeans(m=1.0)

        with pytest.raises(ValueError, match="m must be > 1"):
            FuzzyCMeans(m=0.5)

    def test_fit_produces_centroids(self, simple_data):
        """fit() should produce k centroids."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm.fit(simple_data)

        assert fcm.centroids_ is not None
        assert fcm.centroids_.shape == (3, 2)

    def test_fit_produces_membership(self, simple_data):
        """fit() should produce membership matrix U."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm.fit(simple_data)

        assert fcm.membership_ is not None
        assert fcm.membership_.shape == (3, len(simple_data))

    def test_membership_sums_to_one(self, simple_data):
        """Membership values for each point should sum to 1 (Definition 3.11, C1)."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm.fit(simple_data)

        assert fcm.membership_ is not None
        membership_sums = fcm.membership_.sum(axis=0)
        np.testing.assert_array_almost_equal(
            membership_sums, np.ones(len(simple_data)), decimal=5
        )

    def test_membership_values_in_range(self, simple_data):
        """All membership values should be in [0, 1]."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm.fit(simple_data)

        assert fcm.membership_ is not None
        assert np.all(fcm.membership_ >= 0)
        assert np.all(fcm.membership_ <= 1)

    def test_fit_convergence(self, simple_data):
        """FCM should converge (J_m decreases)."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm.fit(simple_data)

        # J_m should generally decrease (may have small fluctuations)
        jm_history = fcm.jm_history_
        # Check overall trend: final should be less than initial
        assert jm_history[-1] <= jm_history[0]

    def test_hard_labels_from_membership(self, simple_data):
        """Hard labels should be argmax of membership."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm.fit(simple_data)

        expected_labels = np.argmax(fcm.membership_, axis=0)
        np.testing.assert_array_equal(fcm.labels_, expected_labels)

    def test_higher_fuzziness_more_uniform(self, simple_data):
        """Higher m should produce more uniform membership distributions."""
        fcm_low = FuzzyCMeans(n_clusters=3, m=1.5, random_state=42)
        fcm_high = FuzzyCMeans(n_clusters=3, m=4.0, random_state=42)

        fcm_low.fit(simple_data)
        fcm_high.fit(simple_data)

        # Higher m should have membership values closer to 1/k
        # Measure variance of membership for a sample point
        assert fcm_low.membership_ is not None
        assert fcm_high.membership_ is not None
        var_low = np.var(fcm_low.membership_[:, 0])
        var_high = np.var(fcm_high.membership_[:, 0])

        assert var_high < var_low  # Higher m = more uniform = lower variance

    def test_predict_new_data(self, simple_data):
        """predict() should return membership and labels for new data."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm.fit(simple_data)

        new_points = np.array([[0.0, 0.0], [10.0, 0.0]])
        membership, labels = fcm.predict(new_points)

        assert membership.shape == (3, 2)
        assert len(labels) == 2

    def test_fit_predict(self, simple_data):
        """fit_predict() returns hard labels."""
        fcm = FuzzyCMeans(n_clusters=3, random_state=42)
        labels = fcm.fit_predict(simple_data)

        assert labels is not None
        assert len(labels) == len(simple_data)

    def test_reproducibility(self, simple_data):
        """Same random_state should produce same results."""
        fcm1 = FuzzyCMeans(n_clusters=3, random_state=42)
        fcm2 = FuzzyCMeans(n_clusters=3, random_state=42)

        labels1 = fcm1.fit_predict(simple_data)
        labels2 = fcm2.fit_predict(simple_data)

        np.testing.assert_array_equal(labels1, labels2)


class TestAnalyzeFuzzyDocuments:
    """Tests for the fuzzy document analysis function."""

    def test_identifies_fuzzy_documents(self):
        """Should identify documents with membership > threshold in multiple clusters."""
        # Mock membership matrix: doc 0 belongs clearly to cluster 0,
        # doc 1 is fuzzy between clusters 0 and 1
        membership = np.array(
            [
                [0.9, 0.4, 0.1],  # cluster 0
                [0.1, 0.5, 0.1],  # cluster 1
            ]
        )
        documents = ["clear doc", "fuzzy doc", "clear doc 2"]

        result = analyze_fuzzy_documents(membership, documents, threshold=0.3)

        assert len(result) == 1
        assert result[0]["doc_index"] == 1
        assert "cluster_0" in result[0]["memberships"]
        assert "cluster_1" in result[0]["memberships"]

    def test_returns_empty_for_crisp_partition(self):
        """Should return empty list when all docs belong clearly to one cluster."""
        membership = np.array(
            [
                [0.95, 0.02],  # cluster 0
                [0.05, 0.98],  # cluster 1
            ]
        )
        documents = ["doc 1", "doc 2"]

        result = analyze_fuzzy_documents(membership, documents, threshold=0.3)

        assert len(result) == 0


# =============================================================================
# Clustering Metrics Tests
# =============================================================================


class TestSilhouetteScore:
    """Tests for Silhouette Score computation."""

    def test_well_separated_clusters(self, simple_data, simple_labels):
        """Well-separated clusters should have high silhouette score."""
        score = silhouette_score(simple_data, simple_labels)
        # Score should be positive for well-separated clusters
        assert score > 0.5

    def test_single_cluster_returns_zero(self, simple_data):
        """Single cluster should return silhouette score of 0."""
        labels = np.zeros(len(simple_data), dtype=int)
        score = silhouette_score(simple_data, labels)
        assert score == 0.0

    def test_score_in_valid_range(self, simple_data, simple_labels):
        """Silhouette score should be in [-1, 1]."""
        score = silhouette_score(simple_data, simple_labels)
        assert -1 <= score <= 1


class TestAdjustedRandIndex:
    """Tests for Adjusted Rand Index computation."""

    def test_perfect_clustering(self, simple_labels):
        """Perfect clustering should have ARI = 1."""
        ari = adjusted_rand_index(simple_labels, simple_labels)
        assert abs(ari - 1.0) < 1e-10

    def test_different_label_names(self):
        """ARI should work regardless of label names."""
        labels_true = np.array([0, 0, 1, 1, 2, 2])
        labels_pred = np.array([1, 1, 2, 2, 0, 0])  # Same partition, different names
        ari = adjusted_rand_index(labels_true, labels_pred)
        assert abs(ari - 1.0) < 1e-10

    def test_random_clustering(self):
        """Random clustering should have ARI close to 0."""
        np.random.seed(42)
        labels_true = np.array([0] * 50 + [1] * 50)
        labels_pred = np.random.randint(0, 2, 100)
        ari = adjusted_rand_index(labels_true, labels_pred)
        # Random should be close to 0, but with some variance
        assert -0.5 < ari < 0.5

    def test_length_mismatch_raises_error(self):
        """ARI should raise error for different length arrays."""
        labels_true = np.array([0, 1, 2])
        labels_pred = np.array([0, 1])
        with pytest.raises(ValueError, match="same length"):
            adjusted_rand_index(labels_true, labels_pred)


class TestNormalizedMutualInformation:
    """Tests for Normalized Mutual Information computation."""

    def test_perfect_clustering(self, simple_labels):
        """Perfect clustering should have NMI = 1."""
        nmi = normalized_mutual_information(simple_labels, simple_labels)
        assert abs(nmi - 1.0) < 1e-10

    def test_nmi_in_valid_range(self, simple_labels):
        """NMI should be in [0, 1]."""
        np.random.seed(42)
        random_labels = np.random.randint(0, 3, len(simple_labels))
        nmi = normalized_mutual_information(simple_labels, random_labels)
        assert 0 <= nmi <= 1

    def test_length_mismatch_raises_error(self):
        """NMI should raise error for different length arrays."""
        labels_true = np.array([0, 1, 2])
        labels_pred = np.array([0, 1])
        with pytest.raises(ValueError, match="same length"):
            normalized_mutual_information(labels_true, labels_pred)


class TestFuzzyPartitionCoefficient:
    """Tests for Fuzzy Partition Coefficient computation."""

    def test_crisp_partition(self):
        """Crisp partition (each point in one cluster) should have FPC = 1."""
        # Crisp membership: each column has exactly one 1
        membership = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 1],
            ]
        )
        fpc = fuzzy_partition_coefficient(membership)
        assert abs(fpc - 1.0) < 1e-10

    def test_uniform_membership(self):
        """Uniform membership should have FPC = 1/k."""
        # Uniform membership: each element = 1/3
        k = 3
        membership = np.ones((k, 10)) / k
        fpc = fuzzy_partition_coefficient(membership)
        expected = 1 / k
        assert abs(fpc - expected) < 1e-10

    def test_fpc_in_valid_range(self):
        """FPC should be in [1/k, 1]."""
        np.random.seed(42)
        k = 4
        membership = np.random.rand(k, 20)
        membership = membership / membership.sum(axis=0, keepdims=True)

        fpc = fuzzy_partition_coefficient(membership)
        assert 1 / k <= fpc <= 1


class TestElbowMethod:
    """Tests for the Elbow Method utility."""

    def test_returns_results_for_k_range(self, simple_data):
        """Elbow method should return results for all k values."""
        results = elbow_method(simple_data, k_range=range(2, 5), random_state=42)

        assert "k" in results
        assert "sse" in results
        assert "silhouette" in results
        assert len(results["k"]) == 3
        assert results["k"] == [2, 3, 4]

    def test_sse_decreases_with_k(self, simple_data):
        """SSE should generally decrease as k increases."""
        results = elbow_method(simple_data, k_range=range(2, 6), random_state=42)

        # SSE should decrease (or stay same) as k increases
        for i in range(1, len(results["sse"])):
            assert results["sse"][i] <= results["sse"][i - 1] + 1e-6


# =============================================================================
# Integration Tests
# =============================================================================


class TestClusteringIntegration:
    """Integration tests comparing K-Means and FCM."""

    def test_kmeans_and_fcm_find_same_clusters(self, simple_data, simple_labels):
        """K-Means and FCM should find similar cluster structures."""
        kmeans = KMeans(n_clusters=3, random_state=42)
        fcm = FuzzyCMeans(n_clusters=3, m=2.0, random_state=42)

        kmeans_labels = kmeans.fit_predict(simple_data)
        fcm_labels = fcm.fit_predict(simple_data)

        # Both should have reasonable ARI with ground truth
        kmeans_ari = adjusted_rand_index(simple_labels, kmeans_labels)
        fcm_ari = adjusted_rand_index(simple_labels, fcm_labels)

        # With well-separated clusters, both should perform well
        assert kmeans_ari > 0.7
        assert fcm_ari > 0.7

    def test_fcm_provides_uncertainty_info(self, overlapping_data):
        """FCM should show higher uncertainty for overlapping clusters."""
        fcm = FuzzyCMeans(n_clusters=2, random_state=42)
        fcm.fit(overlapping_data)

        # Find max membership for each point
        max_memberships = np.max(fcm.membership_, axis=0)

        # With overlapping clusters, some points should have lower max membership
        # (indicating uncertainty about cluster assignment)
        min_confidence = np.min(max_memberships)
        assert min_confidence < 0.95  # Some uncertainty expected
