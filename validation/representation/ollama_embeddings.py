"""Embedding generation using Ollama Nomic model."""

import logging

import httpx
import numpy as np

logger = logging.getLogger(__name__)


class OllamaEmbeddings:
    """Generate embeddings using Ollama's nomic-embed-text model.

    Nomic embeddings default to 768 dimensions for semantic text representation.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        host: str = "172.19.80.1",
        port: int = 11434,
        timeout: float = 30.0,
    ):
        """Initialize Ollama embeddings client.

        Args:
            model: Ollama model name (default: nomic-embed-text)
            host: Ollama server host (default: localhost)
            port: Ollama server port (default: 11434)
            timeout: Request timeout in seconds
        """
        self.model = model
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        logger.info(f"Initialized Ollama embeddings: {self.base_url}/api/embeddings")

    def embed(self, text: str, normalize: bool = True) -> np.ndarray:
        """Generate embedding for a single text.

        Args:
            text: Input text to embed
            normalize: Whether to L2 normalize the embedding

        Returns:
            Normalized embedding vector of shape (768,)

        Raises:
            ConnectionError: If Ollama is unreachable
            ValueError: If Ollama returns an error
        """
        if not text or not text.strip():
            return np.zeros(768)

        try:
            resp = httpx.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            embedding = np.array(resp.json()["embedding"], dtype=np.float32)

            if normalize:
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm

            return embedding

        except httpx.RequestError as e:
            logger.error(f"Connection error to Ollama: {e}")
            raise ConnectionError(f"Ollama unavailable at {self.base_url}") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama error: {e.response.status_code} {e.response.text}")
            raise ValueError(f"Ollama request failed: {e}") from e

    def embed_batch(self, texts: list[str], normalize: bool = True) -> np.ndarray:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            normalize: Whether to L2 normalize each embedding

        Returns:
            Matrix of shape (len(texts), 768)
        """
        embeddings = []
        for text in texts:
            embedding = self.embed(text, normalize=normalize)
            embeddings.append(embedding)

        matrix = np.vstack(embeddings) if embeddings else np.zeros((len(texts), 768))
        logger.info(f"Generated embeddings matrix: {matrix.shape}")
        return matrix
