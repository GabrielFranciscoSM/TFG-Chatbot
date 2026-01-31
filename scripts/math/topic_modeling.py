#!/usr/bin/env python3
"""
Topic Modeling with manually implemented TF-IDF and NMF.

This script implements topic discovery from scratch for academic demonstration,
showing mathematical understanding of TF-IDF vectorization and NMF decomposition.
"""

import argparse
import json
import logging
import re
import string
from collections import Counter
from pathlib import Path

import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Common English stopwords
STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "as",
    "is",
    "was",
    "are",
    "were",
    "been",
    "be",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "i",
    "you",
    "he",
    "she",
    "we",
    "they",
    "what",
    "which",
    "who",
    "whom",
    "where",
    "when",
    "why",
    "how",
    "all",
    "each",
    "every",
    "both",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "not",
    "only",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "also",
    "into",
    "over",
    "after",
    "before",
    "between",
    "through",
    "during",
    "above",
    "below",
    "up",
    "down",
    "out",
    "off",
    "about",
    "against",
    "further",
    "then",
    "once",
    "here",
    "there",
    "any",
    "own",
    "being",
    "their",
    "them",
}


class TFIDFVectorizer:
    """Manual TF-IDF implementation for academic demonstration.

    TF-IDF = Term Frequency × Inverse Document Frequency

    TF(t,d) = count(t,d) / len(d)
    IDF(t) = log(N / (1 + df(t)))
    """

    def __init__(self, max_features: int = 1000, min_df: int = 2):
        """Initialize TF-IDF vectorizer.

        Args:
            max_features: Maximum vocabulary size
            min_df: Minimum document frequency for a term
        """
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_: dict[str, int] = {}
        self.idf_: np.ndarray | None = None
        self.feature_names_: list[str] = []

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize and normalize text.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        # Lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))

        # Split into words
        tokens = re.findall(r"\b[a-z]{2,}\b", text)

        # Remove stopwords
        tokens = [t for t in tokens if t not in STOPWORDS]

        return tokens

    def _build_vocabulary(self, tokenized_docs: list[list[str]]) -> None:
        """Build vocabulary from tokenized documents.

        Args:
            tokenized_docs: List of tokenized documents
        """
        # Count document frequency for each term
        df_counts: Counter = Counter()
        for doc in tokenized_docs:
            unique_terms = set(doc)
            df_counts.update(unique_terms)

        # Filter by min_df and sort by frequency
        filtered_terms = [
            (term, count) for term, count in df_counts.items() if count >= self.min_df
        ]
        filtered_terms.sort(key=lambda x: x[1], reverse=True)

        # Take top max_features
        top_terms = filtered_terms[: self.max_features]

        # Build vocabulary mapping
        self.vocabulary_ = {term: idx for idx, (term, _) in enumerate(top_terms)}
        self.feature_names_ = [term for term, _ in top_terms]

        logger.info(f"Vocabulary size: {len(self.vocabulary_)}")

    def _compute_tf(self, tokens: list[str]) -> np.ndarray:
        """Compute Term Frequency for a document.

        TF(t,d) = count(t,d) / len(d)

        Args:
            tokens: List of tokens in document

        Returns:
            TF vector
        """
        tf = np.zeros(len(self.vocabulary_))

        if not tokens:
            return tf

        token_counts = Counter(tokens)
        doc_len = len(tokens)

        for term, count in token_counts.items():
            if term in self.vocabulary_:
                idx = self.vocabulary_[term]
                tf[idx] = count / doc_len

        return tf

    def _compute_idf(self, tokenized_docs: list[list[str]]) -> np.ndarray:
        """Compute Inverse Document Frequency.

        IDF(t) = log(N / (1 + df(t)))

        Args:
            tokenized_docs: List of tokenized documents

        Returns:
            IDF vector
        """
        n_docs = len(tokenized_docs)
        idf = np.zeros(len(self.vocabulary_))

        # Count document frequency for vocabulary terms
        df = np.zeros(len(self.vocabulary_))
        for doc in tokenized_docs:
            unique_terms = set(doc)
            for term in unique_terms:
                if term in self.vocabulary_:
                    df[self.vocabulary_[term]] += 1

        # Compute IDF with smoothing
        idf = np.log(n_docs / (1 + df))

        return idf

    def fit_transform(self, documents: list[str]) -> np.ndarray:
        """Fit vocabulary and transform documents to TF-IDF matrix.

        Args:
            documents: List of document strings

        Returns:
            TF-IDF matrix of shape (n_docs, n_features)
        """
        # Tokenize all documents
        tokenized_docs = [self._tokenize(doc) for doc in documents]

        # Build vocabulary
        self._build_vocabulary(tokenized_docs)

        # Compute IDF
        self.idf_ = self._compute_idf(tokenized_docs)

        # Compute TF-IDF for each document
        n_docs = len(documents)
        n_features = len(self.vocabulary_)
        tfidf_matrix = np.zeros((n_docs, n_features))

        for i, tokens in enumerate(tokenized_docs):
            tf = self._compute_tf(tokens)
            tfidf_matrix[i] = tf * self.idf_

        logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

        return tfidf_matrix

    def get_feature_names(self) -> list[str]:
        """Get feature names (vocabulary terms)."""
        return self.feature_names_


