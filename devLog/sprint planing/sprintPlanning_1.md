---
layout: default
title: Sprint Planning 1
parent: Sprint Planning
grand_parent: DevLog
---

# Sprint Planning - Sprint 1

## Información General

- **Sprint:** Sprint 1
- **Fecha de inicio:** 29 de septiembre de 2025
- **Fecha de finalización:** 10 de octubre de 2025
- **Duración:** 2 semanas (12 días laborables)
- **Equipo:** Gabriel Francisco

---

## Objetivo del Sprint (Sprint Goal)

> **Desarrollar un chatbot básico ReAct funcional que sirva como Producto Mínimo Viable (PMV) de un agente de IA para aplicaciones educativas.**

El sprint se enfoca en implementar la infraestructura base y los componentes esenciales de un agente conversacional con arquitectura ReAct (Reason-Action), incluyendo capacidad de razonamiento, uso de herramientas y memoria a corto plazo.

---

## Alcance del Sprint

### Milestone Asociado
- **Milestone 1:** Chatbot Básico ReAct

### Funcionalidades Planificadas

#### 1. Infraestructura de Inferencia
- Desplegar un modelo de lenguaje (SLM) en local utilizando vLLM
- Configurar el modelo para soportar function calling
- Optimizar para las limitaciones de hardware disponibles (≤5 GB VRAM)
- Contenerización con Docker

#### 2. Agente de IA con Arquitectura ReAct
- Diseñar e implementar un agente básico usando LangGraph
- Definir estados del agente: START, THINK, END
- Implementar lógica de razonamiento y selección de acciones
- Integrar el agente con el modelo de inferencia

#### 3. Sistema de Memoria a Corto Plazo
- Implementar persistencia de estado conversacional
- Configurar checkpointer para guardar el estado
- Establecer sistema de threads para conversaciones independientes
- Integrar base de datos para almacenamiento

#### 4. Sistema de Herramientas
- Definir herramientas básicas para el agente
- Implementar mecanismo de incorporación de herramientas
- Configurar el agente para seleccionar herramientas según la query

#### 5. API Backend
- Desarrollar API REST con FastAPI
- Implementar endpoints básicos: `/`, `/health`, `/chat`
- Documentar la API
- Habilitar interacción con el agente a través de HTTP

#### 6. Arquitectura de Microservicios
- Dockerizar el backend
- Configurar Docker Compose con múltiples servicios
- Establecer comunicación entre servicios (vLLM + Backend)

#### 7. Testing y Calidad
- Implementar tests unitarios para el agente
- Crear tests de integración para la API
- Configurar pytest y estructura de testing

#### 8. Documentación
- Establecer CHANGELOG siguiendo Keep a Changelog
- Implementar versionado semántico
- Configurar automatización de releases con GitHub Actions

---

## Product Backlog Items Seleccionados

### Issues Comprometidos

| ID | Título | Tipo | Estimación | Prioridad |
|----|--------|------|------------|-----------|
| #21 | Inferencia en local con vLLM | Feature | M | Alta |
| #22 | Configuración de vLLM adicional para uso de herramientas | Feature | S | Alta |
| #25 | Diseño e implementación de un agente chatbot básico | Feature | L | Alta |
| #26 | Memoria a corto plazo | Feature | M | Alta |
| #23 | Definición de herramientas básicas | Feature | S | Media |
| #24 | Incorporación de herramientas al agente | Feature | M | Media |

**Total de Issues:** 6

### Estimación de Esfuerzo
- **Small (S):** 1-2 días
- **Medium (M):** 2-4 días
- **Large (L):** 4-6 días

---

## Criterios de Aceptación

### Para el Sprint

El sprint se considerará exitoso cuando:

1. ✅ El sistema permita desplegar un modelo LLM en local con soporte de function calling
2. ✅ Exista un agente funcional con arquitectura ReAct capaz de procesar queries
3. ✅ El agente pueda mantener memoria de conversaciones mediante threads
4. ✅ El agente pueda seleccionar y usar herramientas de forma dinámica
5. ✅ La API REST esté operativa y permita interactuar con el agente
6. ✅ Todo el sistema esté contenerizado y sea desplegable con un solo comando
7. ✅ Exista una suite de tests que valide la funcionalidad básica
8. ✅ La documentación refleje el estado actual del proyecto

### Por Issue

#### Issue #21: Inferencia en local con vLLM
- [ ] vLLM ejecutándose en contenedor Docker
- [ ] Modelo LLM cargado y respondiendo a peticiones
- [ ] Consumo de recursos dentro de límites (≤5 GB VRAM)
- [ ] Endpoint de inferencia accesible

#### Issue #22: Configuración vLLM para herramientas
- [ ] Modelo soporta format de function calling
- [ ] Configuración de chat templates adecuada
- [ ] Pruebas exitosas de llamada a herramientas

#### Issue #25: Agente chatbot básico
- [ ] GraphAgent implementado con LangGraph
- [ ] Estados START, THINK, END definidos
- [ ] Flujo de ejecución funcional
- [ ] Integración con modelo de inferencia

#### Issue #26: Memoria a corto plazo
- [ ] Checkpointer configurado
- [ ] Base de datos para persistencia activa
- [ ] Sistema de threads funcionando
- [ ] Conversaciones independientes manteniendo contexto

#### Issue #23: Definición de herramientas básicas
- [ ] Al menos 2-3 herramientas básicas implementadas
- [ ] Documentación de cada herramienta
- [ ] Interfaz consistente para las herramientas

#### Issue #24: Incorporación de herramientas
- [ ] Herramientas integradas en el agente
- [ ] Agente selecciona herramienta apropiada según query
- [ ] Ejecución correcta de herramientas y procesamiento de resultados

