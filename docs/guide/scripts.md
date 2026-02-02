---
layout: default
title: Scripts Reference
parent: Developer Guide
nav_order: 3
---

# Scripts Reference

All utility scripts are located in the `scripts/` directory.

---

## Development Scripts

### `run_tests.sh` - Execute Container Tests

Runs tests inside Docker containers for each service with report generation.

```bash
# Run all services
./scripts/run_tests.sh all

# Run specific service
./scripts/run_tests.sh chatbot
./scripts/run_tests.sh backend
./scripts/run_tests.sh rag

# Run with pytest arguments
./scripts/run_tests.sh chatbot -k "test_embeddings"

# Skip container rebuild (faster)
./scripts/run_tests.sh all --no-rebuild
```

**Output**: Generates markdown reports in `test-reports/` directory.

---

### `seed_users.py` - Create Demo Users

Creates initial users for development and testing.

```bash
# Default usage
python scripts/seed_users.py

# With uv
uv run python scripts/seed_users.py

# Custom MongoDB URI
MONGO_URI=mongodb://user:pass@host:27017 python scripts/seed_users.py

# Custom password
SEED_PASSWORD=mypassword python scripts/seed_users.py
```

**Creates users**:
- `admin` (Admin role)
- `profesor` (Professor role, subject: ISE)
- `estudiante` (Student role, subject: ISE)

---

### `init_ollama.sh` - Initialize Embedding Model

Downloads and configures the embedding model in Ollama (first-time setup).

```bash
./scripts/init_ollama.sh
```

**Model**: `nomic-embed-text` (768 dimensions)

---

## AI/ML Scripts

### `train_difficulty_centroids.py` - Train Difficulty Classifier

Trains centroids for the question difficulty classifier using embeddings.

```bash
# Train with default data
python scripts/train_difficulty_centroids.py \
    --output chatbot/data/difficulty_centroids.json

# With custom labeled data
python scripts/train_difficulty_centroids.py \
    --data /path/to/labeled_questions.json \
    --output /path/to/centroids.json

# Generate sample training data
python scripts/train_difficulty_centroids.py --generate-samples
```

**Labeled data format**:
```json
[
    {"text": "¿Qué es Docker?", "difficulty": "basic"},
    {"text": "¿Cómo funciona Docker internamente?", "difficulty": "intermediate"},
    {"text": "¿Por qué Docker es mejor que VMs?", "difficulty": "advanced"}
]
```

---

### `label_questions_with_llm.py` - Auto-Label Questions

Uses LLM to automatically classify questions by difficulty level.

```bash
# Label questions from file
python scripts/label_questions_with_llm.py \
    --input questions.txt \
    --output chatbot/data/labeled_questions.json

# Generate and label questions for a topic
python scripts/label_questions_with_llm.py \
    --generate-for-topic "Docker y contenedores" \
    --num-questions 30 \
    --output chatbot/data/labeled_questions.json

# Use specific LLM provider
python scripts/label_questions_with_llm.py \
    --provider gemini \
    --input questions.txt \
    --output labeled.json
```

---

## Data Analysis Scripts

### `query_student_history.py` - Query Conversation History

Extracts student conversation history from MongoDB.

```bash
# Query specific user
python scripts/query_student_history.py estudiante

# Output as JSON
python scripts/query_student_history.py estudiante --json

# List all users with conversations
python scripts/query_student_history.py --list-users
```

---

## Scripts Summary Table

| Script | Purpose | Requires Services |
|--------|---------|-------------------|
| `run_tests.sh` | Run tests in containers | ✅ Docker |
| `seed_users.py` | Create demo users | ✅ MongoDB |
| `init_ollama.sh` | Setup embeddings model | ✅ Ollama |
| `train_difficulty_centroids.py` | Train classifier | ✅ RAG Service |
| `label_questions_with_llm.py` | Auto-label questions | ✅ LLM API |
| `query_student_history.py` | Query conversations | ✅ MongoDB |
