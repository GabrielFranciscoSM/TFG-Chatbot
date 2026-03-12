import numpy as np

from math_service.services.clustering import (
    SphericalKMeans,
    get_closest_to_centroid,
    get_optimal_k,
)


def normalize(X):
    """Helper to normalize an array of vectors."""
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return X / norms


def test_spherical_kmeans_basic():
    """Test basic clustering with nicely separated points."""
    # 3 clusters along the 3 axes
    X = np.array(
        [
            [1.0, 0.1, 0.0],
            [1.0, 0.0, 0.1],
            [0.1, 1.0, 0.0],
            [0.0, 1.0, 0.1],
            [0.0, 0.1, 1.0],
            [0.1, 0.0, 1.0],
        ]
    )
    X = normalize(X)

    skm = SphericalKMeans(n_clusters=3, random_state=42)
    labels = skm.fit_predict(X)

    # Check that points near the same axis got the same label
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[4] == labels[5]

    # Check that the 3 clusters are different
    assert len(set(labels)) == 3

    # Check centroids were normalized
    norms = np.linalg.norm(skm.centroids_, axis=1)
    np.testing.assert_allclose(norms, np.ones(3), rtol=1e-5)


def test_spherical_kmeans_fewer_samples_than_clusters():
    """Test handling of dataset smaller than requested clusters."""
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    X = normalize(X)

    skm = SphericalKMeans(n_clusters=5, random_state=42)
    skm.fit(X)

    assert skm.n_clusters == 2
    assert skm.centroids_ is not None
    assert skm.centroids_.shape == (2, 2)


def test_spherical_kmeans_empty_clusters_handling():
    """Test what happens if an empty cluster might occur."""
    # This scenario is hard to deterministically trigger, but we can ensure it doesn't crash on identical points
    X = np.array([[1.0, 0.0]] * 10)
    X = normalize(X)

    skm = SphericalKMeans(n_clusters=3, random_state=42)
    labels = skm.fit_predict(X)

    # Because all points are identical, k-means++ might pick identical centroids,
    # or empty clusters might occur during updates. The code handles this by picking random points.
    assert len(labels) == 10
    # Should all be assigned to one of the identical points
    # Wait, k-means++ will pick distinct points if possible, but they are all identical.
    # We just ensure it runs without division-by-zero errors.
    assert np.all(np.isfinite(skm.centroids_))


def test_get_optimal_k():
    """Test finding the optimal K on an obvious dataset."""
    rng = np.random.default_rng(42)

    # 4 distinct clumps in 10D space
    clump1 = rng.normal(loc=[1, 0, 0, 0, 0, 0, 0, 0, 0, 0], scale=0.1, size=(20, 10))
    clump2 = rng.normal(loc=[0, 1, 0, 0, 0, 0, 0, 0, 0, 0], scale=0.1, size=(20, 10))
    clump3 = rng.normal(loc=[0, 0, 1, 0, 0, 0, 0, 0, 0, 0], scale=0.1, size=(20, 10))
    clump4 = rng.normal(loc=[0, 0, 0, 1, 0, 0, 0, 0, 0, 0], scale=0.1, size=(20, 10))

    X = np.vstack([clump1, clump2, clump3, clump4])
    X = normalize(X)

    k = get_optimal_k(X, max_k=8, random_state=42)
    # Could be 4 realistically, let's just make sure it's sensible. The heuristic might say 3 or 4 depending on variance.
    assert k in [3, 4]


def test_get_closest_to_centroid():
    """Test representative extraction."""
    X = np.array(
        [
            [1.0, 0.01],  # Close to X axis
            [1.0, 0.0],  # Exact X axis (centroid)
            [1.0, -0.01],  # Close to X axis
            [0.01, 1.0],  # Close to Y axis
            [0.0, 1.0],  # Exact Y axis (centroid)
            [-0.01, 1.0],  # Close to Y axis
        ]
    )
    X = normalize(X)

    # Fake labels: 0 for the first 3, 1 for the next 3
    labels = np.array([0, 0, 0, 1, 1, 1])

    # Fake centroids exactly on the axes
    centroids = np.array([[1.0, 0.0], [0.0, 1.0]])

    reps = get_closest_to_centroid(X, labels, centroids)

    # The representatives should be the ones exactly on the axes (index 1 and 4)
    assert len(reps) == 2
    assert 1 in reps
    assert 4 in reps
