#!/usr/bin/env python3
"""
Train difficulty classifier centroids from labeled question samples.

This script generates centroids for the difficulty classifier by:
1. Loading labeled questions (basic, intermediate, advanced)
2. Computing embeddings via the RAG service
3. Calculating centroids as the mean of embeddings per difficulty level
4. Saving centroids to JSON file

Usage:
    python scripts/train_difficulty_centroids.py --output /path/to/centroids.json

    # With custom labeled data file:
    python scripts/train_difficulty_centroids.py \
        --data /path/to/labeled_questions.json \
        --output /path/to/centroids.json

    # Generate sample training data:
    python scripts/train_difficulty_centroids.py --generate-samples

Labeled data format (JSON):
    [
        {"text": "¿Qué es Docker?", "difficulty": "basic"},
        {"text": "¿Cómo funciona el sistema de archivos de Docker?", "difficulty": "intermediate"},
        {"text": "¿Por qué Docker es mejor que VMs para microservicios?", "difficulty": "advanced"}
    ]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np  # noqa: E402

from chatbot.logic.difficulty import (  # noqa: E402
    DifficultyClassifier,
    DifficultyLevel,
    get_embedding_from_rag_service,
    get_embeddings_batch,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Sample Training Data
# =============================================================================

SAMPLE_QUESTIONS = {
    DifficultyLevel.BASIC: [
        # Definitions and simple facts
        "¿Qué es Docker?",
        "¿Qué es un contenedor?",
        "¿Qué es Git?",
        "¿Qué es una API?",
        "¿Qué es Python?",
        "Define el término microservicio.",
        "¿Qué significa REST?",
        "¿Qué es una base de datos?",
        "Lista los tipos de datos primitivos en Python.",
        "¿Qué es un servidor web?",
        "What is Docker?",
        "What is a container?",
        "Define microservice.",
        "What is an API?",
        "List Python data types.",
    ],
    DifficultyLevel.INTERMEDIATE: [
        # Application and relationships
        "¿Cómo funciona Docker internamente?",
        "¿Cuál es la diferencia entre Docker y máquinas virtuales?",
        "¿Cómo se usa Git para control de versiones?",
        "Describe el proceso de crear una imagen Docker.",
        "¿Para qué sirve Docker Compose?",
        "¿Cómo funciona el sistema de capas en Docker?",
        "Explica las características principales de REST.",
        "¿Cómo se comunican los microservicios entre sí?",
        "Describe los pasos para hacer un commit en Git.",
        "¿Cuál es la relación entre contenedores e imágenes?",
        "How does Docker work internally?",
        "What is the difference between Docker and VMs?",
        "Describe the Docker image build process.",
        "Explain REST characteristics.",
        "How do microservices communicate?",
    ],
    DifficultyLevel.ADVANCED: [
        # Analysis, synthesis, and evaluation
        "¿Por qué Docker es mejor que las máquinas virtuales para microservicios?",
        "Analiza las ventajas y desventajas de usar contenedores en producción.",
        "¿Cómo diseñarías una arquitectura de microservicios escalable?",
        "Compara y contrasta Docker Swarm con Kubernetes.",
        "¿Qué implicaciones tiene usar Docker en términos de seguridad?",
        "Justifica el uso de contenedores para aplicaciones stateful.",
        "Evalúa los pros y contras de monolitos vs microservicios.",
        "¿Por qué usaríamos orquestadores de contenedores?",
        "Propón una estrategia de CI/CD usando contenedores.",
        "¿Qué pasaría si no aislamos correctamente los contenedores?",
        "Why is Docker better than VMs for microservices?",
        "Analyze pros and cons of containers in production.",
        "How would you design a scalable microservices architecture?",
        "Compare Docker Swarm with Kubernetes.",
        "Evaluate monoliths vs microservices approaches.",
    ],
}


def generate_sample_data_file(output_path: Path) -> None:
    """Generate a sample labeled questions file."""
    data = []
    for level, questions in SAMPLE_QUESTIONS.items():
        for q in questions:
            data.append({"text": q, "difficulty": level.value})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Generated sample data file: {output_path}")
    logger.info(f"Total samples: {len(data)}")


def load_labeled_data(data_path: Path) -> list[dict]:
    """Load labeled questions from JSON file."""
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} labeled questions from {data_path}")
    return data


def train_centroids(
    labeled_data: list[dict],
    use_batch: bool = True,
) -> dict[DifficultyLevel, np.ndarray]:
    """
    Train difficulty centroids from labeled data.

    Args:
        labeled_data: List of {"text": str, "difficulty": str} dicts
        use_batch: Whether to use batch embedding (faster)

    Returns:
        Dictionary mapping DifficultyLevel to centroid vectors
    """
    # Group questions by difficulty
    questions_by_level: dict[DifficultyLevel, list[str]] = {
        level: [] for level in DifficultyLevel
    }

    for item in labeled_data:
        level = DifficultyLevel(item["difficulty"])
        questions_by_level[level].append(item["text"])

    # Log distribution
    for level, questions in questions_by_level.items():
        logger.info(f"  {level.value}: {len(questions)} samples")

    # Compute embeddings
    logger.info("Computing embeddings...")

    embeddings_by_level: dict[DifficultyLevel, list[np.ndarray]] = {
        level: [] for level in DifficultyLevel
    }

    if use_batch:
        # Batch mode - faster
        all_texts = []
        text_to_level = {}

        for level, questions in questions_by_level.items():
            for q in questions:
                all_texts.append(q)
                text_to_level[q] = level

        try:
            all_embeddings = get_embeddings_batch(all_texts)
            for text, embedding in zip(all_texts, all_embeddings, strict=True):
                level = text_to_level[text]
                embeddings_by_level[level].append(np.array(embedding))
        except Exception as e:
            logger.warning(f"Batch embedding failed: {e}. Falling back to sequential.")
            use_batch = False

    if not use_batch:
        # Sequential mode - fallback
        for level, questions in questions_by_level.items():
            for q in questions:
                try:
                    embedding = get_embedding_from_rag_service(q)
                    embeddings_by_level[level].append(np.array(embedding))
                except Exception as e:
                    logger.error(f"Failed to embed '{q[:50]}...': {e}")

    # Compute centroids as mean
    centroids: dict[DifficultyLevel, np.ndarray] = {}
    for level in DifficultyLevel:
        level_embeddings = embeddings_by_level[level]
        if not level_embeddings:
            logger.warning(f"No embeddings for {level.value}, skipping")
            continue

        embeddings_array = np.array(level_embeddings)
        centroid = embeddings_array.mean(axis=0)
        centroids[level] = centroid

        logger.info(
            f"Computed centroid for {level.value}: "
            f"shape={centroid.shape}, "
            f"from {len(level_embeddings)} samples"
        )

    return centroids


def validate_centroids(
    centroids: dict[DifficultyLevel, np.ndarray],
    labeled_data: list[dict],
) -> dict:
    """
    Validate centroids by computing classification accuracy on training data.

    Returns metrics including accuracy per level and confusion matrix.
    """
    classifier = DifficultyClassifier(use_heuristics=False)
    classifier.centroids = centroids

    correct = 0
    total = 0
    per_level_correct: dict[str, int] = {level.value: 0 for level in DifficultyLevel}
    per_level_total: dict[str, int] = {level.value: 0 for level in DifficultyLevel}

    for item in labeled_data:
        true_level = DifficultyLevel(item["difficulty"])
        per_level_total[true_level.value] += 1
        total += 1

        try:
            embedding = get_embedding_from_rag_service(item["text"])
            result = classifier.classify_embedding(embedding)

            if result.level == true_level:
                correct += 1
                per_level_correct[true_level.value] += 1
        except Exception as e:
            logger.warning(f"Validation error for '{item['text'][:30]}...': {e}")

    accuracy = correct / total if total > 0 else 0
    per_level_accuracy = {
        level: (
            per_level_correct[level] / per_level_total[level]
            if per_level_total[level] > 0
            else 0
        )
        for level in per_level_correct
    }

    return {
        "overall_accuracy": accuracy,
        "per_level_accuracy": per_level_accuracy,
        "total_samples": total,
        "correct": correct,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Train difficulty classifier centroids"
    )
    parser.add_argument(
        "--data",
        type=Path,
        help="Path to labeled questions JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("chatbot/data/difficulty_centroids.json"),
        help="Output path for centroids JSON",
    )
    parser.add_argument(
        "--generate-samples",
        action="store_true",
        help="Generate sample labeled questions file and exit",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate centroids on training data",
    )
    parser.add_argument(
        "--use-builtin",
        action="store_true",
        help="Use built-in sample questions for training",
    )

    args = parser.parse_args()

    # Generate samples mode
    if args.generate_samples:
        sample_path = Path("chatbot/data/sample_labeled_questions.json")
        generate_sample_data_file(sample_path)
        print(f"\nSample data written to: {sample_path}")
        print("Edit this file with your own labeled questions, then run:")
        print(f"  python {__file__} --data {sample_path} --output {args.output}")
        return

    # Load or use built-in data
    if args.use_builtin:
        logger.info("Using built-in sample questions")
        labeled_data = []
        for level, questions in SAMPLE_QUESTIONS.items():
            for q in questions:
                labeled_data.append({"text": q, "difficulty": level.value})
    elif args.data:
        labeled_data = load_labeled_data(args.data)
    else:
        print("Error: Provide --data path or use --use-builtin")
        print("Run with --generate-samples to create a sample data file")
        sys.exit(1)

    # Train centroids
    logger.info("Training centroids...")
    try:
        centroids = train_centroids(labeled_data)
    except Exception as e:
        logger.error(f"Training failed: {e}")
        logger.error("Make sure RAG service is running and accessible")
        sys.exit(1)

    # Save centroids
    classifier = DifficultyClassifier()
    classifier.centroids = centroids
    classifier.save_centroids(args.output)
    print(f"\nCentroids saved to: {args.output}")

    # Optionally validate
    if args.validate:
        logger.info("Validating centroids on training data...")
        metrics = validate_centroids(centroids, labeled_data)
        print("\nValidation Results:")
        print(f"  Overall accuracy: {metrics['overall_accuracy']:.2%}")
        print("  Per-level accuracy:")
        for level, acc in metrics["per_level_accuracy"].items():
            print(f"    {level}: {acc:.2%}")


if __name__ == "__main__":
    main()
