"""Ollama NLP Client for embeddings."""

import json
import logging
import urllib.error
import urllib.request

import numpy as np

from math_service.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for fetching embeddings from Ollama."""

    def __init__(self):
        """Initialize OllamaClient using configuration."""
        self.host = settings.ollama_host
        self.port = settings.ollama_port
        self.model = settings.ollama_model

        # Determine base URL. Default to standard scheme
        # In Docker Compose, ollama resolves to the container internal IP
        if self.host.startswith("http"):
            self.base_url = f"{self.host}:{self.port}"
        else:
            self.base_url = f"http://{self.host}:{self.port}"

    def get_embedding(self, text: str) -> np.ndarray:
        """Fetch embedding for a single text."""
        url = f"{self.base_url}/api/embeddings"
        payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return np.array(result["embedding"])
        except urllib.error.URLError as e:
            logger.error(f"Ollama embedding failed for '{text[:20]}...': {e}")
            # Fallback to zeros (assuming 768 dims for nomic)
            return np.zeros(768)

    def get_embeddings_batch(self, texts: list[str]) -> np.ndarray:
        """Fetch embeddings for a batch of texts.

        Returns an (N, D) numpy array of embeddings.
        """
        if not texts:
            return np.array([])

        embeddings = []
        for i, text in enumerate(texts):
            # Log progress for large batches
            if len(texts) > 50 and (i + 1) % 50 == 0:
                logger.info(f"Fetched {i + 1}/{len(texts)} embeddings...")

            emb = self.get_embedding(text)
            embeddings.append(emb)

        # Stack into matrix and L2 normalize
        X = np.vstack(embeddings)
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        X_norm = X / norms

        return X_norm
