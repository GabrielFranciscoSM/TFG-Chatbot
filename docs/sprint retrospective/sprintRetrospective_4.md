---
layout: default
title: Sprint 4
parent: Sprint Retrospectives
grand_parent: DevLog
---

# Retrospectiva - Sprint 4 (25 Nov 2025 — 15 Dic 2025)

## Resumen ejecutivo

El Sprint 4 se centró en la **creación del Frontend completo** usando React, Vite, TypeScript y Tailwind CSS. Se implementó la interfaz de autenticación (login/registro), la interfaz de chat con historial de sesiones, y el dashboard de profesor con gestión de estudiantes y configuración del agente. El sprint fue exitoso, completando el Milestone 4 (Interfaz Educativa).

---

## Qué funcionó bien ✅

- **Stack Frontend:**
  - Inicialización exitosa con Vite + React + TypeScript.
  - Integración de Tailwind CSS y shadcn/ui para componentes profesionales.
  - Configuración de Biome para linting/formatting del frontend.

- **Autenticación:**
  - Formularios de Login y Registro con validación (React Hook Form + Zod).
  - Gestión de estado de autenticación con React Context + JWT.
  - Route Guards (`RequireAuth`, `PublicRoute`) funcionando correctamente.

- **Interfaz de Chat:**
  - Sidebar con historial de sesiones.
  - Renderizado de Markdown en respuestas del bot.
  - Integración con endpoints del backend (chat, sessions).
  - Manejo de estados de carga con Skeletons.

- **Dashboard de Profesor:**
  - Tarjetas de estadísticas (estudiantes, sesiones).
  - Tabla de estudiantes con paginación.
  - Formulario de configuración del agente (System Prompt, temperatura).

---

## Qué no funcionó / Qué salió mal ❌

- **Curva de Aprendizaje:**
  - shadcn/ui y Radix UI requirieron tiempo de adaptación para entender el sistema de componentes.
  - TanStack Query requirió ajustes para integración correcta con el contexto de autenticación.

- **Integración Backend:**
  - Problemas iniciales de CORS que requirieron configuración adicional en el Gateway.
  - Ajustes en el formato de respuestas del backend para alinearse con las expectativas del frontend.

- **Responsive Design:**
  - Se dedicó más tiempo del esperado a ajustes para dispositivos móviles.

---

## Lecciones aprendidas 🧠

- **Component-First:** El enfoque de shadcn/ui (copiar componentes al proyecto) permite mayor personalización pero requiere entender bien la estructura base.

- **API Contract:** Definir un contrato claro de API (tipos TypeScript compartidos o OpenAPI) desde el inicio habría reducido los ajustes de integración.

- **Testing Frontend:** No se implementaron tests de componentes en este sprint. Priorizar Vitest + Testing Library en futuros sprints.

---

## Acciones a tomar (Sprint 5) ⏭️

1. **Observabilidad LLM (Prioridad Alta)**
   - Implementar Phoenix + OpenInference para tracing del agente.
   - Responsable: Gabriel.

2. **Logging Estructurado (Prioridad Alta)**
   - Configurar logging JSON en todos los servicios backend.
   - Responsable: Gabriel.

3. **Stack de Métricas (Prioridad Media)**
   - Añadir Prometheus + Grafana para monitorización de infraestructura.
   - Responsable: Gabriel.

4. **Tests Frontend (Prioridad Media)**
   - Implementar tests de componentes críticos con Vitest.
   - Responsable: Gabriel.

---

## Métricas y estado del Sprint 📈

- **Estado principal:**
  - Interfaz de Chat: ✅ Completado.
  - Autenticación Frontend: ✅ Completado.
  - Dashboard Profesor: ✅ Completado.
  - Configuración del Agente: ✅ Completado.
  - Tests Frontend: ⚠️ Pendiente.

---

**Elaborado por:** Gabriel Francisco
**Sprint:** Sprint 4 (25/11/2025 — 15/12/2025)
**Fecha de creación:** 8 de diciembre de 2025
