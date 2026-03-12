"""Data loading utilities for clustering experiments."""

import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def load_synthetic_dataset(
    path: str = "math_investigation/data/synthetic_dataset.json",
) -> tuple[list[str], list[int]]:
    """Load synthetic dataset with documents and ground truth labels.

    Args:
        path: Path to the JSON dataset file

    Returns:
        Tuple of (documents, true_labels)
    """
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    true_labels = []

    # Map themes to numeric labels
    theme_to_label = {}
    label_counter = 0

    # Handle both list and dict formats
    items = data if isinstance(data, list) else data.get("fragments", [])

    for item in items:
        documents.append(item["text"])

        # Check both direct 'label' and 'metadata.theme'
        theme = item.get("label") or item.get("theme")
        if not theme and "metadata" in item:
            theme = item["metadata"].get("theme")

        if not theme:
            theme = "unknown"

        if theme not in theme_to_label:
            theme_to_label[theme] = label_counter
            label_counter += 1

        true_labels.append(theme_to_label[theme])

    logger.info(f"Loaded {len(documents)} documents from {path}")
    logger.info(f"Found {len(theme_to_label)} themes: {list(theme_to_label.keys())}")

    return documents, true_labels


def load_documents_from_json(path: str) -> list[str]:
    """Load documents from a generic JSON file.

    Supports formats:
    - List of strings
    - List of dicts with "text" or "content" keys
    - Dict with "documents", "texts", or "fragments" key

    Args:
        path: Path to JSON file

    Returns:
        List of document strings
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                documents.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("question")
                if text:
                    documents.append(text)
    elif isinstance(data, dict):
        for key in ["documents", "texts", "fragments", "questions"]:
            if key in data:
                for item in data[key]:
                    if isinstance(item, str):
                        documents.append(item)
                    elif isinstance(item, dict):
                        text = (
                            item.get("text")
                            or item.get("content")
                            or item.get("question")
                        )
                        if text:
                            documents.append(text)
                break

    logger.info(f"Loaded {len(documents)} documents from {path}")
    return documents


def find_data_files(data_dir: str = "data") -> list[Path]:
    """Find all JSON data files in the data directory.

    Args:
        data_dir: Directory to search

    Returns:
        List of paths to JSON files
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return []

    return list(data_path.glob("*.json"))


def find_nearest_to_centroids(X: np.ndarray, centroids: np.ndarray) -> list[int]:
    """Find the document index nearest to each centroid.

    Args:
        X: Document matrix (n_docs, n_features)
        centroids: Centroid matrix (k, n_features)

    Returns:
        List of document indices (one per centroid)
    """

    nearest_docs = []
    for centroid in centroids:
        distances = np.linalg.norm(X - centroid, axis=1)
        nearest_docs.append(int(np.argmin(distances)))
    return nearest_docs


# Note: numpy import is needed for find_nearest_to_centroids
