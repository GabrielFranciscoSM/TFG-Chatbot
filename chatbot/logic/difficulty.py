"""
Question difficulty classifier using embedding-based clustering.

This module provides a classifier that categorizes questions into three difficulty
levels (basic, intermediate, advanced) using semantic embeddings and distance to
pre-trained cluster centroids.

Classification Criteria:
    - **Basic**: Foundational concepts, definitions, simple factual questions
    - **Intermediate**: Application, relationships between concepts, technical details
    - **Advanced**: Analysis, synthesis, evaluation, complex multi-concept questions

The classifier combines two approaches:
    1. **Heuristic-based**: Fast pattern/keyword matching (no latency)
    2. **Embedding-based**: Semantic similarity to difficulty centroids (more accurate)

Example:
    >>> from chatbot.logic.difficulty import DifficultyClassifier, DifficultyLevel
    >>> classifier = DifficultyClassifier()
    >>> classifier.classify_text("¿Qué es Docker?")
    DifficultyLevel.BASIC
    >>> classifier.classify_text("¿Por qué Docker es mejor que máquinas virtuales para microservicios?")
    DifficultyLevel.ADVANCED
"""

import json
import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import requests
from pydantic import BaseModel, Field

from chatbot.config import settings

logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """Classification of question difficulty levels."""

    BASIC = "basic"  # Foundational concepts, definitions
    INTERMEDIATE = "intermediate"  # Application, relationships
    ADVANCED = "advanced"  # Analysis, synthesis, evaluation


class DifficultyResult(BaseModel):
    """Result of difficulty classification."""

    level: DifficultyLevel = Field(..., description="Classified difficulty level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    method: str = Field(
        ..., description="Classification method used (heuristic or embedding)"
    )
    distances: dict[str, float] | None = Field(
        None, description="Distances to each centroid (only for embedding method)"
    )


# =============================================================================
# Heuristic Classification Keywords and Patterns
# =============================================================================

# Keywords indicating BASIC difficulty (definitions, simple facts)
BASIC_KEYWORDS = [
    # Spanish
    "qué es",
    "que es",
    "definición",
    "definicion",
    "define",
    "significa",
    "nombre",
    "lista",
    "enumera",
    "cuál es",
    "cual es",
    "cuáles son",
    "cuales son",
    "ejemplo de",
    "menciona",
    # English
    "what is",
    "define",
    "definition",
    "list",
    "name",
    "which is",
    "example of",
    "mention",
]

# Keywords indicating INTERMEDIATE difficulty (application, relationships)
INTERMEDIATE_KEYWORDS = [
    # Spanish
    "cómo funciona",
    "como funciona",
    "cómo se usa",
    "como se usa",
    "diferencia entre",
    "relación entre",
    "relacion entre",
    "para qué sirve",
    "para que sirve",
    "describe",
    "pasos para",
    "proceso de",
    "características",
    "caracteristicas",
    # English
    "how does",
    "how to use",
    "difference between",
    "relationship between",
    "what is used for",
    "describe",
    "steps to",
    "process of",
    "features of",
    "characteristics",
]

# Keywords indicating ADVANCED difficulty (analysis, synthesis, evaluation)
ADVANCED_KEYWORDS = [
    # Spanish
    "por qué",
    "porqué",
    "analiza",
    "analizar",
    "evalúa",
    "evaluar",
    "compara y contrasta",
    "ventajas y desventajas",
    "pros y contras",
    "justifica",
    "argumenta",
    "diseña",
    "propón",
    "propon",
    "implementa",
    "optimiza",
    "qué pasaría si",
    "que pasaria si",
    "implicaciones",
    "consecuencias",
    "mejor enfoque",
    "mejor manera",
    # English
    "why",
    "analyze",
    "evaluate",
    "compare and contrast",
    "advantages and disadvantages",
    "pros and cons",
    "justify",
    "argue",
    "design",
    "propose",
    "implement",
    "optimize",
    "what would happen if",
    "implications",
    "consequences",
    "best approach",
    "best way",
]

# Regex patterns for difficulty detection
BASIC_PATTERNS = [
    r"\bqu[eé]\s+es\s+(?:un|una|el|la)\b",  # "qué es un/una/el/la"
    r"\bdefine\b",
    r"\bwhat\s+is\s+(?:a|an|the)\b",
]

INTERMEDIATE_PATTERNS = [
    r"\bc[oó]mo\s+(?:funciona|se\s+(?:usa|hace|implementa))\b",
    r"\bdiferencia\s+entre\b",
    r"\bhow\s+(?:does|do|to)\b",
    r"\bsteps\s+to\b",
]

