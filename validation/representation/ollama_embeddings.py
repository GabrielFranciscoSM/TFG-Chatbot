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
        host: str = "localhost",
        port: int = 11434,
        timeout: float = 30.0,
        max_input_tokens: int = 512,
        chunk_overlap_tokens: int = 64,
    ):
        """Initialize Ollama embeddings client.

        Args:
            model: Ollama model name (default: nomic-embed-text)
            host: Ollama server host (default: localhost)
            port: Ollama server port (default: 11434)
            timeout: Request timeout in seconds
            max_input_tokens: Max approximate tokens per embedding request
            chunk_overlap_tokens: Token overlap between consecutive chunks
        """
        self.model = model
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.max_input_tokens = max(32, int(max_input_tokens))
        self.chunk_overlap_tokens = max(0, int(chunk_overlap_tokens))
        logger.info(f"Initialized Ollama embeddings: {self.base_url}/api/embeddings")

    def _token_chunks(self, text: str) -> list[tuple[str, int]]:
        """Split text into approximate-token chunks with overlap.

        We use whitespace tokenization as a lightweight approximation to avoid
        exceeding model context limits on very long inputs.
        """
        tokens = text.split()
        if not tokens:
            return []

        max_tokens = self.max_input_tokens
        overlap = min(self.chunk_overlap_tokens, max_tokens // 2)
        step = max(1, max_tokens - overlap)

        chunks: list[tuple[str, int]] = []
        for start in range(0, len(tokens), step):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            if not chunk_tokens:
                continue
            chunks.append((" ".join(chunk_tokens), len(chunk_tokens)))
            if end >= len(tokens):
                break
        return chunks

    def _embed_request(self, prompt: str) -> np.ndarray:
        """Send a single embedding request to Ollama."""
        resp = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": prompt},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return np.array(resp.json()["embedding"], dtype=np.float32)

    def _is_context_length_error(self, exc: httpx.HTTPStatusError) -> bool:
        """Detect Ollama errors caused by prompt length exceeding model context."""
        return (
            exc.response.status_code == 500
            and "context length" in exc.response.text.lower()
        )

    def _embed_tokens_with_fallback(self, tokens: list[str]) -> np.ndarray:
        """Embed token span; on context overflow, split recursively and pool."""
        if not tokens:
            return np.zeros(768, dtype=np.float32)

        prompt = " ".join(tokens)
        try:
            return self._embed_request(prompt)
        except httpx.HTTPStatusError as exc:
            if self._is_context_length_error(exc) and len(tokens) > 1:
                mid = len(tokens) // 2
                left_tokens = tokens[:mid]
                right_tokens = tokens[mid:]

                left_embedding = self._embed_tokens_with_fallback(left_tokens)
                right_embedding = self._embed_tokens_with_fallback(right_tokens)

                left_weight = float(len(left_tokens))
                right_weight = float(len(right_tokens))
                total_weight = left_weight + right_weight
                return (
                    (left_embedding * left_weight) + (right_embedding * right_weight)
                ) / total_weight
            raise

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
            return np.zeros(768, dtype=np.float32)

        try:
            tokens = text.split()
            token_count = len(tokens)

            if token_count <= self.max_input_tokens:
                try:
                    embedding = self._embed_request(text)
                except httpx.HTTPStatusError as exc:
                    if self._is_context_length_error(exc):
                        embedding = self._embed_tokens_with_fallback(tokens)
                    else:
                        raise
            else:
                chunks = self._token_chunks(text)
                if not chunks:
                    return np.zeros(768, dtype=np.float32)

                weighted_sum = None
                total_weight = 0.0
                for chunk_text, chunk_weight in chunks:
                    chunk_tokens = chunk_text.split()
                    chunk_embedding = self._embed_tokens_with_fallback(chunk_tokens)
                    if weighted_sum is None:
                        weighted_sum = np.zeros_like(chunk_embedding, dtype=np.float32)
                    weighted_sum += chunk_embedding * float(chunk_weight)
                    total_weight += float(chunk_weight)

                if weighted_sum is None or total_weight == 0:
                    return np.zeros(768, dtype=np.float32)

                embedding = weighted_sum / total_weight

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
