#!/usr/bin/env python3
"""CLI for running topic modeling experiments with NMF.

Usage:
    python -m math_investigation.cli.run_topic_modeling --k 5 --cost frobenius
    python -m math_investigation.cli.run_topic_modeling --k 5 --embeddings
"""

import argparse
import json
import logging
from pathlib import Path

import numpy as np

from math_investigation.nlp import OllamaEmbeddings, TFIDFVectorizer
from math_investigation.topic_modeling import NMF, uci_coherence, umass_coherence
from math_investigation.utils import load_synthetic_dataset
from math_investigation.visualization import (
    generate_concept_map,
    generate_document_topic_heatmap,
    generate_word_bars,
    generate_wordcloud,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TopicModeler:
    """Complete topic modeling pipeline using TF-IDF + NMF."""

    def __init__(
        self,
        n_components: int = 5,
        max_features: int = 1000,
        max_iter: int = 200,
        random_state: int = 42,
        cost: str = "frobenius",
        use_embeddings: bool = False,
    ):
        self.use_embeddings = use_embeddings
        self.vectorizer = TFIDFVectorizer(max_features=max_features)
        self.embeddings_vectorizer = OllamaEmbeddings() if use_embeddings else None
        self.nmf = NMF(
            n_components=n_components,
            max_iter=max_iter,
            random_state=random_state,
            cost=cost,
        )
        self.tfidf_matrix_: np.ndarray | None = None
        self.documents_: list[str] | None = None
        self.word_embeddings_: np.ndarray | None = None

    def fit(self, documents: list[str]) -> None:
        logger.info(f"Fitting topic model on {len(documents)} documents")
        self.documents_ = documents
        self.tfidf_matrix_ = self.vectorizer.fit_transform(documents)

        if self.use_embeddings:
            assert self.embeddings_vectorizer is not None
            V = self.embeddings_vectorizer.fit_transform(documents)
            v_min = V.min()
            if v_min < 0:
                V = V - v_min

            logger.info("Embedding vocabulary for topic interpretation...")
            feature_names = self.vectorizer.get_feature_names()
            self.word_embeddings_ = np.zeros((len(feature_names), 768))
            for i, word in enumerate(feature_names):
                try:
                    self.word_embeddings_[i] = (
                        self.embeddings_vectorizer._get_embedding(word)
                    )
                except Exception:
                    self.word_embeddings_[i] = np.zeros(768)
        else:
            V = self.tfidf_matrix_

        self.nmf.fit(V)

    def get_topics(self, n_words: int = 10) -> dict[int, list[str]]:
        if self.nmf.H_ is None:
            raise ValueError("Model not fitted.")

        feature_names = self.vectorizer.get_feature_names()
        topics = {}

        if self.use_embeddings and self.word_embeddings_ is not None:
            norms = np.linalg.norm(self.word_embeddings_, axis=1, keepdims=True)
            norms[norms == 0] = 1
            word_emb_norm = self.word_embeddings_ / norms

            for topic_idx, topic_emb in enumerate(self.nmf.H_):
                similarities = word_emb_norm @ topic_emb
                top_indices = similarities.argsort()[-n_words:][::-1]
                topics[topic_idx] = [feature_names[i] for i in top_indices]
        else:
            for topic_idx, topic_vec in enumerate(self.nmf.H_):
                top_indices = topic_vec.argsort()[-n_words:][::-1]
                topics[topic_idx] = [feature_names[i] for i in top_indices]

        return topics

    def compute_coherence(self, n_words: int = 10) -> dict:
        if self.documents_ is None or self.tfidf_matrix_ is None:
            raise ValueError("Model not fitted.")

        topics = self.get_topics(n_words=n_words)
        uci = uci_coherence(topics, self.documents_)
        umass = umass_coherence(
            topics, self.tfidf_matrix_, self.vectorizer.get_feature_names()
        )

        return {
            "uci": uci,
            "umass": umass,
            "avg_uci": np.mean(list(uci.values())),
            "avg_umass": np.mean(list(umass.values())),
        }


def main():
    parser = argparse.ArgumentParser(description="Run topic modeling experiments")
    parser.add_argument("--k", type=int, default=5, help="Number of topics")
    parser.add_argument(
        "--cost", type=str, default="frobenius", choices=["frobenius", "kl"]
    )
    parser.add_argument(
        "--embeddings", action="store_true", help="Use dense embeddings"
    )
    parser.add_argument(
        "--data", type=str, default="math_investigation/data/synthetic_dataset.json"
    )
    parser.add_argument(
        "--output", type=str, default="math_investigation/results/topic_modeling"
    )
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load data
    documents, _ = load_synthetic_dataset(args.data)

    # Fit model
    modeler = TopicModeler(
        n_components=args.k,
        cost=args.cost,
        use_embeddings=args.embeddings,
        random_state=args.seed,
    )
    modeler.fit(documents)

    # Results
    topics = modeler.get_topics(n_words=10)
    coherence = modeler.compute_coherence()

    results = {
        "k": args.k,
        "cost": args.cost,
        "use_embeddings": args.embeddings,
        "topics": topics,
        "coherence": coherence,
    }

    # Save results
    with open(output_path / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Visualizations
    generate_wordcloud(topics, output_dir=str(output_path / "wordclouds"))
    generate_word_bars(topics, output_dir="math_investigation/results/visualizations")

    if modeler.nmf.W_ is not None:
        generate_document_topic_heatmap(modeler.nmf.W_, output_dir=str(output_path))

    # Generate Concept Map
    # Compute topic correlations from H matrix
    if modeler.nmf.H_ is not None:
        H = modeler.nmf.H_
        correlations = np.corrcoef(H)
        generate_concept_map(topics, topic_correlations=correlations)

    # Print summary
    print("\n" + "=" * 60)
    print("TOPIC MODELING RESULTS")
    print("=" * 60)
    print(f"k: {args.k}, Cost: {args.cost}, Embeddings: {args.embeddings}")
    print(f"Avg UCI Coherence: {coherence['avg_uci']:.4f}")
    print(f"Avg UMass Coherence: {coherence['avg_umass']:.4f}")
    print("\nTopics:")
    for i, words in topics.items():
        print(f"  Topic {i}: {', '.join(words)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