ADVANCED_PATTERNS = [
    r"\bpor\s*qu[eé]\b",
    r"\banaliza\b",
    r"\beval[uú]a\b",
    r"\bcompara\s+y\s+contrasta\b",
    r"\bwhy\s+(?:is|are|do|does|should|would)\b",
    r"\banalyze\b",
    r"\bevaluate\b",
]


def _heuristic_classify(query: str) -> DifficultyResult | None:
    """
    Classify query difficulty using heuristic pattern/keyword matching.

    This is a fast classification method that doesn't require embeddings.
    Returns None if no clear pattern is matched (fall back to embedding).

    Args:
        query: The question text to classify

    Returns:
        DifficultyResult if a pattern matches, None otherwise
    """
    query_lower = query.lower().strip()

    # Check ADVANCED patterns first (most specific)
    for pattern in ADVANCED_PATTERNS:
        if re.search(pattern, query_lower):
            return DifficultyResult(
                level=DifficultyLevel.ADVANCED,
                confidence=0.85,
                method="heuristic",
                distances=None,
            )

    # Check ADVANCED keywords
    for keyword in ADVANCED_KEYWORDS:
        if keyword in query_lower:
            return DifficultyResult(
                level=DifficultyLevel.ADVANCED,
                confidence=0.80,
                method="heuristic",
                distances=None,
            )

    # Check INTERMEDIATE patterns
    for pattern in INTERMEDIATE_PATTERNS:
        if re.search(pattern, query_lower):
            return DifficultyResult(
                level=DifficultyLevel.INTERMEDIATE,
                confidence=0.85,
                method="heuristic",
                distances=None,
            )

    # Check INTERMEDIATE keywords
    for keyword in INTERMEDIATE_KEYWORDS:
        if keyword in query_lower:
            return DifficultyResult(
                level=DifficultyLevel.INTERMEDIATE,
                confidence=0.80,
                method="heuristic",
                distances=None,
            )

    # Check BASIC patterns
    for pattern in BASIC_PATTERNS:
        if re.search(pattern, query_lower):
            return DifficultyResult(
                level=DifficultyLevel.BASIC,
                confidence=0.85,
                method="heuristic",
                distances=None,
            )

    # Check BASIC keywords
    for keyword in BASIC_KEYWORDS:
        if keyword in query_lower:
            return DifficultyResult(
                level=DifficultyLevel.BASIC,
                confidence=0.80,
                method="heuristic",
                distances=None,
            )

    # No clear pattern matched
    return None


