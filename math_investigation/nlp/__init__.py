"""NLP module: vectorizers and text processing utilities."""

from math_investigation.nlp.bow import BoWVectorizer
from math_investigation.nlp.embeddings import OllamaEmbeddings
from math_investigation.nlp.stopwords import (
    STOPWORDS,
    get_multilingual_stopwords,
    get_stopwords,
)
from math_investigation.nlp.tfidf import TFIDFVectorizer

__all__ = [
    "STOPWORDS",
    "get_stopwords",
    "get_multilingual_stopwords",
    "TFIDFVectorizer",
    "BoWVectorizer",
    "OllamaEmbeddings",
]
