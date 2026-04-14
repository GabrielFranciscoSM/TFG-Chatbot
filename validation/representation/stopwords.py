"""Multilingual stopwords for text processing.

Uses the stop-words package which provides comprehensive stopword lists
for 50+ languages including Spanish, English, and more.

Supported languages: https://github.com/Alir3z4/python-stop-words
"""

from stop_words import get_stop_words

# Default to Spanish (primary language) + English (technical terms)
STOPWORDS_ES = set(get_stop_words("spanish"))
STOPWORDS_EN = set(get_stop_words("english"))
STOPWORDS = STOPWORDS_ES | STOPWORDS_EN  # Combined for multilingual support


def get_stopwords(language: str = "spanish") -> set[str]:
    """Get stopwords for a specific language.

    Args:
        language: Language code or name (e.g., 'spanish', 'english', 'french')
                  See stop_words.AVAILABLE_LANGUAGES for full list.

    Returns:
        Set of stopwords for the specified language.

    Examples:
        >>> stopwords = get_stopwords("spanish")
        >>> len(stopwords) > 0
        True
        >>> "el" in get_stopwords("spanish")
        True
    """
    return set(get_stop_words(language))


def get_multilingual_stopwords(*languages: str) -> set[str]:
    """Get combined stopwords from multiple languages.

    Args:
        *languages: Variable number of language codes.

    Returns:
        Union of stopwords from all specified languages.

    Examples:
        >>> stopwords = get_multilingual_stopwords("spanish", "english")
        >>> "the" in stopwords and "el" in stopwords
        True
    """
    combined = set()
    for lang in languages:
        combined |= get_stopwords(lang)
    return combined