class DifficultyClassifier:
    """
    Question difficulty classifier using embeddings and clustering.

    The classifier uses pre-trained centroids for each difficulty level.
    Classification is done by computing the distance from the query embedding
    to each centroid and selecting the closest one.

    Attributes:
        centroids: Dictionary mapping DifficultyLevel to centroid vectors
        embedding_dim: Dimension of embedding vectors (default: 768 for nomic-embed-text)
        use_heuristics: Whether to try heuristic classification first
    """

    def __init__(
        self,
        centroids_path: str | Path | None = None,
        embedding_dim: int = 768,
        use_heuristics: bool = True,
    ):
        """
        Initialize the difficulty classifier.

        Args:
            centroids_path: Path to JSON file with pre-trained centroids.
                           If None, uses default centroids or requires training.
            embedding_dim: Dimension of embedding vectors
            use_heuristics: Whether to try fast heuristic classification first
        """
        self.embedding_dim = embedding_dim
        self.use_heuristics = use_heuristics
        self.centroids: dict[DifficultyLevel, np.ndarray] | None = None

        if centroids_path:
            self.load_centroids(centroids_path)

    def load_centroids(self, path: str | Path) -> None:
        """
        Load pre-trained centroids from a JSON file.

        Args:
            path: Path to the centroids file

        File format:
            {
                "basic": [0.1, 0.2, ...],
                "intermediate": [0.3, 0.4, ...],
                "advanced": [0.5, 0.6, ...]
            }
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Centroids file not found: {path}")

        with open(path) as f:
            data = json.load(f)

        self.centroids = {}
        for level in DifficultyLevel:
            if level.value in data:
                centroid = np.array(data[level.value])
                if len(centroid) != self.embedding_dim:
                    raise ValueError(
                        f"Centroid dimension mismatch for {level.value}: "
                        f"expected {self.embedding_dim}, got {len(centroid)}"
                    )
                self.centroids[level] = centroid
            else:
                logger.warning(f"Missing centroid for level: {level.value}")

        logger.info(
            f"Loaded centroids from {path} for levels: {list(self.centroids.keys())}"
        )

    def save_centroids(self, path: str | Path) -> None:
        """
        Save trained centroids to a JSON file.

        Args:
            path: Path to save the centroids
        """
        if not self.centroids:
            raise ValueError("No centroids to save. Train the classifier first.")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            level.value: centroid.tolist() for level, centroid in self.centroids.items()
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved centroids to {path}")

    def classify_embedding(
        self, embedding: list[float] | np.ndarray
    ) -> DifficultyResult:
        """
        Classify difficulty based on embedding distance to centroids.

        Uses Euclidean distance to find the nearest centroid.
        Confidence is computed using softmax over negative distances.

        Args:
            embedding: The query embedding vector

        Returns:
            DifficultyResult with level, confidence, and distances

        Raises:
            ValueError: If centroids are not loaded/trained
        """
        if not self.centroids:
            raise ValueError("Centroids not loaded. Load or train centroids first.")

        embedding = np.array(embedding)
        if len(embedding) != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dim}, got {len(embedding)}"
            )

        # Compute distances to each centroid
        distances: dict[str, float] = {}
        for level, centroid in self.centroids.items():
            dist = float(np.linalg.norm(embedding - centroid))
            distances[level.value] = dist

        # Find nearest centroid
        min_level = min(distances, key=distances.get)  # type: ignore
        predicted_level = DifficultyLevel(min_level)

        # Compute confidence using softmax over negative distances
        # (closer = higher confidence)
        dist_values = np.array(list(distances.values()))
        neg_distances = -dist_values
        # Softmax with temperature for smoother probabilities
        temperature = 0.5
        exp_neg = np.exp(neg_distances / temperature)
        softmax_probs = exp_neg / exp_neg.sum()

        # Get confidence for predicted level
        level_names = list(distances.keys())
        predicted_idx = level_names.index(min_level)
        confidence = float(softmax_probs[predicted_idx])

        return DifficultyResult(
            level=predicted_level,
            confidence=confidence,
            method="embedding",
            distances=distances,
        )

    def classify_text(
        self,
        text: str,
        embedding: list[float] | np.ndarray | None = None,
    ) -> DifficultyResult:
        """
        Classify difficulty of a question text.

        First tries heuristic classification (if enabled), then falls back
        to embedding-based classification.

        Args:
            text: The question text to classify
            embedding: Pre-computed embedding (optional, computed if needed)

        Returns:
            DifficultyResult with classification details
        """
        # Try heuristic classification first (fast)
        if self.use_heuristics:
            heuristic_result = _heuristic_classify(text)
            if heuristic_result:
                logger.debug(
                    f"Heuristic classification: {heuristic_result.level.value} "
                    f"(confidence: {heuristic_result.confidence:.2f})"
                )
                return heuristic_result

        # Fall back to embedding-based classification
        if embedding is not None:
            return self.classify_embedding(embedding)

        # No embedding provided and no centroids - use length heuristic
        if not self.centroids:
            logger.warning("No centroids loaded, using length-based heuristic")
            text_len = len(text)
            if text_len < 50:
                level = DifficultyLevel.BASIC
            elif text_len < 120:
                level = DifficultyLevel.INTERMEDIATE
            else:
                level = DifficultyLevel.ADVANCED

            return DifficultyResult(
                level=level,
                confidence=0.5,
                method="length_heuristic",
                distances=None,
            )

        raise ValueError(
            "Embedding required for classification when heuristics don't match. "
            "Provide an embedding or enable heuristics."
        )

    def train(
        self,
        labeled_data: list[tuple[np.ndarray, DifficultyLevel]],
    ) -> dict[str, Any]:
        """
        Train centroids from labeled embeddings using K-Means.

        Args:
            labeled_data: List of (embedding, difficulty_level) tuples

        Returns:
            Training metrics including cluster sizes and inertia
        """
        # Group embeddings by difficulty level
        embeddings_by_level: dict[DifficultyLevel, list[np.ndarray]] = {
            level: [] for level in DifficultyLevel
        }

        for embedding, level in labeled_data:
            embeddings_by_level[level].append(embedding)

        # Compute centroids as mean of each group
        self.centroids = {}
        metrics: dict[str, Any] = {"cluster_sizes": {}, "centroids_computed": []}

        for level in DifficultyLevel:
            level_embeddings = embeddings_by_level[level]
            if not level_embeddings:
                logger.warning(f"No samples for level {level.value}, skipping")
                continue

            embeddings_array = np.array(level_embeddings)
            centroid = embeddings_array.mean(axis=0)
            self.centroids[level] = centroid

            metrics["cluster_sizes"][level.value] = len(level_embeddings)
            metrics["centroids_computed"].append(level.value)

            logger.info(
                f"Computed centroid for {level.value} from {len(level_embeddings)} samples"
            )

        logger.info(f"Training complete. Centroids: {list(self.centroids.keys())}")
        return metrics


# =============================================================================
# Convenience Functions
# =============================================================================

# Global classifier instance (lazy initialization)
_classifier: DifficultyClassifier | None = None


def get_difficulty_classifier(
    centroids_path: str | Path | None = None,
) -> DifficultyClassifier:
    """
    Get or create the global difficulty classifier instance.

    Args:
        centroids_path: Optional path to centroids file

    Returns:
        Configured DifficultyClassifier instance
    """
    global _classifier
    if _classifier is None:
        _classifier = DifficultyClassifier(centroids_path=centroids_path)
    return _classifier


def classify_difficulty(
    text: str,
    embedding: list[float] | np.ndarray | None = None,
) -> DifficultyLevel:
    """
    Convenience function to classify question difficulty.

    Args:
        text: The question text
        embedding: Optional pre-computed embedding

    Returns:
        DifficultyLevel enum value
    """
    classifier = get_difficulty_classifier()
    result = classifier.classify_text(text, embedding)
    return result.level


def classify_difficulty_detailed(
    text: str,
    embedding: list[float] | np.ndarray | None = None,
) -> DifficultyResult:
    """
    Convenience function to get detailed classification result.

    Args:
        text: The question text
        embedding: Optional pre-computed embedding

    Returns:
        DifficultyResult with level, confidence, method, and distances
    """
    classifier = get_difficulty_classifier()
    return classifier.classify_text(text, embedding)


# =============================================================================
# Embedding Helper Functions
# =============================================================================

# Global Ollama embeddings instance for local use
_ollama_embeddings = None


def _get_ollama_embeddings():
    """Get or create Ollama embeddings instance for local embedding generation."""
    global _ollama_embeddings
    if _ollama_embeddings is None:
        import os

        from langchain_ollama import OllamaEmbeddings

        # Use environment variables or defaults for local development
        # Default to localhost:11435 (typical host-mapped port for Ollama container)
        ollama_host = os.environ.get("OLLAMA_HOST", "localhost")
        ollama_port = os.environ.get("OLLAMA_PORT", "11435")
        ollama_model = os.environ.get("OLLAMA_MODEL", "nomic-embed-text")

        ollama_url = f"http://{ollama_host}:{ollama_port}"
        logger.info(
            f"Initializing Ollama embeddings at {ollama_url} with model {ollama_model}"
        )

        _ollama_embeddings = OllamaEmbeddings(
            base_url=ollama_url,
            model=ollama_model,
        )
    return _ollama_embeddings


def get_embedding_from_ollama(text: str) -> list[float]:
    """
    Get embedding directly from Ollama (local or containerized).

    This is the preferred method when running outside of containers.

    Args:
        text: Text to embed

    Returns:
        Embedding vector as list of floats
    """
    embeddings = _get_ollama_embeddings()
    return embeddings.embed_query(text)


def get_embeddings_batch_ollama(texts: list[str]) -> list[list[float]]:
    """
    Get embeddings for multiple texts directly from Ollama.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    embeddings = _get_ollama_embeddings()
    return embeddings.embed_documents(texts)


