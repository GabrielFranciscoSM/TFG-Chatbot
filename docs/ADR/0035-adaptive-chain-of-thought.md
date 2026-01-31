---
adr: 0035
title: "Adaptive Chain-of-Thought Prompting"
date: 2026-01-30
status: Accepted
layout: default
parent: Architecture Decision Records
nav_order: 35
---

# ADR 0035 — Adaptive Chain-of-Thought Prompting

## Status

Accepted

## Context

El chatbot pedagógico necesita proporcionar respuestas de mayor calidad para preguntas complejas (conceptuales, analíticas, resolución de problemas) mientras mantiene baja latencia para consultas simples (saludos, preguntas factuales).

Chain-of-Thought (CoT) prompting mejora significativamente la calidad de razonamiento en LLMs, pero añade latencia y verbosidad que no siempre es necesaria.

## Decision

Implementar CoT adaptativo que:

1. **Clasifica consultas** usando heurísticas (keywords, patrones regex)
2. **Aplica CoT selectivamente** solo para consultas complejas
3. **Parsea respuestas estructuradas** con tags `<thinking>` y `<answer>`
4. **Almacena razonamiento** en el estado para debugging/análisis

## Consequences

### Pros
- Mejor calidad de respuestas para preguntas complejas
- Baja latencia mantenida para consultas simples
- Razonamiento disponible para análisis y mejora continua
- Sin dependencia de LLM adicional para clasificación

### Cons
- Clasificador heurístico puede tener falsos positivos/negativos
- Complejidad adicional en el parsing de respuestas
- El modelo debe seguir el formato estructurado

## Alternatives Considered

1. **CoT siempre activo**: Rechazado por latencia innecesaria en consultas simples
2. **Clasificador basado en LLM**: Rechazado por añadir ~200ms de latencia
3. **Sin CoT**: Rechazado por pérdida de calidad en respuestas complejas

## Implementation

- `chatbot/logic/difficulty.py`: Clasificador de dificultad (BASIC/INTERMEDIATE/ADVANCED)
  - CoT se activa automáticamente para preguntas ADVANCED
- `chatbot/logic/prompts.py`: `SYSTEM_PROMPT_COT` con formato estructurado + prompts adaptativos
- `chatbot/logic/graph.py`: `think()` modificado para CoT adaptativo basado en dificultad

**Nota**: El clasificador `query_classifier.py` fue eliminado y consolidado con `difficulty.py` (Feb 2026).

## References

- [Investigación CoT](../investigacion/chain-of-thought/README.md)
- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in LLMs" (2022)
