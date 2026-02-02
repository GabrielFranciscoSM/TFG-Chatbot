"""Plotting functions for clustering and topic modeling visualization."""

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def plot_elbow(results: dict, output_path: str) -> None:
    """Plot Elbow Method results."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # SSE plot
    ax1.plot(results["k"], results["sse"], "bo-", linewidth=2, markersize=8)
    ax1.set_xlabel("Number of clusters (k)", fontsize=12)
    ax1.set_ylabel("SSE (Sum of Squared Errors)", fontsize=12)
    ax1.set_title("Elbow Method - SSE", fontsize=14)
    ax1.grid(True, alpha=0.3)

    # Silhouette plot
    ax2.plot(results["k"], results["silhouette"], "ro-", linewidth=2, markersize=8)
    ax2.set_xlabel("Number of clusters (k)", fontsize=12)
    ax2.set_ylabel("Silhouette Score", fontsize=12)
    ax2.set_title("Silhouette Score vs k", fontsize=14)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Elbow plot saved to {output_path}")


def plot_fcm_membership_heatmap(
    membership: np.ndarray, output_path: str, sample_size: int = 50
) -> None:
    """Plot FCM membership heatmap."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return

    # Sample for better visualization
    n_samples = membership.shape[1]
    if n_samples > sample_size:
        indices = np.linspace(0, n_samples - 1, sample_size, dtype=int)
        membership_sample = membership[:, indices]
    else:
        membership_sample = membership

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(membership_sample, aspect="auto", cmap="YlOrRd")

    ax.set_xlabel("Documents (sampled)", fontsize=12)
    ax.set_ylabel("Cluster", fontsize=12)
    ax.set_title("FCM Membership Matrix (μ_ji)", fontsize=14)
    ax.set_yticks(range(membership.shape[0]))
    ax.set_yticklabels([f"Cluster {i}" for i in range(membership.shape[0])])

    plt.colorbar(im, ax=ax, label="Membership degree")
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"FCM membership heatmap saved to {output_path}")


