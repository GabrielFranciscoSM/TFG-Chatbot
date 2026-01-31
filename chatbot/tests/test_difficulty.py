"""Tests for the difficulty classifier module."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from chatbot.logic.difficulty import (
    ADVANCED_KEYWORDS,
    BASIC_KEYWORDS,
    INTERMEDIATE_KEYWORDS,
    DifficultyClassifier,
    DifficultyLevel,
    DifficultyResult,
    _heuristic_classify,
    classify_difficulty,
    classify_difficulty_detailed,
    get_difficulty_classifier,
)


class TestDifficultyLevel:
    """Test DifficultyLevel enum."""

    def test_enum_values(self):
        """Test that all difficulty levels have correct values."""
        assert DifficultyLevel.BASIC.value == "basic"
        assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
        assert DifficultyLevel.ADVANCED.value == "advanced"

    def test_enum_from_value(self):
        """Test creating enum from string value."""
        assert DifficultyLevel("basic") == DifficultyLevel.BASIC
        assert DifficultyLevel("intermediate") == DifficultyLevel.INTERMEDIATE
        assert DifficultyLevel("advanced") == DifficultyLevel.ADVANCED


class TestHeuristicClassification:
    """Test heuristic-based difficulty classification."""

    @pytest.mark.parametrize(
        "query",
        [
            "¿Qué es Docker?",
            "Define microservicio",
            "¿Qué significa REST?",
            "What is a container?",
            "Define API",
            "Lista los tipos de datos",
        ],
    )
    def test_basic_questions(self, query: str):
        """Basic definitional questions should be classified as BASIC."""
        result = _heuristic_classify(query)
        assert result is not None
        assert result.level == DifficultyLevel.BASIC
        assert result.method == "heuristic"

    @pytest.mark.parametrize(
        "query",
        [
            "¿Cómo funciona Docker?",
            "Diferencia entre Docker y VMs",
            "Describe el proceso de build",
            "How does Git work?",
            "Steps to create an image",
            "Características de REST",
        ],
    )
    def test_intermediate_questions(self, query: str):
        """Application/relationship questions should be INTERMEDIATE."""
        result = _heuristic_classify(query)
        assert result is not None
        assert result.level == DifficultyLevel.INTERMEDIATE
        assert result.method == "heuristic"

    @pytest.mark.parametrize(
        "query",
        [
            "¿Por qué Docker es mejor que VMs?",
            "Analiza las ventajas de contenedores",
            "Evalúa monolitos vs microservicios",
            "Why use containers?",
            "Analyze the pros and cons",
            "Compara y contrasta Kubernetes y Swarm",
        ],
    )
    def test_advanced_questions(self, query: str):
        """Analysis/evaluation questions should be ADVANCED."""
        result = _heuristic_classify(query)
        assert result is not None
        assert result.level == DifficultyLevel.ADVANCED
        assert result.method == "heuristic"

    def test_unmatched_query_returns_none(self):
        """Queries without clear patterns should return None."""
        result = _heuristic_classify("xyz random text")
        assert result is None


class TestDifficultyClassifier:
    """Test DifficultyClassifier class."""

    def test_init_without_centroids(self):
        """Classifier should initialize without centroids."""
        classifier = DifficultyClassifier()
        assert classifier.centroids is None
        assert classifier.embedding_dim == 768
        assert classifier.use_heuristics is True

    def test_init_with_custom_config(self):
        """Classifier should accept custom configuration."""
        classifier = DifficultyClassifier(
            embedding_dim=512,
            use_heuristics=False,
        )
        assert classifier.embedding_dim == 512
        assert classifier.use_heuristics is False

    def test_save_and_load_centroids(self):
        """Test saving and loading centroids."""
        classifier = DifficultyClassifier(embedding_dim=3)

        # Create mock centroids
        classifier.centroids = {
            DifficultyLevel.BASIC: np.array([1.0, 0.0, 0.0]),
            DifficultyLevel.INTERMEDIATE: np.array([0.0, 1.0, 0.0]),
            DifficultyLevel.ADVANCED: np.array([0.0, 0.0, 1.0]),
        }

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Save centroids
            classifier.save_centroids(temp_path)

            # Load in new classifier
            new_classifier = DifficultyClassifier(
                centroids_path=temp_path,
                embedding_dim=3,
            )

            assert new_classifier.centroids is not None
            assert len(new_classifier.centroids) == 3

            for level in DifficultyLevel:
                np.testing.assert_array_almost_equal(
                    classifier.centroids[level],
                    new_classifier.centroids[level],
                )
        finally:
            temp_path.unlink()

    def test_load_nonexistent_file_raises_error(self):
        """Loading from nonexistent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            DifficultyClassifier(centroids_path="/nonexistent/path.json")

    def test_classify_embedding(self):
        """Test embedding-based classification."""
        classifier = DifficultyClassifier(embedding_dim=3, use_heuristics=False)

        classifier.centroids = {
            DifficultyLevel.BASIC: np.array([1.0, 0.0, 0.0]),
            DifficultyLevel.INTERMEDIATE: np.array([0.0, 1.0, 0.0]),
            DifficultyLevel.ADVANCED: np.array([0.0, 0.0, 1.0]),
        }

        # Test embedding closest to BASIC centroid
        result = classifier.classify_embedding([0.9, 0.1, 0.0])
        assert result.level == DifficultyLevel.BASIC
        assert result.method == "embedding"
        assert result.distances is not None
        assert "basic" in result.distances

        # Test embedding closest to ADVANCED centroid
        result = classifier.classify_embedding([0.0, 0.1, 0.9])
        assert result.level == DifficultyLevel.ADVANCED

    def test_classify_embedding_without_centroids_raises_error(self):
        """Classification without centroids should raise ValueError."""
        classifier = DifficultyClassifier(use_heuristics=False)

        with pytest.raises(ValueError, match="Centroids not loaded"):
            classifier.classify_embedding([0.1, 0.2, 0.3])

    def test_classify_text_uses_heuristics_first(self):
        """classify_text should try heuristics before embeddings."""
        classifier = DifficultyClassifier(use_heuristics=True)

        # This should match heuristic pattern
        result = classifier.classify_text("¿Qué es Docker?")
        assert result.level == DifficultyLevel.BASIC
        assert result.method == "heuristic"

    def test_classify_text_length_fallback(self):
        """When no centroids and no heuristic match, use length heuristic."""
        classifier = DifficultyClassifier(use_heuristics=True)

        # Short query - no pattern match
        result = classifier.classify_text("xyz")
        assert result.level == DifficultyLevel.BASIC
        assert result.method == "length_heuristic"

        # Long query
        long_query = "x" * 150
        result = classifier.classify_text(long_query)
        assert result.level == DifficultyLevel.ADVANCED
        assert result.method == "length_heuristic"

    def test_train_centroids(self):
        """Test training centroids from labeled data."""
        classifier = DifficultyClassifier(embedding_dim=3)

        # Mock labeled data with embeddings
        labeled_data = [
            (np.array([1.0, 0.0, 0.0]), DifficultyLevel.BASIC),
            (np.array([0.9, 0.1, 0.0]), DifficultyLevel.BASIC),
            (np.array([0.0, 1.0, 0.0]), DifficultyLevel.INTERMEDIATE),
            (np.array([0.1, 0.9, 0.0]), DifficultyLevel.INTERMEDIATE),
            (np.array([0.0, 0.0, 1.0]), DifficultyLevel.ADVANCED),
            (np.array([0.0, 0.1, 0.9]), DifficultyLevel.ADVANCED),
        ]

        metrics = classifier.train(labeled_data)

        assert classifier.centroids is not None
        assert len(classifier.centroids) == 3
        assert metrics["cluster_sizes"]["basic"] == 2
        assert metrics["cluster_sizes"]["intermediate"] == 2
        assert metrics["cluster_sizes"]["advanced"] == 2

        # Verify centroid is mean
        basic_expected = np.array([0.95, 0.05, 0.0])
        np.testing.assert_array_almost_equal(
            classifier.centroids[DifficultyLevel.BASIC],
            basic_expected,
        )


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_classify_difficulty_returns_level(self):
        """classify_difficulty should return DifficultyLevel enum."""
        level = classify_difficulty("¿Qué es Docker?")
        assert isinstance(level, DifficultyLevel)
        assert level == DifficultyLevel.BASIC

    def test_classify_difficulty_detailed_returns_result(self):
        """classify_difficulty_detailed should return DifficultyResult."""
        result = classify_difficulty_detailed("¿Por qué usar Docker?")
        assert isinstance(result, DifficultyResult)
        assert result.level == DifficultyLevel.ADVANCED
        assert 0 <= result.confidence <= 1

    def test_get_difficulty_classifier_returns_singleton(self):
        """get_difficulty_classifier should return same instance."""
        classifier1 = get_difficulty_classifier()
        classifier2 = get_difficulty_classifier()
        assert classifier1 is classifier2


