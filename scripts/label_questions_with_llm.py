#!/usr/bin/env python3
"""
Label questions with difficulty levels using an LLM.

This script uses Gemini/Mistral/vLLM to automatically classify questions
into difficulty levels (basic, intermediate, advanced) for training
the difficulty classifier.

Usage:
    # Label questions from a file
    python scripts/label_questions_with_llm.py \
        --input questions.txt \
        --output chatbot/data/labeled_questions.json

    # Generate and label sample questions for a topic
    python scripts/label_questions_with_llm.py \
        --generate-for-topic "Docker y contenedores" \
        --num-questions 30 \
        --output chatbot/data/labeled_questions.json

    # Use specific LLM provider
    python scripts/label_questions_with_llm.py \
        --provider gemini \
        --input questions.txt \
        --output labeled.json

Input file format (one question per line):
    ¿Qué es Docker?
    ¿Cómo funciona el sistema de capas en Docker?
    ¿Por qué Docker es mejor que las máquinas virtuales?
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402

from chatbot.config import settings  # noqa: E402
from chatbot.logic.difficulty import DifficultyLevel  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# LLM Client Setup
# =============================================================================


def get_llm_client(provider: str):
    """Get configured LLM client based on provider."""
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = settings.get_gemini_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=api_key,
            temperature=0.7,
        )
    elif provider == "mistral":
        from langchain_mistralai import ChatMistralAI

        api_key = settings.get_mistral_api_key()
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not set in environment")
        return ChatMistralAI(
            model=settings.mistral_model,
            mistral_api_key=api_key,
            temperature=0.7,
        )
    elif provider == "vllm":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.model_path,
            openai_api_key="EMPTY",
            openai_api_base=settings.vllm_url,
            temperature=0.7,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# =============================================================================
# Prompts
# =============================================================================

CLASSIFICATION_SYSTEM_PROMPT = """Eres un experto en educación que clasifica preguntas por nivel de dificultad.

Clasifica preguntas en uno de estos tres niveles:
- basic: Preguntas sobre definiciones, conceptos fundamentales, hechos simples.
- intermediate: Preguntas sobre funcionamiento, procesos, relaciones entre conceptos.
- advanced: Preguntas de análisis, evaluación, síntesis, comparación profunda.

Responde SOLO con una de estas tres palabras: basic, intermediate, advanced"""

GENERATION_SYSTEM_PROMPT = """Eres un generador de preguntas educativas técnicas.

Genera preguntas variadas en los tres niveles de dificultad:
- Básico (~33%): Definiciones, conceptos fundamentales. Ej: "¿Qué es X?"
- Intermedio (~33%): Funcionamiento, procesos, relaciones. Ej: "¿Cómo funciona X?"
- Avanzado (~33%): Análisis, evaluación, diseño. Ej: "¿Por qué X es mejor que Y?"

IMPORTANTE: Responde SOLO con JSON válido, sin texto adicional ni markdown."""


# =============================================================================
# Classification Functions
# =============================================================================


def classify_question(llm, question: str, max_retries: int = 3) -> str | None:
    """
    Classify a single question using the LLM.

    Returns difficulty level string or None if classification fails.
    """
    messages = [
        SystemMessage(content=CLASSIFICATION_SYSTEM_PROMPT),
        HumanMessage(content=f"Pregunta: {question}\n\nNivel:"),
    ]

    for attempt in range(max_retries):
        try:
            response = llm.invoke(messages)
            content = response.content.strip().lower()

            # Extract difficulty level from response
            for level in DifficultyLevel:
                if level.value in content:
                    return level.value

            logger.warning(f"Unexpected response: {content}")
            return None

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2**attempt)  # Exponential backoff

    return None


def classify_questions_batch(
    llm,
    questions: list[str],
    delay: float = 0.5,
) -> list[dict]:
    """
    Classify multiple questions with rate limiting.

    Returns list of {"text": str, "difficulty": str} dicts.
    """
    results = []
    total = len(questions)

    for i, question in enumerate(questions, 1):
        logger.info(f"Classifying [{i}/{total}]: {question[:50]}...")

        difficulty = classify_question(llm, question)

        if difficulty:
            results.append(
                {
                    "text": question,
                    "difficulty": difficulty,
                }
            )
            logger.info(f"  → {difficulty}")
        else:
            logger.warning("  → Failed to classify, skipping")

        # Rate limiting
        if i < total:
            time.sleep(delay)

    return results


def generate_questions_for_topic(
    llm,
    topic: str,
    num_questions: int = 30,
) -> list[dict]:
    """
    Generate labeled questions for a topic using the LLM.

    Returns list of {"text": str, "difficulty": str} dicts.
    """
    user_prompt = f"""Genera exactamente {num_questions} preguntas sobre el tema "{topic}".

Formato JSON requerido:
[
  {{"question": "pregunta aquí", "difficulty": "basic"}},
  {{"question": "pregunta aquí", "difficulty": "intermediate"}},
  {{"question": "pregunta aquí", "difficulty": "advanced"}}
]

