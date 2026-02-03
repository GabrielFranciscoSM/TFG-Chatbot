---
layout: default
title: "Use Grafana for Visualization"
date: 2026-01-09
parent: Architecture Decision Records
nav_order: 33
---

# ADR 0033 — Use Grafana for Visualization

## Status

Accepted

## Context

El stack de observabilidad del TFG incluye Prometheus para métricas de infraestructura (ADR-0031) y Loki para agregación de logs (ADR-0032). Necesitamos una plataforma de visualización que permita:
- Dashboards unificados para métricas y logs
- Alertas visuales y notificaciones
- Exploración interactiva de datos
- Provisioning declarativo de configuración

## Decision

Utilizaremos **Grafana** como plataforma única de visualización para métricas (Prometheus) y logs (Loki).

### Componentes:
- **Grafana**: Plataforma open-source de visualización y observabilidad
- **Provisioning**: Configuración declarativa de datasources y dashboards
- **Dashboards JSON**: Dashboards versionados en Git

## Consequences

- **Pros:**
  - Unifica visualización de métricas y logs en una sola UI.
  - Integración nativa con Prometheus y Loki (mismo ecosistema Grafana Labs).
  - Provisioning declarativo permite configuración como código.
  - Amplia comunidad con dashboards pre-construidos disponibles.
  - Self-hosted (privacidad de datos).

- **Cons / Trade-offs:**
  - Añade un servicio más al stack de infraestructura.
  - Requiere configuración inicial de datasources y dashboards.
  - Curva de aprendizaje para crear dashboards complejos.

## Alternatives considered

- **Prometheus UI:** Incluida en Prometheus, pero muy básica para dashboards.
- **Kibana:** Potente para logs, pero requiere Elasticsearch (no Loki).
- **Datadog/New Relic:** SaaS propietarios, no self-hosted.
- **Chronograf:** Buena opción para InfluxDB, pero no para Prometheus/Loki.

## Implementation

```yaml
# docker-compose.yml
grafana:
  image: docker.io/grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:-admin}
    GF_USERS_ALLOW_SIGN_UP: "false"
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/provisioning:/etc/grafana/provisioning
  depends_on:
    - prometheus
    - loki
```

```yaml
# grafana/provisioning/datasources/datasources.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    url: http://loki:3100
```

### Estructura de provisioning:
```
grafana/provisioning/
├── dashboards/
│   ├── dashboards.yml       # Configuración del provider
│   └── json/
│       ├── logs.json        # Dashboard de logs
│       └── system-health.json  # Dashboard de salud del sistema
└── datasources/
    └── datasources.yml      # Configuración de datasources
```

## References

- https://grafana.com/
- https://grafana.com/docs/grafana/latest/administration/provisioning/
- https://grafana.com/docs/loki/latest/
- ADR-0031: Use Prometheus for Infrastructure Metrics
- ADR-0032: JSON Structured Logging