class TestDifficultyResult:
    """Test DifficultyResult model."""

    def test_result_validation(self):
        """DifficultyResult should validate fields."""
        result = DifficultyResult(
            level=DifficultyLevel.BASIC,
            confidence=0.85,
            method="heuristic",
            distances=None,
        )
        assert result.level == DifficultyLevel.BASIC
        assert result.confidence == 0.85

    def test_confidence_bounds(self):
        """Confidence should be between 0 and 1."""
        with pytest.raises(ValueError):
            DifficultyResult(
                level=DifficultyLevel.BASIC,
                confidence=1.5,  # Invalid
                method="test",
            )

        with pytest.raises(ValueError):
            DifficultyResult(
                level=DifficultyLevel.BASIC,
                confidence=-0.1,  # Invalid
                method="test",
            )


class TestKeywordsAndPatterns:
    """Test that keyword lists are properly defined."""

    def test_basic_keywords_exist(self):
        """BASIC_KEYWORDS should contain expected keywords."""
        assert "qué es" in BASIC_KEYWORDS
        assert "define" in BASIC_KEYWORDS
        assert "what is" in BASIC_KEYWORDS

    def test_intermediate_keywords_exist(self):
        """INTERMEDIATE_KEYWORDS should contain expected keywords."""
        assert "cómo funciona" in INTERMEDIATE_KEYWORDS
        assert "diferencia entre" in INTERMEDIATE_KEYWORDS
        assert "how does" in INTERMEDIATE_KEYWORDS

    def test_advanced_keywords_exist(self):
        """ADVANCED_KEYWORDS should contain expected keywords."""
        assert "por qué" in ADVANCED_KEYWORDS
        assert "analiza" in ADVANCED_KEYWORDS
        assert "why" in ADVANCED_KEYWORDS
