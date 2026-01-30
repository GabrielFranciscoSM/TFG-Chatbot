"""
Query complexity classifier for adaptive Chain-of-Thought prompting.

This module provides a simple heuristic-based classifier that determines
whether a query requires deep reasoning (CoT) or can be answered directly.

The classifier uses pattern matching and keyword analysis to categorize
queries without adding latency from LLM calls.

Example:
    >>> from chatbot.logic.query_classifier import classify_query, QueryComplexity
    >>> classify_query("Hola, ¿cómo estás?")
    QueryComplexity.SIMPLE
    >>> classify_query("¿Por qué usamos Docker en lugar de máquinas virtuales?")
    QueryComplexity.COMPLEX
"""

import re
from enum import Enum


class QueryComplexity(Enum):
    """Classification of query complexity for CoT decision."""

    SIMPLE = "simple"  # Direct answer, no reasoning needed
    COMPLEX = "complex"  # Requires step-by-step reasoning


# Keywords that indicate complex queries requiring reasoning
COMPLEX_KEYWORDS_ES = [
    # Explanatory
    "por qué",
    "porqué",
    "explica",
    "explicar",
    "explicame",
    "explícame",
    # Comparative/analytical
    "diferencia",
    "diferencias",
    "comparar",
    "compara",
    "versus",
    "vs",
    "mejor",
    "peor",
    "ventajas",
    "desventajas",
    "pros",
    "contras",
    # Problem-solving
    "cómo puedo",
    "como puedo",
    "cómo se",
    "como se",
    "cómo funciona",
    "como funciona",
    "solucionar",
    "resolver",
    "arreglar",
    "debuggear",
    "depurar",
    # Conceptual
    "qué significa",
    "que significa",
    "qué es",
    "que es",
    "para qué sirve",
    "para que sirve",
    "cuál es el propósito",
    "cual es el proposito",
    # Analysis
    "analiza",
    "analizar",
    "evalúa",
    "evaluar",
    "argumenta",
    "justifica",
    "razona",
]

COMPLEX_KEYWORDS_EN = [
    # Explanatory
    "why",
    "explain",
    "how does",
    "how do",
    # Comparative/analytical
    "difference",
    "compare",
    "versus",
    "vs",
    "better",
    "worse",
    "advantages",
    "disadvantages",
    "pros",
    "cons",
    # Problem-solving
    "how can i",
    "how to",
    "solve",
    "fix",
    "debug",
    "troubleshoot",
    # Conceptual
    "what is",
    "what does",
    "what are",
    "purpose of",
    # Analysis
    "analyze",
    "evaluate",
    "justify",
    "reason",
]

# Keywords that indicate simple queries
SIMPLE_KEYWORDS = [
    # Greetings (ES)
    "hola",
    "buenos días",
    "buenas tardes",
    "buenas noches",
    "gracias",
    "adiós",
    "hasta luego",
    # Greetings (EN)
    "hello",
    "hi",
    "hey",
    "thanks",
    "thank you",
    "bye",
    "goodbye",
    # Simple requests (ES)
    "cuándo",
    "cuando",
    "dónde",
    "donde",
    "quién",
    "quien",
    "cuánto",
    "cuanto",
    # Simple requests (EN)
    "when",
    "where",
    "who",
    "how much",
    "how many",
]

# Patterns that indicate complex reasoning is needed
COMPLEX_PATTERNS = [
    r"\bpor\s+qu[eé]\b",  # "por qué" with variations
    r"\bc[oó]mo\s+(?:funciona|se\s+hace|puedo)\b",  # "cómo funciona/se hace/puedo"
    r"\bdiferencia\s+entre\b",  # "diferencia entre X y Y"
    r"\bcompar[ae]\b",  # "compara/compare"
    r"\bexplica\b",  # "explica"
    r"\bwhy\s+(?:is|are|do|does|should|would)\b",  # "why is/are/do..."
    r"\bhow\s+(?:does|do|can|should|would)\b",  # "how does/do/can..."
    r"\bwhat\s+(?:is|are)\s+the\s+(?:difference|purpose|reason)\b",  # conceptual "what is"
]


def classify_query(query: str) -> QueryComplexity:
    """
    Classify a query as simple or complex using heuristics.

    This classifier uses keyword matching and pattern analysis to determine
    if a query requires Chain-of-Thought reasoning or can be answered directly.

    Args:
        query: The user's query text

    Returns:
        QueryComplexity.SIMPLE for direct answers
        QueryComplexity.COMPLEX for queries requiring reasoning

    Examples:
        >>> classify_query("Hola")
        QueryComplexity.SIMPLE
        >>> classify_query("¿Por qué Docker es mejor que VMs?")
        QueryComplexity.COMPLEX
    """
    query_lower = query.lower().strip()

    # Check for simple greetings first (very short queries)
    if len(query_lower) < 20:
        for keyword in SIMPLE_KEYWORDS[:15]:  # Only greetings subset
            if keyword in query_lower:
                return QueryComplexity.SIMPLE

    # Check complex patterns (regex)
    for pattern in COMPLEX_PATTERNS:
        if re.search(pattern, query_lower):
            return QueryComplexity.COMPLEX

    # Check complex keywords
    all_complex_keywords = COMPLEX_KEYWORDS_ES + COMPLEX_KEYWORDS_EN
    for keyword in all_complex_keywords:
        if keyword in query_lower:
            return QueryComplexity.COMPLEX

    # Check simple keywords (factual questions)
    for keyword in SIMPLE_KEYWORDS:
        if keyword in query_lower:
            return QueryComplexity.SIMPLE

    # Default: if query is longer than 50 chars and not matched, assume complex
    if len(query_lower) > 50:
        return QueryComplexity.COMPLEX

    return QueryComplexity.SIMPLE