def get_embedding_from_rag_service(text: str) -> list[float]:
    """
    Get embedding from the RAG service.

    Makes an HTTP call to the RAG service's embed endpoint.
    Falls back to Ollama if RAG service is unavailable.

    Args:
        text: Text to embed

    Returns:
        Embedding vector as list of floats

    Raises:
        RuntimeError: If both RAG service and Ollama fail
    """
    rag_url = settings.rag_service_url
    endpoint = f"{rag_url}/embed"

    try:
        response = requests.post(
            endpoint,
            json={"text": text},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]
    except requests.RequestException as e:
        logger.warning(f"RAG service unavailable, falling back to Ollama: {e}")
        try:
            return get_embedding_from_ollama(text)
        except Exception as ollama_error:
            logger.error(f"Ollama embedding also failed: {ollama_error}")
            raise RuntimeError(
                f"All embedding methods failed: {e}, {ollama_error}"
            ) from e


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Get embeddings for multiple texts from the RAG service.
    Falls back to Ollama if RAG service is unavailable.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors

    Raises:
        RuntimeError: If both RAG service and Ollama fail
    """
    rag_url = settings.rag_service_url
    endpoint = f"{rag_url}/embed/batch"

    try:
        response = requests.post(
            endpoint,
            json={"texts": texts},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["embeddings"]
    except requests.RequestException as e:
        logger.warning(f"RAG service unavailable, falling back to Ollama: {e}")
        try:
            return get_embeddings_batch_ollama(texts)
        except Exception as ollama_error:
            logger.error(f"Ollama batch embedding also failed: {ollama_error}")
            raise RuntimeError(
                f"All embedding methods failed: {e}, {ollama_error}"
            ) from e