class NMF:
    """Non-negative Matrix Factorization using multiplicative update rules.

    Decomposes V ≈ W @ H where:
    - V: input matrix (m × n) - document-term matrix
    - W: basis matrix (m × k) - document-topic affinities
    - H: coefficient matrix (k × n) - topic-term distributions

    Supports two cost functions:
    - Frobenius: ||V - WH||²_F
    - KL-divergence: D_KL(V || WH)

    Reference: Lee & Seung (2001) "Algorithms for NMF"
    """

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
        """Initialize W and H matrices with random non-negative values.

        Args:
            V: Input matrix

        Returns:
            Tuple of (W, H) matrices
        """
        if self.random_state is not None:
            np.random.seed(self.random_state)

        m, n = V.shape
        k = self.n_components

        # Initialize with small positive values
        # Scale by sqrt(mean(V)) for better convergence
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
        """Multiplicative update for KL-divergence.

        D_KL(V || WH) = Σ(V_ij log(V_ij / (WH)_ij) - V_ij + (WH)_ij)

        H_ij ← H_ij × Σ_k(W_ki × V_ij / (WH)_ij) / Σ_k W_ki
        W_ij ← W_ij × Σ_l(H_jl × V_il / (WH)_il) / Σ_l H_jl
        """
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
        """Compute reconstruction error based on cost function.

        Frobenius: ||V - WH||²_F
        KL: D_KL(V || WH)
        """
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


class CoherenceScorer:
    """Manual implementation of topic coherence metrics.

    Implements UCI and UMass coherence for academic demonstration.
    """

    def __init__(self, vectorizer: TFIDFVectorizer):
        """Initialize coherence scorer.

        Args:
            vectorizer: Fitted TFIDFVectorizer for vocabulary access
        """
        self.vectorizer = vectorizer
        self.vocab = set(vectorizer.get_feature_names())

    def uci_coherence(
        self,
        topics: dict[int, list[str]],
        documents: list[str],
        window_size: int = 10,
    ) -> dict[int, float]:
        """Compute UCI coherence using sliding window co-occurrence.

        C_UCI = (2 / (n*(n-1))) * Σ log((P(w_i, w_j) + ε) / (P(w_i) * P(w_j)))

        Args:
            topics: Dictionary of topic_idx -> top words
            documents: Original documents for co-occurrence
            window_size: Sliding window size

        Returns:
            Dictionary of topic_idx -> coherence score
        """
        # Build co-occurrence counts from sliding windows
        word_counts: Counter = Counter()
        pair_counts: Counter = Counter()
        total_windows = 0

        for doc in documents:
            tokens = self.vectorizer._tokenize(doc)
            # Sliding window
            for i in range(len(tokens) - window_size + 1):
                window = tokens[i : i + window_size]
                unique_words = set(window) & self.vocab

                for word in unique_words:
                    word_counts[word] += 1

                for w1 in unique_words:
                    for w2 in unique_words:
                        if w1 < w2:  # Avoid duplicates
                            pair_counts[(w1, w2)] += 1

                total_windows += 1

        if total_windows == 0:
            return dict.fromkeys(topics, 0.0)

        # Compute coherence for each topic
        coherence_scores = {}
        eps = 1e-10

        for topic_idx, words in topics.items():
            words_in_vocab = [w for w in words if w in self.vocab]
            n = len(words_in_vocab)

            if n < 2:
                coherence_scores[topic_idx] = 0.0
                continue

            pmi_sum = 0.0
            pairs = 0

            for i, w1 in enumerate(words_in_vocab):
                for w2 in words_in_vocab[i + 1 :]:
                    p_w1 = word_counts[w1] / total_windows
                    p_w2 = word_counts[w2] / total_windows

                    pair_key = tuple(sorted([w1, w2]))
                    p_w1w2 = pair_counts[pair_key] / total_windows

                    # Pointwise mutual information
                    pmi = np.log((p_w1w2 + eps) / (p_w1 * p_w2 + eps))
                    pmi_sum += pmi
                    pairs += 1

            coherence_scores[topic_idx] = pmi_sum / pairs if pairs > 0 else 0.0

        return coherence_scores

    def umass_coherence(
        self,
        topics: dict[int, list[str]],
        doc_term_matrix: np.ndarray,
    ) -> dict[int, float]:
        """Compute UMass coherence using document co-occurrence.

        C_UMass = (2 / (n*(n-1))) * Σ log((D(w_i, w_j) + 1) / D(w_i))

        Args:
            topics: Dictionary of topic_idx -> top words
            doc_term_matrix: Document-term matrix (binary presence)

        Returns:
            Dictionary of topic_idx -> coherence score
        """
        vocab_list = self.vectorizer.get_feature_names()
        vocab_to_idx = {w: i for i, w in enumerate(vocab_list)}

        # Convert to binary presence
        binary_matrix = (doc_term_matrix > 0).astype(int)

        # Document frequency
        doc_freq = binary_matrix.sum(axis=0)

        coherence_scores = {}

        for topic_idx, words in topics.items():
            n = len(words)
            if n < 2:
                coherence_scores[topic_idx] = 0.0
                continue

            score_sum = 0.0
            pairs = 0

            for i, w1 in enumerate(words):
                if w1 not in vocab_to_idx:
                    continue
                idx1 = vocab_to_idx[w1]

                for w2 in words[i + 1 :]:
                    if w2 not in vocab_to_idx:
                        continue
                    idx2 = vocab_to_idx[w2]

                    # D(w2) - documents containing w2
                    d_w2 = doc_freq[idx2]

                    # D(w1, w2) - documents containing both
                    d_w1_w2 = np.sum(binary_matrix[:, idx1] * binary_matrix[:, idx2])

                    # UMass score
                    score = np.log((d_w1_w2 + 1) / (d_w2 + 1e-10))
                    score_sum += score
                    pairs += 1

            coherence_scores[topic_idx] = score_sum / pairs if pairs > 0 else 0.0

        return coherence_scores


