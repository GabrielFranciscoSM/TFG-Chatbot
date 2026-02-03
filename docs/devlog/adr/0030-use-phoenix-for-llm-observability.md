---
layout: default
title: "Use Phoenix for LLM Observability"
date: 2025-12-08
parent: Architecture Decision Records
nav_order: 30
---

# ADR 0030 — Use Phoenix for LLM Observability

## Status

Accepted

## Context

El chatbot del TFG utiliza LangChain y LangGraph para orquestar conversaciones con LLMs. Necesitamos visibilidad sobre:
- Latencia de llamadas al LLM
- Tokens utilizados por interacción
- Flujo de ejecución del grafo conversacional
- Detección de problemas y alucinaciones

Las herramientas tradicionales (Prometheus, ELK) no están diseñadas para observabilidad de LLMs.

## Decision

Utilizaremos **Phoenix** (de Arize AI) con **OpenInference** para la observabilidad del agente LLM.

### Componentes:
- **Phoenix**: Plataforma open-source de observabilidad para LLMs
- **OpenInference**: Estándar de instrumentación basado en OpenTelemetry
- **LangChainInstrumentor**: Instrumentación automática de LangChain/LangGraph

## Consequences

- **Pros:**
  - Tracing automático de cadenas LangChain y grafos LangGraph.
  - UI dedicada para análisis de LLMs (no como Grafana que es genérico).
  - Visualización de tokens, latencia, y flujos de ejecución.
  - Self-hosted (privacidad de datos educativos).
  - Basado en estándares abiertos (OpenTelemetry/OpenInference).

- **Cons / Trade-offs:**
  - Añade un servicio más al stack de infraestructura.
  - Menor madurez que alternativas comerciales (LangSmith).
  - Requiere configuración de OTLP exporter.

## Alternatives considered

- **Langfuse:** Similar funcionalidad, mejor UI, pero menos análisis de embeddings.
- **LangSmith:** Oficial de LangChain, pero propietario y solo cloud.
- **OpenTelemetry + Jaeger:** Genérico, no optimizado para LLMs.

## Implementation

```python
# chatbot/instrumentation.py
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

LangChainInstrumentor().instrument()
```

## References

- https://docs.arize.com/phoenix
- https://github.com/Arize-ai/openinference
- https://opentelemetry.io/
