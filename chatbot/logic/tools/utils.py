"""Utility functions and RAG normalization helpers for chatbot tools."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def navigate_nested_dict(data: dict, path: str) -> Any | None:
    """Navigate a nested dictionary using dot notation path.

    Args:
        data: The dictionary to navigate
        path: Dot-separated path (e.g., "parent.child.key")

    Returns:
        The value at the path, or None if not found
    """
    parts = path.split(".")
    value: dict[Any, Any] | Any = data
    for part in parts:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
        if value is None:
            return None
    return value


def extract_content_from_result(result: dict) -> str | None:
    """Extract content from a RAG result using common field names.

    Args:
        result: A single result dictionary from RAG service

    Returns:
        Content string or None
    """
    return (
        result.get("content")
        or result.get("text")
        or result.get("snippet")
        or result.get("payload")
    )


def extract_metadata_from_result(result: dict) -> dict:
    """Extract and normalize metadata from a RAG result.

    Args:
        result: A single result dictionary from RAG service

    Returns:
        Normalized metadata dictionary
    """
    metadata = (
        result.get("metadata")
        or result.get("meta")
        or result.get("payload_metadata")
        or {}
    )

    if metadata is None:
        return {}

    if not isinstance(metadata, dict):
        try:
            return dict(metadata)
        except Exception:
            return {"raw": metadata}

    return metadata


def extract_score_from_result(result: dict) -> float | None:
    """Extract score/similarity from a RAG result.

    Args:
        result: A single result dictionary from RAG service

    Returns:
        Score as float or None
    """
    if "score" in result and result.get("score") is not None:
        return result.get("score")
    elif "similarity" in result and result.get("similarity") is not None:
        return result.get("similarity")
    elif "distance" in result and result.get("distance") is not None:
        return result.get("distance")
    return None


def normalize_single_result(result: Any) -> dict[str, Any]:
    """Normalize a single RAG result to standard format.

    Args:
        result: A single result (dict or other) from RAG service

    Returns:
        Normalized result dict with content, metadata, and score
    """
    if isinstance(result, dict):
        logger.debug("Processing raw result keys=%s", list(result.keys()))

        content = extract_content_from_result(result)
        metadata = extract_metadata_from_result(result)
        score = extract_score_from_result(result)

        # Log truncated content for debugging
        try:
            content_snip = content[:200] if isinstance(content, str) else str(content)
        except Exception:
            content_snip = str(content)

        logger.debug(
            "Normalized result content=%s score=%s metadata_keys=%s",
            content_snip,
            score,
            list(metadata.keys()) if isinstance(metadata, dict) else None,
        )

        return {"content": content, "metadata": metadata, "score": score}
    else:
        return {"content": str(result), "metadata": {}, "score": None}


def normalize_rag_results(data: Any) -> list[dict[str, Any]]:
    """Normalize RAG service response into standard format.

    Args:
        data: Raw response from RAG service

    Returns:
        List of normalized results with content, metadata, and score
    """
    raw_results = data.get("results") if isinstance(data, dict) else None
    logger.debug("raw_results type=%s", type(raw_results))

    normalized = []

    if raw_results and isinstance(raw_results, list):
        for result in raw_results:
            normalized.append(normalize_single_result(result))
    else:
        # If the provider returned a flat text or other shape
        if isinstance(data, dict) and "content" in data:
            normalized.append(
                {
                    "content": data.get("content"),
                    "metadata": data.get("metadata", {}),
                    "score": data.get("score"),
                }
            )
        else:
            normalized.append({"content": str(data), "metadata": {}, "score": None})

    return normalized