def plot_comparison(kmeans_results: dict, fcm_results: dict, output_path: str) -> None:
    """Plot comparison between K-Means and FCM."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Silhouette comparison
    methods = ["K-Means (TF-IDF)", "K-Means (BoW)"]
    silhouettes = [
        kmeans_results["tfidf"]["silhouette"],
        kmeans_results["bow"]["silhouette"],
    ]
    colors = ["#2ecc71", "#27ae60"]

    if "emb" in kmeans_results:
        methods.append("K-Means (Emb)")
        silhouettes.append(kmeans_results["emb"]["silhouette"])
        colors.append("#1e8449")

    methods.extend(["FCM (TF-IDF)", "FCM (BoW)"])
    silhouettes.extend(
        [
            fcm_results["tfidf"]["silhouette"],
            fcm_results["bow"]["silhouette"],
        ]
    )
    colors.extend(["#e74c3c", "#c0392b"])

    if "emb" in fcm_results:
        methods.append("FCM (Emb)")
        silhouettes.append(fcm_results["emb"]["silhouette"])
        colors.append("#922b21")

    axes[0].bar(methods, silhouettes, color=colors)
    axes[0].set_ylabel("Silhouette Score", fontsize=12)
    axes[0].set_title("Clustering Quality Comparison", fontsize=14)
    axes[0].tick_params(axis="x", rotation=45, labelsize=10)

    # Convergence comparison
    axes[1].plot(
        kmeans_results["tfidf"]["sse_history"],
        "g-",
        label="K-Means (TF-IDF)",
        linewidth=2,
    )
    axes[1].plot(
        kmeans_results["bow"]["sse_history"], "g--", label="K-Means (BoW)", linewidth=2
    )
    if "emb" in kmeans_results:
        axes[1].plot(
            kmeans_results["emb"]["sse_history"],
            "g:",
            label="K-Means (Emb)",
            linewidth=2,
        )

    axes[1].plot(
        fcm_results["tfidf"]["jm_history"], "r-", label="FCM (TF-IDF)", linewidth=2
    )
    axes[1].plot(
        fcm_results["bow"]["jm_history"], "r--", label="FCM (BoW)", linewidth=2
    )
    if "emb" in fcm_results:
        axes[1].plot(
            fcm_results["emb"]["jm_history"], "r:", label="FCM (Emb)", linewidth=2
        )

    axes[1].set_xlabel("Iteration", fontsize=12)
    axes[1].set_ylabel("Objective Function", fontsize=12)
    axes[1].set_title("Convergence Comparison", fontsize=14)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Comparison plot saved to {output_path}")


def generate_wordcloud(
    topics: dict[int, list[str]],
    weights: dict[int, list[float]] | None = None,
    output_dir: str = "math_investigation/results/visualizations",
) -> None:
    """Generate wordcloud images for each topic."""
    try:
        import matplotlib.pyplot as plt
        from wordcloud import WordCloud
    except ImportError:
        logger.warning("wordcloud/matplotlib not available, skipping")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for topic_idx, words in topics.items():
        if weights and topic_idx in weights:
            word_weights = dict(zip(words, weights[topic_idx], strict=True))
        else:
            word_weights = {w: 1.0 / (i + 1) for i, w in enumerate(words)}

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white",
            colormap="viridis",
        ).generate_from_frequencies(word_weights)

        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Topic {topic_idx}", fontsize=16)
        plt.savefig(output_path / f"wordcloud_topic_{topic_idx}.png", dpi=150)
        plt.close()

    logger.info(f"Wordclouds saved to {output_dir}")


def generate_document_topic_heatmap(
    W_matrix: np.ndarray,
    output_dir: str = "math_investigation/results/visualizations",
    filename: str = "document_topic_heatmap.png",
) -> None:
    """Generate heatmap of document-topic distribution."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        logger.warning("matplotlib/seaborn not available, skipping")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Sample if too many documents
    if W_matrix.shape[0] > 100:
        indices = np.linspace(0, W_matrix.shape[0] - 1, 100, dtype=int)
        W_sample = W_matrix[indices]
    else:
        W_sample = W_matrix

    plt.figure(figsize=(12, 8))
    sns.heatmap(
        W_sample,
        cmap="YlOrRd",
        xticklabels=[f"Topic {i}" for i in range(W_sample.shape[1])],
    )
    plt.xlabel("Topics", fontsize=12)
    plt.ylabel("Documents", fontsize=12)
    plt.title("Document-Topic Distribution", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path / filename, dpi=150)
    plt.close()

    logger.info(f"Document-topic heatmap saved to {output_path / filename}")


def generate_word_bars(
    topics: dict[int, list[str]],
    weights: dict[int, list[float]] | None = None,
    output_dir: str = "math_investigation/results/visualizations",
) -> None:
    """Generate bar charts for topic words."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for topic_idx, words in topics.items():
        if weights and topic_idx in weights:
            w = weights[topic_idx]
        else:
            w = [1.0 / (i + 1) for i in range(len(words))]

        plt.figure(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(words)))
        plt.barh(range(len(words)), w[::-1], color=colors)
        plt.yticks(range(len(words)), words[::-1])
        plt.xlabel("Weight", fontsize=12)
        plt.title(f"Topic {topic_idx} - Top Words", fontsize=14)
        plt.tight_layout()
        plt.savefig(output_path / f"topic_{topic_idx}_words.png", dpi=150)
        plt.close()


def generate_coherence_comparison(
    results: list[dict],
    output_dir: str = "math_investigation/results/visualizations",
    filename: str = "coherence_comparison.png",
) -> None:
    """Generate bar chart comparing coherence across different k values."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping")
        return

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

    ax.set_xlabel("Number of Topics (k)", fontsize=12)
    ax.set_ylabel("Coherence Score", fontsize=12)
    ax.set_title("Topic Coherence Comparison", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([f"k={k}" for k in ks])
    ax.legend()
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path / filename, dpi=150)
    plt.close()
    logger.info(f"Coherence comparison saved to {output_path / filename}")