Genera {num_questions} preguntas balanceadas entre los tres niveles."""

    messages = [
        SystemMessage(content=GENERATION_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            content = response.content.strip()

            # Extract JSON from response
            # Handle case where LLM wraps in markdown code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            questions_data = json.loads(content)

            results = []
            for item in questions_data:
                q = item.get("question") or item.get("text")
                d = item.get("difficulty", "").lower()

                if q and d in ["basic", "intermediate", "advanced"]:
                    results.append({"text": q, "difficulty": d})

            logger.info(f"Generated {len(results)} questions for topic '{topic}'")
            return results

        except json.JSONDecodeError as e:
            logger.warning(f"Attempt {attempt + 1} - Failed to parse JSON: {e}")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    logger.error(f"Failed to generate questions for '{topic}' after 3 attempts")
    return []


# =============================================================================
# I/O Functions
# =============================================================================


def load_questions_from_file(path: Path) -> list[str]:
    """Load questions from a text file (one per line)."""
    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                questions.append(line)
    logger.info(f"Loaded {len(questions)} questions from {path}")
    return questions


def save_labeled_questions(results: list[dict], path: Path) -> None:
    """Save labeled questions to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # If file exists, merge with existing data
    existing = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)
        logger.info(f"Found {len(existing)} existing entries in {path}")

    # Merge, avoiding duplicates
    existing_texts = {item["text"] for item in existing}
    new_items = [r for r in results if r["text"] not in existing_texts]

    combined = existing + new_items

    with open(path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(combined)} total entries to {path} ({len(new_items)} new)")


def print_summary(results: list[dict]) -> None:
    """Print classification summary."""
    by_level = {"basic": 0, "intermediate": 0, "advanced": 0}
    for r in results:
        by_level[r["difficulty"]] += 1

    print("\n" + "=" * 50)
    print("Classification Summary")
    print("=" * 50)
    print(f"Total questions: {len(results)}")
    print(
        f"  Basic:        {by_level['basic']} ({by_level['basic']/len(results)*100:.1f}%)"
    )
    print(
        f"  Intermediate: {by_level['intermediate']} ({by_level['intermediate']/len(results)*100:.1f}%)"
    )
    print(
        f"  Advanced:     {by_level['advanced']} ({by_level['advanced']/len(results)*100:.1f}%)"
    )
    print("=" * 50)


# =============================================================================
# Sample Topics
# =============================================================================

SAMPLE_TOPICS = [
    "Docker y contenedores",
    "Kubernetes y orquestación",
    "Git y control de versiones",
    "CI/CD y DevOps",
    "APIs REST y microservicios",
    "Bases de datos SQL y NoSQL",
    "Python y programación",
    "Testing y calidad de software",
]


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Label questions with difficulty levels using LLM"
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        type=Path,
        help="Path to text file with questions (one per line)",
    )
    input_group.add_argument(
        "--generate-for-topic",
        type=str,
        help="Generate questions for this topic",
    )
    input_group.add_argument(
        "--generate-all-topics",
        action="store_true",
        help="Generate questions for all sample topics",
    )

    # Output
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("chatbot/data/labeled_questions.json"),
        help="Output JSON file path",
    )

    # Generation options
    parser.add_argument(
        "--num-questions",
        type=int,
        default=30,
        help="Number of questions to generate per topic (default: 30)",
    )

    # LLM options
    parser.add_argument(
        "--provider",
        choices=["gemini", "mistral", "vllm"],
        default=settings.llm_provider,
        help=f"LLM provider (default: {settings.llm_provider})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between API calls in seconds (default: 0.5)",
    )

    args = parser.parse_args()

    # Initialize LLM
    logger.info(f"Using LLM provider: {args.provider}")
    try:
        llm = get_llm_client(args.provider)
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        sys.exit(1)

    results = []

    # Mode 1: Classify questions from file
    if args.input:
        if not args.input.exists():
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)

        questions = load_questions_from_file(args.input)
        results = classify_questions_batch(llm, questions, delay=args.delay)

    # Mode 2: Generate questions for a single topic
    elif args.generate_for_topic:
        results = generate_questions_for_topic(
            llm,
            args.generate_for_topic,
            args.num_questions,
        )

    # Mode 3: Generate questions for all sample topics
    elif args.generate_all_topics:
        for topic in SAMPLE_TOPICS:
            logger.info(f"\n--- Generating for: {topic} ---")
            topic_results = generate_questions_for_topic(
                llm,
                topic,
                args.num_questions,
            )
            results.extend(topic_results)
            time.sleep(1)  # Rate limiting between topics

    # Save and summarize
    if results:
        save_labeled_questions(results, args.output)
        print_summary(results)
        print(f"\nOutput saved to: {args.output}")
        print("\nNext step: Train centroids with:")
        print(f"  python scripts/train_difficulty_centroids.py --data {args.output}")
    else:
        logger.error("No questions were classified/generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
