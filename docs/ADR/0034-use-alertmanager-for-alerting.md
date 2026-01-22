---
layout: default
title: "Use AlertManager for Alerting"
date: 2026-01-22
parent: Architecture Decision Records
nav_order: 34
---

# ADR 0034 — Use AlertManager for Alerting

## Status

Accepted

## Context

Con Prometheus recolectando métricas de infraestructura (ADR 0031), necesitamos un sistema para:
- Definir reglas de alertas basadas en métricas.
- Agrupar y deduplicar alertas.
- Enrutar notificaciones a diferentes canales (Slack, email, etc.).
- Silenciar alertas durante mantenimiento.

## Decision

Utilizaremos **Prometheus AlertManager** para gestionar las alertas del sistema.

### Reglas implementadas:
- **ServiceDown**: Servicio caído por >1 minuto (crítico).
- **HighErrorRate**: Tasa de errores 5xx >1% durante 5 minutos (warning).
- **HighLatency**: Latencia P95 >2 segundos durante 5 minutos (warning).

### Estructura de archivos:
```
alertmanager/
├── alertmanager.yml    # Configuración de rutas y receptores
└── alert_rules.yml     # Reglas de alertas (cargado por Prometheus)
```

## Consequences

- **Pros:**
  - Nativa de Prometheus, sin dependencias adicionales.
  - Grouping y deduplicación evitan "alert fatigue".
  - Soporta múltiples canales (Slack, PagerDuty, email, webhooks).
  - Interfaz web para silenciar alertas.

- **Cons / Trade-offs:**
  - Configuración YAML puede ser verbosa.
  - Requiere servicio adicional en docker-compose.
  - Sin historial de alertas persistente (solo activas).

## Alternatives considered

- **Grafana Alerting:** Integrado en Grafana 8+, pero menos flexible para rutas complejas.
- **PagerDuty/Opsgenie:** Más potentes pero propietarios y costosos.
- **Alertmanager silences via API:** Más automatizable que UI manual.

## Implementation

```yaml
# docker-compose.yml
alertmanager:
  image: prom/alertmanager:latest
  ports:
    - "9094:9093"
  volumes:
    - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

```yaml
# prometheus.yml
rule_files:
  - /etc/prometheus/alert_rules.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

```yaml
# alertmanager/alert_rules.yml
groups:
  - name: service_health
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
```

## References

- https://prometheus.io/docs/alerting/latest/alertmanager/
- https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
