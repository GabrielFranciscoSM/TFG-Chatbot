---
layout: default
title: Sprint Planning 5 - Logs y Monitorización
parent: Sprints
grand_parent: DevLog
nav_order: 5
---

# Sprint Planning - Sprint 5 (Logs y Monitorización)

## Información General

- **Sprint:** Sprint 5
- **Fecha de inicio:** 8 de diciembre de 2025
- **Fecha de finalización:** 29 de diciembre de 2025
- **Duración:** 3 semanas
- **Equipo:** Gabriel Francisco

---

## Objetivo del Sprint (Sprint Goal)

> Implementar un sistema completo de observabilidad que permita monitorizar el comportamiento del agente LLM y la infraestructura de servicios, preparando el terreno para las métricas y análisis del Milestone 6.

El objetivo es dotar al sistema de capacidades de logging estructurado, tracing de LLM, y monitorización de servicios para detectar problemas y analizar el uso del chatbot educativo.

---

## Alcance

- **Observabilidad LLM:** Phoenix + OpenInference para tracing de LangChain/LangGraph.
- **Logging estructurado:** JSON logging en todos los servicios Python.
- **Métricas de infraestructura:** Prometheus + Grafana para salud de servicios.
- **Alertas:** Configuración básica para detectar servicios caídos o errores.

### Stack Tecnológico Seleccionado
- **LLM Tracing:** Phoenix (Arize AI) + OpenInference
- **Logging:** python-json-logger
- **Metrics:** Prometheus + prometheus-fastapi-instrumentator
- **Log Aggregation:** Loki + Promtail
- **Visualization:** Grafana

---

## Historias de Usuario (HU) asociadas

- **HU #9** — [HU 011] Como desarrollador quiero obtener datos de uso para poder ofrecer métricas y análisis de estos datos.
- **HU #10** — [HU 012] Como administrador me gustaría recibir alertas si algún servicio funciona inadecuadamente para poder solucionarlo con la mayor brevedad.
- **HU #11** — [HU 013] Como desarrollador quiero monitorear los servicios de la aplicación para detectar problemas rápidamente.

---

## Criterios de Aceptación

- **Observabilidad LLM (HU #9):**
  - [ ] El chatbot envía traces a Phoenix con cada interacción.
  - [ ] Se visualizan los spans de LangGraph en la UI de Phoenix.
  - [ ] Los eventos pedagógicos se registran en MongoDB.

- **Logging (HU #9, #11):**
  - [ ] Todos los servicios Python emiten logs en formato JSON.
  - [ ] Los logs incluyen correlation ID para trazabilidad.
  - [ ] Los logs se agregan en Loki y son consultables desde Grafana.

- **Monitorización (HU #11, #10):**
  - [ ] Los servicios exponen endpoints `/metrics` para Prometheus.
  - [ ] Existe un dashboard de Grafana con salud del sistema.
  - [ ] Las alertas notifican cuando un servicio está caído.

---

## Tareas (desglose)

### Semana 1: Phoenix + Logging JSON
1. **Phoenix/OpenInference**
   - Añadir dependencias (arize-phoenix, openinference-instrumentation-langchain).
   - Crear módulo `chatbot/instrumentation.py`.
   - Añadir servicio Phoenix a docker-compose.yml.
   - Verificar traces en UI de Phoenix.

2. **Logging JSON**
   - Instalar python-json-logger en todos los servicios.
   - Crear configuración centralizada de logging.
   - Añadir correlation ID middleware.

### Semana 2: Prometheus + Loki
3. **Prometheus**
   - Añadir prometheus-fastapi-instrumentator a Gateway y RAG.
   - Exponer endpoints /metrics en cada servicio.
   - Configurar Prometheus para scraping.

4. **Loki + Promtail**
   - Añadir servicios Loki/Promtail a docker-compose.
   - Configurar Promtail para leer logs de containers.
   - Verificar logs en Grafana.

### Semana 3: Grafana + Alertas
5. **Dashboards**
   - Dashboard de salud del sistema.
   - Dashboard de métricas de uso.
   - Panel de logs en tiempo real.

6. **Alertas y Eventos**
   - Configurar alertas por servicio caído.
   - Implementar eventos de interacción pedagógica.
   - Persistir eventos en MongoDB.

---

## Estimaciones (puntos)

- Phoenix/OpenInference: 5
- Logging JSON: 5
- Prometheus + Loki: 8
- Grafana Dashboards: 5
- Alertas y Eventos: 5
- **Total aproximado:** 28 puntos

---

## Riesgos y dependencias

- **Complejidad de stack:** Muchos servicios nuevos (Phoenix, Loki, Prometheus, Grafana) pueden introducir complejidad operativa.
- **Recursos:** El stack de observabilidad consume memoria/CPU adicional.
- **Integración LangGraph:** OpenInference puede no capturar todos los spans de LangGraph automáticamente.

---

## Definition of Done

- Phoenix muestra traces del chatbot correctamente.
- Los logs de todos los servicios son JSON y están en Loki.
- Grafana tiene al menos 2 dashboards funcionales.
- Las alertas básicas están configuradas.
- Los ADRs están documentados.

---

## Backlog del sprint (prioridad)

- Issue #9 — [HU 011] Datos de uso y métricas. Enlace: [#9](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/9)
- Issue #10 — [HU 012] Alertas de servicio. Enlace: [#10](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/10)
- Issue #11 — [HU 013] Monitorización de servicios. Enlace: [#11](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/11)

---

**Elaborado por:** Gabriel Francisco

**Fecha:** 8 de diciembre de 2025

---