def generate_concept_map(
    topics: dict[int, list[str]],
    topic_correlations: np.ndarray | None = None,
    output_path: str = "math_investigation/results/visualizations/concept_map.json",
) -> dict:
    """Generate concept map structure for UI integration."""
    import json

    nodes = []
    for topic_idx, words in topics.items():
        name = words[0].title() if words else f"Topic {topic_idx}"
        nodes.append(
            {
                "id": topic_idx,
                "name": name,
                "keywords": words[:5],
                "all_keywords": words,
            }
        )

    connections = []
    if topic_correlations is not None:
        n_topics = len(topics)
        for i in range(n_topics):
            for j in range(i + 1, n_topics):
                strength = float(topic_correlations[i, j])
                if strength > 0.1:
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

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(concept_map, f, indent=2, ensure_ascii=False)

    logger.info(f"Concept map saved to {output}")
    return concept_map


# =============================================================================
# Dimensionality Reduction Visualizations (t-SNE / UMAP)
# =============================================================================


def plot_tsne_clusters(
    embeddings: np.ndarray,
    labels: np.ndarray,
    output_path: str,
    perplexity: int = 30,
    title: str = "t-SNE Cluster Visualization",
    label_names: dict[int, str] | None = None,
    figsize: tuple[int, int] = (12, 8),
) -> None:
    """Plot t-SNE dimensionality reduction with cluster coloring.

    Args:
        embeddings: High-dimensional embeddings array (n_samples, n_features)
        labels: Cluster labels for each sample (n_samples,)
        output_path: Path to save the plot
        perplexity: t-SNE perplexity parameter (default 30, range 5-50)
        title: Plot title
        label_names: Optional mapping from label int to display name
        figsize: Figure size as (width, height)
    """
    try:
        from sklearn.manifold import TSNE
    except ImportError:
        logger.warning("sklearn not available, skipping t-SNE plot")
        return

    logger.info(f"Computing t-SNE with perplexity={perplexity}...")

    # Adjust perplexity if needed (must be < n_samples)
    n_samples = embeddings.shape[0]
    if perplexity >= n_samples:
        perplexity = max(5, n_samples // 4)
        logger.warning(f"Adjusted perplexity to {perplexity} due to small sample size")

    tsne = TSNE(
        n_components=2,
        perplexity=perplexity,
        random_state=42,
        max_iter=1000,
        learning_rate="auto",
        init="pca",
    )
    embeddings_2d = tsne.fit_transform(embeddings)

    _plot_2d_clusters(
        embeddings_2d,
        labels,
        output_path,
        title=title,
        label_names=label_names,
        figsize=figsize,
        method="t-SNE",
    )


def plot_umap_clusters(
    embeddings: np.ndarray,
    labels: np.ndarray,
    output_path: str,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    title: str = "UMAP Cluster Visualization",
    label_names: dict[int, str] | None = None,
    figsize: tuple[int, int] = (12, 8),
) -> None:
    """Plot UMAP dimensionality reduction with cluster coloring.

    Args:
        embeddings: High-dimensional embeddings array (n_samples, n_features)
        labels: Cluster labels for each sample (n_samples,)
        output_path: Path to save the plot
        n_neighbors: UMAP n_neighbors parameter (default 15)
        min_dist: UMAP minimum distance parameter (default 0.1)
        title: Plot title
        label_names: Optional mapping from label int to display name
        figsize: Figure size as (width, height)
    """
    try:
        import umap
    except ImportError:
        logger.warning("umap-learn not available, skipping UMAP plot")
        return

    logger.info(
        f"Computing UMAP with n_neighbors={n_neighbors}, min_dist={min_dist}..."
    )

    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        random_state=42,
        metric="cosine",
    )
    embeddings_2d = reducer.fit_transform(embeddings)

    _plot_2d_clusters(
        embeddings_2d,
        labels,
        output_path,
        title=title,
        label_names=label_names,
        figsize=figsize,
        method="UMAP",
    )


