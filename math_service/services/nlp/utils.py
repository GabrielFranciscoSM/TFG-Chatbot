"""Shared NLP utility functions."""

import re
import string

from math_service.services.nlp.stopwords import STOPWORDS


def tokenize(text: str) -> list[str]:
    """Tokenize and normalize text.

    Args:
        text: Input text to tokenize

    Returns:
        List of normalized tokens (lowercase, no punctuation, no stopwords)
    """
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = re.findall(r"\b[a-z]{2,}\b", text)
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens
