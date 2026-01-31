#!/usr/bin/env python3
"""
Visualization module for Topic Modeling results.

Generates wordclouds, heatmaps, and concept maps from NMF topic models.
"""

import argparse
import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_wordcloud(
    topics: dict[int, list[str]],
    weights: dict[int, list[float]] | None = None,
    output_dir: str = "data/visualizations",
) -> None:
    """Generate wordcloud images for each topic.

    Args:
        topics: Dictionary of topic_idx -> top words
        weights: Optional dictionary of topic_idx -> word weights
        output_dir: Directory to save images
    """
    try:
        from wordcloud import WordCloud
    except ImportError:
        logger.warning("wordcloud not installed. Generating simple bar charts instead.")
        generate_word_bars(topics, weights, output_dir)
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for topic_idx, words in topics.items():
        # Create word frequency dict
        if weights and topic_idx in weights:
            word_weights = dict(zip(words, weights[topic_idx], strict=True))
        else:
            # Decreasing weights based on rank
            word_weights = {w: 1.0 / (i + 1) for i, w in enumerate(words)}

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white",
            colormap="viridis",
            max_words=len(words),
        ).generate_from_frequencies(word_weights)

        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Topic {topic_idx}")
        plt.tight_layout()

        filepath = output_path / f"topic_{topic_idx}_wordcloud.png"
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved wordcloud: {filepath}")


def generate_word_bars(
    topics: dict[int, list[str]],
    weights: dict[int, list[float]] | None = None,
    output_dir: str = "data/visualizations",
) -> None:
    """Generate bar charts for topic words (fallback if wordcloud unavailable).

    Args:
        topics: Dictionary of topic_idx -> top words
        weights: Optional dictionary of topic_idx -> word weights
        output_dir: Directory to save images
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for topic_idx, words in topics.items():
        # Get weights
        if weights and topic_idx in weights:
            w = weights[topic_idx]
        else:
            w = [1.0 / (i + 1) for i in range(len(words))]

        plt.figure(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(words)))
        plt.barh(range(len(words)), w[::-1], color=colors)
        plt.yticks(range(len(words)), words[::-1])
        plt.xlabel("Weight")
        plt.title(f"Topic {topic_idx} - Top Words")
        plt.tight_layout()

        filepath = output_path / f"topic_{topic_idx}_words.png"
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved topic words: {filepath}")


def generate_document_topic_heatmap(
    W_matrix: np.ndarray,
    output_dir: str = "data/visualizations",
    filename: str = "document_topic_heatmap.png",
) -> None:
    """Generate heatmap of document-topic distribution.

    Args:
        W_matrix: Document-topic matrix from NMF (n_docs x n_topics)
        output_dir: Directory to save images
        filename: Output filename
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Normalize rows to show proportion
    W_normalized = W_matrix / (W_matrix.sum(axis=1, keepdims=True) + 1e-10)

    # Limit to first 50 documents for visibility
    n_docs_to_show = min(50, W_normalized.shape[0])

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        W_normalized[:n_docs_to_show],
        cmap="YlOrRd",
        xticklabels=[f"Topic {i}" for i in range(W_matrix.shape[1])],
        yticklabels=False,
        cbar_kws={"label": "Topic Proportion"},
    )
    plt.xlabel("Topics")
    plt.ylabel(f"Documents (first {n_docs_to_show})")
    plt.title("Document-Topic Distribution")
    plt.tight_layout()

    filepath = output_path / filename
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Saved heatmap: {filepath}")


def generate_coherence_comparison(
    results: list[dict],
    output_dir: str = "data/visualizations",
    filename: str = "coherence_comparison.png",
) -> None:
    """Generate bar chart comparing coherence across different k values.

    Args:
        results: List of dicts with 'k', 'uci', 'umass' keys
        output_dir: Directory to save images
        filename: Output filename
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ks = [r["k"] for r in results]
    uci = [r["uci"] for r in results]
    umass = [r["umass"] for r in results]

    x = np.arange(len(ks))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, uci, width, label="UCI Coherence", color="steelblue")
    ax.bar(x + width / 2, umass, width, label="UMass Coherence", color="coral")

    ax.set_xlabel("Number of Topics (k)")
    ax.set_ylabel("Coherence Score")
    ax.set_title("Topic Coherence Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels([f"k={k}" for k in ks])
    ax.legend()
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()

    filepath = output_path / filename
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Saved coherence comparison: {filepath}")


def generate_concept_map(
    topics: dict[int, list[str]],
    topic_correlations: np.ndarray | None = None,
    output_path: str = "data/visualizations/concept_map.json",
) -> dict:
    """Generate concept map structure for UI integration.

    Args:
        topics: Dictionary of topic_idx -> top words
        topic_correlations: Optional correlation matrix between topics
        output_path: Path to save JSON

    Returns:
        Concept map dictionary
    """
    # Build topic nodes
    nodes = []
    for topic_idx, words in topics.items():
        # Use first word as topic name
        name = words[0].title() if words else f"Topic {topic_idx}"
        nodes.append(
            {
                "id": topic_idx,
                "name": name,
                "keywords": words[:5],
                "all_keywords": words,
            }
        )

    # Build connections based on shared vocabulary or correlations
    connections = []
    if topic_correlations is not None:
        n_topics = len(topics)
        for i in range(n_topics):
            for j in range(i + 1, n_topics):
                strength = float(topic_correlations[i, j])
                if strength > 0.1:  # Threshold for connection
                    connections.append(
                        {
                            "source": i,
                            "target": j,
                            "strength": round(strength, 3),
                        }
                    )

    concept_map = {
        "topics": nodes,
        "connections": connections,
        "metadata": {
            "n_topics": len(topics),
            "generated_by": "NMF Topic Modeling",
        },
    }

    # Save to file
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(concept_map, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved concept map: {output}")

    return concept_map


def main():
    """Generate all visualizations from a fitted topic model."""
    parser = argparse.ArgumentParser(
        description="Generate visualizations for topic modeling results."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/visualizations",
        help="Output directory for visualizations",
    )

    args = parser.parse_args()

    # Import and run topic modeling to get results
    from topic_modeling import TopicModeler, load_dataset

    documents, labels = load_dataset("data/synthetic_dataset.json")

    # Fit model
    modeler = TopicModeler(n_components=5, max_features=500)
    modeler.fit(documents)

    # Get data for visualizations
    topics = modeler.get_topics(n_words=15)

    # Extract weights from H matrix
    weights: dict[int, list[float]] = {}
    if modeler.nmf.H_ is not None:
        for topic_idx, topic_vec in enumerate(modeler.nmf.H_):
            top_indices = topic_vec.argsort()[-15:][::-1]
            weights[topic_idx] = [float(topic_vec[i]) for i in top_indices]

    # Generate visualizations
    generate_word_bars(topics, weights, args.output_dir)
    generate_document_topic_heatmap(modeler.nmf.W_, args.output_dir)
    generate_concept_map(topics)

    # Coherence comparison for different k
    results = []
    for k in [3, 5, 10]:
        m = TopicModeler(n_components=k, max_features=500)
        m.fit(documents)
        coherence = m.compute_coherence()
        results.append(
            {
                "k": k,
                "uci": coherence["avg_uci"],
                "umass": coherence["avg_umass"],
            }
        )

    generate_coherence_comparison(results, args.output_dir)

    logger.info(f"All visualizations saved to {args.output_dir}")


if __name__ == "__main__":
    main()