---

## Riesgos Identificados

### Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Limitaciones de hardware impiden despliegue del modelo | Alta | Alto | Explorar SLMs, considerar inferencia híbrida (API + local) |
| Modelo no soporta function calling adecuadamente | Media | Alto | Investigar modelos alternativos con fine-tuning específico |
| Complejidad de implementación de memoria excede estimación | Media | Medio | Usar frameworks probados (LangGraph), simplificar alcance inicial |
| Problemas de integración entre vLLM y backend | Baja | Medio | Testing temprano de integración, documentación de APIs |

### Riesgos de Proceso

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Subestimación del tiempo requerido | Media | Medio | Priorizar funcionalidad core, dejar features secundarias para sprints posteriores |
| Cambios en requisitos durante el sprint | Baja | Bajo | Mantener foco en objetivo del sprint, postponer cambios no críticos |

---

## Definición de "Hecho" (Definition of Done)

Una funcionalidad se considera "Hecha" cuando:

1. ✅ El código está escrito y commiteado
2. ✅ Existen tests que validan la funcionalidad
3. ✅ Los tests pasan exitosamente
4. ✅ El código está integrado en la rama principal
5. ✅ La documentación está actualizada (README, CHANGELOG, comentarios)
6. ✅ La funcionalidad funciona en el entorno Docker
7. ✅ No existen bugs críticos conocidos

---

## Plan de Trabajo

### Semana 1 (29 Sep - 5 Oct)

**Días 1-2:** Infraestructura base
- Setup de vLLM con Docker
- Selección y despliegue de modelo inicial
- Configuración básica de function calling

**Días 3-4:** Agente básico
- Implementación de GraphAgent
- Definición de estados
- Integración con modelo

**Días 5-6:** Sistema de herramientas
- Definir herramientas básicas
- Integrar herramientas en agente
- Tests de uso de herramientas

### Semana 2 (6 Oct - 10 Oct)

**Días 7-8:** Memoria y ajustes
- Implementar memoria a corto plazo
- Ajustar modelo si es necesario (ej: cambio a Qwen)
- Tests de memoria conversacional

**Días 9-10:** API Backend
- Desarrollar API con FastAPI
- Implementar endpoints
- Tests de API

**Días 11-12:** Integración y documentación
- Dockerización completa
- Docker Compose final
- Documentación
- Release v0.1.0

---

## Recursos Necesarios

### Hardware
- Máquina con GPU (≥5 GB VRAM para desarrollo)
- Acceso a APIs alternativas para testing (opcional)

### Software
- Docker/Podman
- Python 3.12+
- vLLM
- LangGraph
- FastAPI
- MongoDB (o similar para checkpointing)

### Conocimiento
- Arquitecturas de agentes de IA
- LangGraph framework
- Function calling con LLMs
- Docker y microservicios
- Testing con pytest

---

## Dependencias Externas

1. **vLLM:** Framework de inferencia - crítico para el proyecto
2. **LangGraph:** Framework de agentes - crítico para implementación
3. **Modelo LLM:** Disponibilidad de modelo adecuado (instruct + function calling)
4. **Hardware:** Acceso a GPU con VRAM suficiente

---

## Ceremonias del Sprint

### Daily Scrum
- **Frecuencia:** Diario
- **Formato:** Documentado en markdown
- **Contenido:**
  - ¿Qué hice ayer?
  - ¿Qué haré hoy?
  - ¿Qué obstáculos encontré?
  - Links de interés / aprendizajes

### Sprint Review
- **Fecha:** 11 de octubre de 2025 (día posterior al cierre)
- **Objetivo:** Demostrar el incremento completado
- **Entregables:**
  - Sistema funcional end-to-end
  - Documentación del sprint
  - CHANGELOG actualizado
  - Release v0.1.0

### Sprint Retrospective
- **Integrada en Sprint Review**
- **Temas a cubrir:**
  - Qué funcionó bien
  - Qué se puede mejorar
  - Obstáculos encontrados y soluciones
  - Aprendizajes técnicos

---

## Métricas de Éxito

### Métricas Cuantitativas
- **Velocity:** 6 issues completados
- **Cobertura de tests:** >70% del código crítico
- **Issues bloqueados:** 0
- **Bugs críticos:** 0 al final del sprint

### Métricas Cualitativas
- Sistema desplegable con un solo comando
- Agente capaz de mantener conversaciones coherentes
- Documentación clara y actualizada
- Código modular y mantenible

---

## Notas Adicionales

### Consideraciones Técnicas
- Priorizar simplicidad sobre complejidad en esta primera iteración
- El objetivo es un PMV funcional, no un sistema completo
- La arquitectura debe ser extensible para futuros sprints
- Mantener bajo acoplamiento entre componentes

### Gestión del Proyecto
- Usar GitHub Projects para tracking visual
- Daily scrums documentados para seguimiento
- Issues bien definidos con criterios de aceptación claros
- Commits descriptivos y referenciando issues

---

## Compromisos del Equipo

**Como equipo de desarrollo, nos comprometemos a:**

1. Entregar un chatbot básico ReAct funcional al final del sprint
2. Mantener comunicación clara mediante daily scrums documentados
3. Priorizar calidad sobre cantidad de features
4. Mantener tests actualizados con cada cambio
5. Documentar decisiones técnicas importantes
6. Solicitar ayuda/investigar cuando aparezcan blockers

---

**Elaborado por:** Gabriel Francisco  
**Fecha:** 29 de septiembre de 2025  
**Última actualización:** 29 de septiembre de 2025  
**Estado:** ✅ Aprobado
