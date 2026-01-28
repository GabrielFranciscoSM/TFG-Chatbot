---
layout: default
title: Sprint 5
parent: Sprint Retrospectives
grand_parent: DevLog
---

# Retrospectiva - Sprint 5 (8 Dic 2025 — 22 Ene 2026)

## Resumen ejecutivo

El Sprint 5 se centró en **Observabilidad e Infraestructura de Monitorización**. Se implementó un stack completo de observabilidad incluyendo Phoenix para tracing de LLM, Prometheus/Grafana para métricas, Loki para logs, y AlertManager para alertas. También se añadió un sistema de eventos pedagógicos para analítica de uso del chatbot. El sprint extendió su duración original pero cumplió todos los objetivos.

---

## Qué funcionó bien ✅

- **LLM Observability:**
  - Phoenix + OpenInference capturan traces de LangGraph correctamente.
  - Spans visibles en la UI de Phoenix para debugging.

- **Stack de Métricas:**
  - Prometheus scrapea métricas de todos los servicios FastAPI.
  - Dashboards de Grafana (`system-health`, `logs`) funcionan correctamente.
  - prometheus-fastapi-instrumentator proporciona métricas automáticas (latencia, requests, errores).

- **Logging Estructurado:**
  - JSON logging con correlation IDs en todos los servicios.
  - Loki + Promtail agregan logs de containers.
  - Panel de logs en tiempo real en Grafana.

- **Alerting:**
  - AlertManager configurado con reglas de ServiceDown, HighErrorRate, HighLatency.
  - Integración correcta con Prometheus.

---

## Qué no funcionó / Qué salió mal ❌

- **Duración del Sprint:**
  - El sprint se extendió del 29 de diciembre al 22 de enero debido a disponibilidad limitada durante las vacaciones.

- **Loki Query Syntax:**
  - El dashboard de logs falló inicialmente por usar `.*` (vacío-compatible) en lugar de `.+`.

- **Pydantic Email Validation:**
  - El script de seeding de usuarios requirió ajustes (`.local` → `example.com`) por validación estricta de emails.

- **Pre-commit Hooks:**
  - Varios intentos de commit fallaron por ruff/mypy hasta refactorizar el script de seeding.

---

## Lecciones aprendidas 🧠

- **Loki Queries:** Siempre usar `.+` en lugar de `.*` para variables de Grafana con Loki.

- **Testing Temprano:** Los scripts de utilidad (seed_users.py) deben pasar linting desde el inicio.

- **ADRs:** Documentar decisiones de AlertManager junto con Prometheus/Grafana mantiene coherencia.

---

## Acciones a tomar (Sprint 6) ⏭️

1. **Analytics UI para Profesores (Prioridad Alta)**
   - Crear página de analytics en el frontend para visualizar eventos pedagógicos.
   - Responsable: Gabriel.

2. **Cerrar Issues de GitHub (Prioridad Alta)**
   - Cerrar issues #102-#108 con referencias a los commits.
   - Responsable: Gabriel.

3. **Tests de Integración (Prioridad Media)**
   - Añadir tests para verificar flujo completo de alertas y eventos.
   - Responsable: Gabriel.

4. **Documentación de Despliegue (Prioridad Media)**
   - Documentar cómo configurar alertas para producción (Slack/email).
   - Responsable: Gabriel.

---

## Métricas y estado del Sprint 📈

| Tarea | Estado |
|-------|--------|
| #102: Logging JSON estructurado | ✅ Completado |
| #103: Eventos pedagógicos en MongoDB | ✅ Completado |
| #104: Alertas en Grafana | ✅ Completado |
| #105: Reglas de alertas Prometheus | ✅ Completado |
| #106: Prometheus en Gateway y RAG | ✅ Completado |
| #107: Loki + Promtail | ✅ Completado |
| #108: Dashboards Grafana | ✅ Completado |

---

## Definition of Done ✅

- [x] Phoenix muestra traces del chatbot.
- [x] Logs JSON en todos los servicios, agregados en Loki.
- [x] Grafana tiene 2+ dashboards funcionales.
- [x] Alertas básicas configuradas (AlertManager).
- [x] ADRs documentados (0030-0034).

---

**Elaborado por:** Gabriel Francisco  
**Sprint:** Sprint 5 (08/12/2025 — 22/01/2026)  
**Fecha de creación:** 22 de enero de 2026
