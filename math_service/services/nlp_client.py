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
            raise ConnectionError(f"Ollama embedding failed: {e}") from e

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


class MistralClient:
    """Client for interacting with Mistral API."""

    def __init__(self):
        """Initialize configurations."""
        self.api_key = (
            settings.mistral_api_key.get_secret_value()
            if settings.mistral_api_key
            else None
        )
        self.model = settings.mistral_model
        self.base_url = "https://api.mistral.ai/v1"

    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt using Mistral."""
        if not self.api_key:
            raise RuntimeError("Mistral API key is not configured")

        url = f"{self.base_url}/chat/completions"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 15,
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
                return ""
        except urllib.error.URLError as e:
            logger.error(f"Failed to generate text from Mistral: {e}")
            raise RuntimeError(f"Mistral text generation failed: {e}") from e
