"""Ollama embeddings using nomic-embed-text model."""

import json
import logging

import numpy as np

logger = logging.getLogger(__name__)


class OllamaEmbeddings:
    """Embeddings using Ollama API with nomic-embed-text model.

    This provides dense semantic embeddings (768 dimensions) as an alternative
    to sparse TF-IDF/BoW representations.

    Requires Ollama running locally with nomic-embed-text model.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11435",
        batch_size: int = 10,
    ):
        """Initialize Ollama embeddings.

        Args:
            model: Ollama embedding model name
            base_url: Ollama API base URL
            batch_size: Number of documents to process per batch
        """
        self.model = model
        self.base_url = base_url
        self.batch_size = batch_size
        self.embedding_dim = 768  # nomic-embed-text dimension

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text using Ollama API."""
        import urllib.error
        import urllib.request

        url = f"{self.base_url}/api/embeddings"
        payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return np.array(result["embedding"])
        except urllib.error.URLError as e:
            logger.error(f"Failed to get embedding: {e}")
            raise

    def fit_transform(self, documents: list[str]) -> np.ndarray:
        """Transform documents to embedding matrix.

        Returns:
            Embedding matrix of shape (n_docs, 768), L2 normalized
        """
        n_docs = len(documents)
        embeddings = np.zeros((n_docs, self.embedding_dim))

        logger.info(
            f"Generating embeddings for {n_docs} documents with {self.model}..."
        )

        for i, doc in enumerate(documents):
            if (i + 1) % 50 == 0:
                logger.info(f"  Processed {i + 1}/{n_docs} documents")

            try:
                embeddings[i] = self._get_embedding(doc)
            except Exception as e:
                logger.warning(f"Failed to get embedding for doc {i}: {e}")
                # Use zero vector as fallback
                embeddings[i] = np.zeros(self.embedding_dim)

        # L2 normalize for clustering
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        embeddings = embeddings / norms

        logger.info(f"Embeddings matrix shape: {embeddings.shape}")
        return embeddings