def _plot_2d_clusters(
    embeddings_2d: np.ndarray,
    labels: np.ndarray,
    output_path: str,
    title: str,
    label_names: dict[int, str] | None = None,
    figsize: tuple[int, int] = (12, 8),
    method: str = "",
) -> None:
    """Internal function to plot 2D scatter with cluster coloring.

    Args:
        embeddings_2d: 2D embeddings array (n_samples, 2)
        labels: Cluster labels for each sample
        output_path: Path to save the plot
        title: Plot title
        label_names: Optional mapping from label int to display name
        figsize: Figure size
        method: Dimensionality reduction method name for axis labels
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return

    fig, ax = plt.subplots(figsize=figsize)

    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

    for idx, label in enumerate(unique_labels):
        mask = labels == label
        display_name = (
            label_names.get(label, f"Cluster {label}")
            if label_names
            else f"Cluster {label}"
        )
        ax.scatter(
            embeddings_2d[mask, 0],
            embeddings_2d[mask, 1],
            c=[colors[idx]],
            label=display_name,
            alpha=0.7,
            s=50,
            edgecolors="white",
            linewidths=0.5,
        )

    ax.set_xlabel(f"{method} Dimension 1", fontsize=12)
    ax.set_ylabel(f"{method} Dimension 2", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"{method} cluster plot saved to {output_path}")


def plot_comparison_tsne_umap(
    embeddings: np.ndarray,
    predicted_labels: np.ndarray,
    true_labels: np.ndarray,
    output_path: str,
    label_names: dict[int, str] | None = None,
    figsize: tuple[int, int] = (16, 12),
) -> None:
    """Plot side-by-side comparison of t-SNE and UMAP with predicted vs true labels.

    Creates a 2x2 grid:
    - Top row: t-SNE (predicted vs true)
    - Bottom row: UMAP (predicted vs true)

    Args:
        embeddings: High-dimensional embeddings array
        predicted_labels: Cluster predictions
        true_labels: Ground truth labels
        output_path: Path to save the plot
        label_names: Optional mapping from label int to display name
        figsize: Figure size
    """
    try:
        import matplotlib.pyplot as plt
        import umap
        from sklearn.manifold import TSNE
    except ImportError:
        logger.warning(
            "matplotlib/sklearn/umap not available, skipping comparison plot"
        )
        return

    logger.info("Computing t-SNE and UMAP for comparison plot...")

    # Compute both reductions
    n_samples = embeddings.shape[0]
    perplexity = min(30, max(5, n_samples // 4))

    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42, init="pca")
    tsne_2d = tsne.fit_transform(embeddings)

    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
    umap_2d = reducer.fit_transform(embeddings)

    # Create 2x2 subplot
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    def scatter_subplot(ax, coords, labels, title, label_names_map):
        unique_labels = np.unique(labels)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
        for idx, label in enumerate(unique_labels):
            mask = labels == label
            name = (
                label_names_map.get(label, f"Label {label}")
                if label_names_map
                else f"Label {label}"
            )
            ax.scatter(
                coords[mask, 0],
                coords[mask, 1],
                c=[colors[idx]],
                label=name,
                alpha=0.7,
                s=40,
                edgecolors="white",
                linewidths=0.3,
            )
        ax.set_title(title, fontsize=12)
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)

    scatter_subplot(
        axes[0, 0], tsne_2d, predicted_labels, "t-SNE - Predicted Labels", label_names
    )
    scatter_subplot(
        axes[0, 1], tsne_2d, true_labels, "t-SNE - True Labels", label_names
    )
    scatter_subplot(
        axes[1, 0], umap_2d, predicted_labels, "UMAP - Predicted Labels", label_names
    )
    scatter_subplot(axes[1, 1], umap_2d, true_labels, "UMAP - True Labels", label_names)

    plt.suptitle("Clustering Validation: Predicted vs True Labels", fontsize=14, y=1.02)
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Comparison plot saved to {output_path}")