class TopicModeler:
    """Complete topic modeling pipeline using TF-IDF + NMF."""

    def __init__(
        self,
        n_components: int = 5,
        max_features: int = 1000,
        max_iter: int = 200,
        random_state: int = 42,
        cost: str = "frobenius",
    ):
        """Initialize topic modeler.

        Args:
            n_components: Number of topics
            max_features: Maximum vocabulary size
            max_iter: Maximum NMF iterations
            random_state: Random seed
            cost: NMF cost function ('frobenius' or 'kl')
        """
        self.vectorizer = TFIDFVectorizer(max_features=max_features)
        self.nmf = NMF(
            n_components=n_components,
            max_iter=max_iter,
            random_state=random_state,
            cost=cost,
        )
        self.coherence_scorer: CoherenceScorer | None = None
        self.tfidf_matrix_: np.ndarray | None = None
        self.documents_: list[str] | None = None

    def fit(self, documents: list[str]) -> None:
        """Fit topic model to documents.

        Args:
            documents: List of document texts
        """
        logger.info(f"Fitting topic model on {len(documents)} documents")

        # Store documents for coherence calculation
        self.documents_ = documents

        # Step 1: TF-IDF vectorization
        self.tfidf_matrix_ = self.vectorizer.fit_transform(documents)

        # Step 2: Initialize coherence scorer
        self.coherence_scorer = CoherenceScorer(self.vectorizer)

        # Step 3: NMF decomposition
        self.nmf.fit(self.tfidf_matrix_)

    def get_topics(self, n_words: int = 10) -> dict[int, list[str]]:
        """Extract top words for each topic.

        Args:
            n_words: Number of top words per topic

        Returns:
            Dictionary mapping topic index to list of top words
        """
        if self.nmf.H_ is None:
            raise ValueError("Model not fitted. Call fit() first.")

        feature_names = self.vectorizer.get_feature_names()
        topics = {}

        for topic_idx, topic_vec in enumerate(self.nmf.H_):
            # Get indices of top words
            top_indices = topic_vec.argsort()[-n_words:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            topics[topic_idx] = top_words

        return topics

    def get_document_topics(self) -> np.ndarray:
        """Get dominant topic for each document.

        Returns:
            Array of topic indices for each document
        """
        if self.nmf.W_ is None:
            raise ValueError("Model not fitted. Call fit() first.")

        return np.argmax(self.nmf.W_, axis=1)

    def compute_coherence(self, n_words: int = 10) -> dict:
        """Compute coherence metrics for extracted topics.

        Args:
            n_words: Number of top words per topic for coherence

        Returns:
            Dictionary with UCI and UMass coherence per topic
        """
        if self.coherence_scorer is None or self.documents_ is None:
            raise ValueError("Model not fitted. Call fit() first.")

        topics = self.get_topics(n_words=n_words)

        uci_scores = self.coherence_scorer.uci_coherence(topics, self.documents_)
        umass_scores = self.coherence_scorer.umass_coherence(topics, self.tfidf_matrix_)

        return {
            "uci": uci_scores,
            "umass": umass_scores,
            "avg_uci": np.mean(list(uci_scores.values())),
            "avg_umass": np.mean(list(umass_scores.values())),
        }

    def evaluate(self, true_labels: list[str], compute_coherence: bool = True) -> dict:
        """Evaluate topic model against ground truth labels.

        Args:
            true_labels: List of true topic labels
            compute_coherence: Whether to compute coherence metrics

        Returns:
            Evaluation metrics
        """
        predicted_topics = self.get_document_topics()

        # Map predicted clusters to true labels (majority voting)
        unique_labels = list(set(true_labels))
        label_to_int = {label: i for i, label in enumerate(unique_labels)}
        true_int = np.array([label_to_int[label] for label in true_labels])

        # Compute purity (simple metric)
        contingency = np.zeros((self.nmf.n_components, len(unique_labels)))
        for pred, true in zip(predicted_topics, true_int, strict=True):
            contingency[pred, true] += 1

        # Purity = sum of max in each cluster / total
        purity = np.sum(np.max(contingency, axis=1)) / len(true_labels)

        result = {
            "n_topics": self.nmf.n_components,
            "n_documents": len(true_labels),
            "n_unique_labels": len(unique_labels),
            "purity": purity,
            "cost_function": self.nmf.cost,
            "final_reconstruction_error": self.nmf.reconstruction_errors_[-1],
        }

        # Add coherence metrics
        if compute_coherence:
            coherence = self.compute_coherence()
            result["avg_uci_coherence"] = coherence["avg_uci"]
            result["avg_umass_coherence"] = coherence["avg_umass"]

        return result


def load_dataset(path: str) -> tuple[list[str], list[str]]:
    """Load synthetic dataset.

    Args:
        path: Path to JSON dataset

    Returns:
        Tuple of (documents, labels)
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    documents = [item["text"] for item in data]
    labels = [item.get("label", "Unknown") for item in data]

    return documents, labels


def main():
    parser = argparse.ArgumentParser(
        description="Topic Modeling with manual TF-IDF and NMF implementations."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/synthetic_dataset.json",
        help="Path to input dataset",
    )
    parser.add_argument(
        "--n-topics",
        type=int,
        nargs="+",
        default=[3, 5, 10],
        help="Number of topics to test",
    )
    parser.add_argument(
        "--max-features",
        type=int,
        default=500,
        help="Maximum vocabulary size",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=200,
        help="Maximum NMF iterations",
    )
    parser.add_argument(
        "--top-words",
        type=int,
        default=10,
        help="Number of top words per topic to display",
    )
    parser.add_argument(
        "--cost",
        type=str,
        choices=["frobenius", "kl"],
        default="frobenius",
        help="NMF cost function: frobenius or kl (KL-divergence)",
    )
    parser.add_argument(
        "--coherence",
        action="store_true",
        help="Compute and display coherence metrics (UCI, UMass)",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run with fewer documents for testing",
    )

    args = parser.parse_args()

    # Load dataset
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Dataset not found: {input_path}")
        return

    documents, labels = load_dataset(args.input)

    if args.test_mode:
        # Use first 50 documents for quick testing
        documents = documents[:50]
        labels = labels[:50]
        logger.info("Running in TEST MODE with 50 documents")

    logger.info(f"Loaded {len(documents)} documents")
    logger.info(f"Using cost function: {args.cost}")

    # Test different numbers of topics
    for k in args.n_topics:
        print(f"\n{'='*60}")
        print(f"Topic Modeling with k={k} topics (cost: {args.cost})")
        print("=" * 60)

        modeler = TopicModeler(
            n_components=k,
            max_features=args.max_features,
            max_iter=args.max_iter,
            cost=args.cost,
        )

        modeler.fit(documents)

        # Print topics
        topics = modeler.get_topics(n_words=args.top_words)
        print(f"\nExtracted Topics (top {args.top_words} words):")
        for topic_idx, words in topics.items():
            print(f"  Topic {topic_idx}: {', '.join(words)}")

        # Evaluate
        metrics = modeler.evaluate(labels, compute_coherence=args.coherence)
        print("\nMetrics:")
        print(f"  Cost Function: {metrics['cost_function']}")
        print(f"  Purity: {metrics['purity']:.4f}")
        print(f"  Reconstruction Error: {metrics['final_reconstruction_error']:.4f}")

        if args.coherence:
            print(f"  Avg UCI Coherence: {metrics['avg_uci_coherence']:.4f}")
            print(f"  Avg UMass Coherence: {metrics['avg_umass_coherence']:.4f}")


if __name__ == "__main__":
    main()
