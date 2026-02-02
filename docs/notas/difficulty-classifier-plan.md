# Plan: Implement Question Difficulty Classifier Module

**Date:** 10 de febrero de 2026  
**HU:** #17 - Clasificador de Dificultad  
**Sprint:** Week 3

## Overview

Implement a difficulty classification system using embedding-based clustering. The classifier will categorize questions into basic/intermediate/advanced levels by computing distances to pre-trained difficulty centroids, integrating with the existing LangGraph agent flow.

---

## Implementation Steps

### 1. Create `chatbot/logic/difficulty.py`

Implement `DifficultyLevel` enum and `DifficultyClassifier` class following the pattern in `chatbot/logic/classifier.py`, using K-Means centroids from `math_investigation/clustering/kmeans.py`.

```python
class DifficultyLevel(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class DifficultyClassifier:
    def __init__(self, centroids_path: str | None = None):
        self.centroids: dict[DifficultyLevel, np.ndarray] | None = None
    
    def classify(self, embedding: list[float]) -> DifficultyLevel:
        """Classify question by distance to difficulty centroids."""
        ...
    
    def train(self, labeled_questions: list[tuple[str, DifficultyLevel]]):
        """Train/update centroids from labeled questions."""
        ...
```

### 2. Add Embedding Integration

Create helper to fetch embeddings from RAG service (call `/embed` endpoint) or use local `OllamaEmbeddings` following the pattern in `rag_service/embeddings/embedding_service.py`.

### 3. Extend `SubjectState`

Add `query_difficulty: DifficultyLevel | None` field in `chatbot/logic/graph.py` to track classified difficulty through the agent flow.

### 4. Integrate in `think()` Node

Call `classify_difficulty()` in the `think` method of `GraphAgent` and use the result to adjust prompt selection or response complexity alongside existing `QueryComplexity`.

### 5. Add Configuration Settings

Extend `chatbot/config.py` with:
- `difficulty_centroids_path` - Path to stored centroids
- `difficulty_model_version` - Version tracking

### 6. Create Training Script

Add `scripts/train_difficulty_centroids.py` to generate initial centroids from labeled question samples using the existing K-Means implementation.

---

## Difficulty Level Criteria

| Level | Description | Characteristics |
|-------|-------------|-----------------|
| **Basic** | Foundational concepts | Short questions, simple vocabulary, definitions, "what is" |
| **Intermediate** | Application & relationships | Technical terminology, "how", "compare", relationships |
| **Advanced** | Analysis & synthesis | Complex structure, multiple concepts, "why", practical applications |

---

## Reusable Components

| Component | File | Purpose |
|-----------|------|---------|
| Query classifier pattern | `chatbot/logic/classifier.py` | Reference implementation for hybrid classification |
| K-Means clustering | `math_investigation/clustering/kmeans.py` | Train difficulty centroids |
| Fuzzy C-Means | `math_investigation/clustering/fcm.py` | Soft classification (optional) |
| Silhouette score | `math_investigation/clustering/metrics.py` | Validate cluster quality |
| Embedding service | `rag_service/embeddings/embedding_service.py` | Generate 768-dim embeddings |

---

## Open Questions

### 1. Labeled Training Data Source
- [ ] Use existing test questions from `generate_test` tool
- [ ] Manually annotate sample questions
- [ ] Bootstrap with LLM-generated labels

### 2. Soft vs Hard Classification
- [ ] K-Means for discrete levels
- [ ] FuzzyCMeans for confidence scores per level

### 3. Centroid Persistence Format
- [ ] NumPy `.npy` files (simple)
- [ ] JSON for portability
- [ ] MongoDB collection for dynamic updates

---

## Acceptance Criteria

- [ ] Module `chatbot/logic/difficulty.py` created
- [ ] Classifier with basic/intermediate/advanced levels functional
- [ ] Distance-to-centroid classification implemented
- [ ] Integration with agent `think()` node
- [ ] Unit tests for classifier
- [ ] Configuration settings added

---

## References

- ADR template: `docs/ADR/adr-template.md`
- Existing classifier: `chatbot/logic/classifier.py`
- State definition: `chatbot/logic/graph.py` (`SubjectState`)
- Test models: `chatbot/logic/models.py` (`Question.difficulty`)
