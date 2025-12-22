---
layout: default
title: "Use Prometheus for Infrastructure Metrics"
date: 2025-12-08
parent: Architecture Decision Records
nav_order: 31
---

# ADR 0031 — Use Prometheus for Infrastructure Metrics

## Status

Accepted

## Context

Necesitamos monitorizar la salud y rendimiento de los microservicios del TFG (Gateway, Chatbot, RAG Service). Las métricas requeridas incluyen:
- Latencia de requests HTTP
- Tasa de errores
- Requests por segundo
- Uso de recursos

## Decision

Utilizaremos **Prometheus** para recolección de métricas y **Grafana** para visualización.

### Componentes:
- **Prometheus**: Base de datos de series temporales con modelo pull
- **prometheus-fastapi-instrumentator**: Instrumentación automática de FastAPI
- **Grafana**: Visualización y dashboards

## Consequences

- **Pros:**
  - Estándar de industria para métricas de infraestructura.
  - Integración nativa con FastAPI y contenedores Docker.
  - Alerting integrado con Alertmanager.
  - Grafana permite unificar métricas + logs (con Loki).

- **Cons / Trade-offs:**
  - Modelo pull requiere que Prometheus pueda alcanzar los servicios.
  - Configuración de scraping puede ser compleja en entornos dinámicos.
  - Datos no diseñados para alta cardinalidad (user-level metrics).

## Alternatives considered

- **Datadog/New Relic:** Muy potentes pero propietarios y costosos.
- **InfluxDB + Telegraf:** Buena alternativa, pero menos ecosistema.
- **OpenTelemetry Metrics:** Emergente, pero Prometheus tiene mejor madurez.

## Implementation

```python
# En cada servicio FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'gateway'
    static_configs:
      - targets: ['backend:8000']
```

## References

- https://prometheus.io/
- https://grafana.com/
- https://github.com/trallnag/prometheus-fastapi-instrumentator
