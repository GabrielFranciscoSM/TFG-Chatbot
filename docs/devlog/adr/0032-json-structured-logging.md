---
layout: default
title: "Use JSON Structured Logging"
date: 2025-12-08
parent: Architecture Decision Records
nav_order: 32
---

# ADR 0032 — Use JSON Structured Logging

## Status

Accepted

## Context

Los servicios Python actualmente usan el módulo `logging` con formato de texto plano. Esto dificulta:
- Parseo automático de logs
- Correlación de requests entre servicios
- Agregación en sistemas como Loki o Elasticsearch
- Análisis y búsqueda de campos específicos

## Decision

Todos los servicios Python emitirán logs en **formato JSON estructurado** usando `python-json-logger`.

### Campos estándar:
- `timestamp`: ISO 8601
- `level`: DEBUG/INFO/WARNING/ERROR
- `message`: Mensaje del log
- `service`: Nombre del servicio
- `correlation_id`: ID de request para trazabilidad
- `extra`: Campos adicionales según contexto

## Consequences

- **Pros:**
  - Logs parseables automáticamente por Loki/ELK.
  - Correlación entre servicios mediante `correlation_id`.
  - Campos estructurados permiten queries precisas.
  - Compatible con estándar OpenTelemetry logging.

- **Cons / Trade-offs:**
  - Logs menos legibles directamente en terminal (mitigation: usar `jq`).
  - Requiere configuración adicional vs logging por defecto.
  - Verbosidad incrementada en bytes.

## Alternatives considered

- **Loguru:** Popular, pero introduce dependencia no estándar.
- **structlog:** Muy potente, pero curva de aprendizaje mayor.
- **OpenTelemetry Logging:** Aún inmaduro comparado con tracing/metrics.

## Implementation

```python
# logging_config.py
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
handler.setFormatter(formatter)
logging.root.addHandler(handler)
```

## References

- https://github.com/madzak/python-json-logger
- https://www.structlog.org/
- https://opentelemetry.io/docs/specs/otel/logs/
