---
adr: 0037
title: "Student Knowledge Profile Schema"
date: 2026-02-16
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 37
---

# ADR 0037 — Student Knowledge Profile Schema

## Status

Accepted

## Context

El chatbot pedagógico necesita mantener un **perfil de conocimiento** para cada estudiante que permita:

1. **Respuestas adaptativas**: Ajustar complejidad y detalle según nivel del estudiante
2. **Seguimiento de progreso**: Tracking de maestría por tema/asignatura
3. **Análisis para profesores**: Dashboard con insights sobre dificultades comunes
4. **Personalización de tests**: Generar preguntas apropiadas al nivel

### Requisitos funcionales

| Requisito | Descripción |
|-----------|-------------|
| RF-1 | Registrar cada interacción con dificultad clasificada |
| RF-2 | Mantener distribución de dificultad (básico/intermedio/avanzado) |
| RF-3 | Trackear maestría por tema dentro de cada asignatura |
| RF-4 | Almacenar historial de tests y puntuaciones |
| RF-5 | Soportar consultas eficientes por usuario y por asignatura |

### Restricciones

- Almacenamiento en MongoDB (decisión previa en [ADR 0029](0029-shared-mongodb-with-separate-collections.md))
- Actualizaciones atómicas para concurrencia
- Límite de documento MongoDB: 16MB

## Decision

Implementar un **esquema de perfil de estudiante** con las siguientes características:

### Schema del perfil (`student_profiles` collection)

```python
class StudentProfile(BaseModel):
    user_id: str                           # _id en MongoDB
    created_at: datetime
    updated_at: datetime
    
    # Distribución de dificultad de interacciones
    difficulty_distribution: dict[str, int] = {
        "basic": 0,
        "intermediate": 0,
        "advanced": 0
    }
    
    # Maestría por asignatura y tema
    subject_mastery: dict[str, dict[str, TopicMastery]] = {}
    # Ejemplo: {"iv": {"docker": TopicMastery(...), "kubernetes": TopicMastery(...)}}
    
    # Interacciones recientes (rolling window)
    recent_interactions: list[Interaction]  # Máximo 50
    
    # Estadísticas de tests
    total_interactions: int = 0
    total_tests_taken: int = 0
    average_test_score: float | None = None

class TopicMastery(BaseModel):
    level: float = 0.5              # Nivel de maestría [0, 1]
    interactions_count: int = 0
    correct_answers: int = 0
    total_test_questions: int = 0
    last_interaction: datetime | None = None
```

### Schema de conversaciones (`conversations` collection)

```python
class ConversationTurn(BaseModel):
    session_id: str
    user_id: str | None
    subject: str | None
    timestamp: datetime
    
    query: str                      # Pregunta completa (sin truncar)
    answer: str                     # Respuesta completa (sin truncar)
    
    difficulty: str | None          # Dificultad clasificada
    latency_ms: float | None        # Tiempo de respuesta
    rag_sources_used: list[str] | None
    was_test: bool = False
```

### Algoritmo de actualización de maestría

```python
def update_topic_mastery(correct: bool, current_level: float) -> float:
    """
    Actualización asimétrica de maestría:
    - Respuesta correcta: +0.1
    - Respuesta incorrecta: -0.05
    
    Asimétrico para fomentar progreso mientras se penalizan errores menos.
    """
    adjustment = 0.1 if correct else -0.05
    return max(0.0, min(1.0, current_level + adjustment))
```

## Consequences

### Pros

1. **Actualizaciones atómicas**: Uso de operadores MongoDB `$inc`, `$push`, `$set` evita race conditions
2. **Consultas eficientes**: Índice en `_id` (user_id) permite O(1) lookup
3. **Historial limitado**: Rolling window de 50 interacciones evita crecimiento ilimitado
4. **Flexibilidad**: Schema permite agregar nuevos temas/asignaturas dinámicamente
5. **Análisis agregado**: Fácil calcular métricas por asignatura o cohorte

### Cons

1. **Denormalización**: Datos de maestría duplicados implícitamente en interacciones y TopicMastery
2. **Consistencia eventual**: El average_test_score usa actualización incremental que puede diverger con errores
3. **Límite de temas**: Con muchos temas por asignatura, el documento podría crecer significativamente

### Mitigaciones

- Límite de 50 interacciones recientes controla tamaño del documento
- Conversaciones completas en colección separada permite análisis detallado sin inflar perfiles
- Índices compuestos `(user_id, subject)` para queries de dashboard de profesor

## Alternatives Considered

### 1. Schema relacional en PostgreSQL

**Rechazado**

- Requeriría nueva dependencia de infraestructura
- MongoDB ya establecido para guías docentes ([ADR 0010](0010-use-mongodb-for-guia-docente.md))
- Joins serían necesarios para cada consulta de perfil

### 2. Perfil completo con todo el historial

**Rechazado**

- Riesgo de superar límite de 16MB de MongoDB
- Queries de perfil serían lentas con historial extenso
- No necesario: análisis detallado usa colección `conversations`

### 3. Cache en Redis + persistencia en MongoDB

**Considerado para futuro**

- Útil si latencia de lectura de perfil se vuelve crítica
- Añade complejidad de sincronización
- Actualmente no necesario dado volumen esperado

### 4. Event sourcing para historial

**Considerado para futuro**

- Permitiría reconstruir estado en cualquier punto del tiempo
- Complejidad adicional significativa
- Útil si se requiere auditoría detallada

## Implementation

### Archivos principales

| Archivo | Propósito |
|---------|-----------|
| `chatbot/logic/profile_manager.py` | ProfileManager con CRUD y actualizaciones atómicas |
| `chatbot/logic/models/student_profile.py` | Modelos Pydantic para StudentProfile, Interaction, etc. |
| `chatbot/db/mongo.py` | Cliente MongoDB compartido |

### Operaciones MongoDB típicas

```python
# Registro de interacción (atómico)
collection.update_one(
    {"_id": user_id},
    {
        "$set": {"updated_at": now},
        "$inc": {
            "total_interactions": 1,
            "difficulty_distribution.intermediate": 1,
            "subject_mastery.iv.docker.interactions_count": 1
        },
        "$push": {
            "recent_interactions": {
                "$each": [interaction.model_dump()],
                "$slice": -50  # Keep only last 50
            }
        }
    },
    upsert=True
)
```

### Índices recomendados

```javascript
// Perfiles (colección principal)
db.student_profiles.createIndex({ "_id": 1 })  // Default

// Conversaciones (para análisis)
db.conversations.createIndex({ "session_id": 1 })
db.conversations.createIndex({ "user_id": 1, "timestamp": -1 })
db.conversations.createIndex({ "subject": 1, "difficulty": 1 })
```

## References

- [ADR 0010](0010-use-mongodb-for-guia-docente.md): Decisión de usar MongoDB
- [ADR 0029](0029-shared-mongodb-with-separate-collections.md): Arquitectura MongoDB compartida
- [ADR 0035](0035-adaptive-chain-of-thought.md): Usa perfil para determinar CoT
- [ADR 0036](0036-clustering-algorithms.md): Clasificación de dificultad que alimenta el perfil
