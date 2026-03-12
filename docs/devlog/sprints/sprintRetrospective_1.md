---
layout: default
title: Sprint Retrospective 1
parent: Sprints
grand_parent: DevLog
nav_order: 11
---

# Sprint Review - Sprint 1

## Información General

- **Sprint:** Sprint 1
- **Fecha de inicio:** 29 de septiembre de 2025
- **Fecha de finalización:** 10 de octubre de 2025
- **Duración:** 2 semanas (12 días)
- **Objetivo del Sprint:** Desarrollar un chatbot básico ReAct funcional

---

## Objetivo del Sprint

Implementar un Producto Mínimo Viable (PMV) de un agente de IA que sirva como base para un chatbot educativo, utilizando una arquitectura ReAct (Reason-Action) con capacidad de usar herramientas y memoria a corto plazo.

---

## Incremento Alcanzado

### ✅ Funcionalidades Completadas

#### 1. **Infraestructura de Inferencia (Issues #21, #22)**
- Despliegue de modelo LLM en Docker utilizando vLLM
- Configuración del modelo Qwen2.5-1.5B-Instruct
- Optimización para hardware limitado (5 GB VRAM)
- Soporte para function calling

#### 2. **Agente de IA con Arquitectura ReAct (Issue #25)**
- Implementación de `GraphAgent` usando LangGraph
- Diseño de estados: START, THINK, END
- Integración con el modelo de inferencia
- Capacidad de razonamiento y selección de acciones

#### 3. **Sistema de Memoria a Corto Plazo (Issue #26)**
- Implementación de checkpointer para persistencia de estado
- Configuración de base de datos para almacenamiento
- Sistema de threads para conversaciones independientes
- Seguimiento de contexto conversacional

#### 4. **Sistema de Herramientas (Issues #23, #24)**
- Definición de herramientas básicas
- Integración de herramientas en el agente
- Selección adaptativa de herramientas según la query del usuario

#### 5. **API Backend**
- Desarrollo de API con FastAPI (`backend/api.py`)
- Endpoints implementados:
  - `/` - Endpoint raíz
  - `/health` - Estado del servicio
  - `/chat` - Interacción con el chatbot
- Documentación de la API

#### 6. **Arquitectura de Microservicios**
- Dockerización del backend
- Docker Compose con 2 servicios:
  - Servicio vLLM (inferencia)
  - Servicio Backend (API)
- Comunicación entre servicios en red interna

#### 7. **Testing**
- Suite de tests unitarios para el agente
- Tests de integración para la API
- Tests de infraestructura
- Configuración de pytest

#### 8. **Documentación y Versionado**
- Implementación de CHANGELOG siguiendo Keep a Changelog
- Versionado semántico (v0.1.0)
- GitHub Actions para releases automáticas
- GitHub Pages con tema Just the Docs (v0.1.2)
- Workflow de Jekyll para generación automática de documentación

### 📊 Métricas del Incremento

- **Issues completados:** 6/6 (100%)
- **Versión entregada:** v0.1.2
- **Cobertura de tests:** Implementada (unitarios, integración, infraestructura)
- **Servicios desplegados:** 2 (vLLM + Backend)

---

## Obstáculos Encontrados

### 🚧 Obstáculos Técnicos

#### 1. **Limitación de Hardware**
- **Descripción:** Disponibilidad de solo 5 GB de VRAM para el despliegue del modelo
- **Impacto:** Restricción en la selección de modelos disponibles
- **Resolución:** 
  - Selección de Small Language Models (SLM)
  - Optimización mediante vLLM
  - Consideración de inferencia híbrida (API + local) para desarrollo

#### 2. **Selección del Modelo Adecuado**
- **Descripción:** Dificultad para encontrar un modelo que cumpliera todos los requisitos:
  - Capacidad de seguir instrucciones (instruct)
  - Fine-tuned para function calling
  - Compatible con limitaciones de hardware
- **Impacto:** Necesidad de cambiar el modelo inicialmente seleccionado
- **Resolución:**
  - Investigación de paper "Small Language Models for Future AI Agents"
  - Migración a Qwen2.5-1.5B-Instruct
  - Actualización de configuraciones (Docker vLLM, .env, system prompt)

#### 3. **Comportamiento Inadecuado en Function Calling**
- **Descripción:** El modelo inicial no respondía correctamente a la llamada de herramientas
- **Impacto:** Retraso en la implementación de la API
- **Resolución:**
  - Cambio a modelo Qwen2.5-1.5B-Instruct con mejor soporte
  - Ajuste de prompts del sistema
  - Validación mediante tests

### 💡 Aprendizajes

1. **Viabilidad de SLMs:** Los Small Language Models son suficientes para aplicaciones agénticas en escenarios con recursos limitados
2. **Importancia de la selección de modelo:** La elección del modelo correcto es crítica para el function calling
3. **Testing temprano:** Implementar tests desde el inicio permite detectar problemas de integración rápidamente
4. **Arquitectura de microservicios:** La separación en contenedores facilita el desarrollo y mantenimiento

---

## Retrospectiva Técnica

### ✨ Lo que funcionó bien
- Uso de LangGraph para simplificar la implementación del agente
- Podman Compose para orquestar los servicios
- Metodología de documentación (Keep a Changelog + Versionado Semántico)
- Configuración de tests automatizados desde el inicio
- GitHub Projects para seguimiento ágil

### 🔄 Áreas de mejora
- Planificar mejor la selección de modelos antes de iniciar la implementación
- Considerar limitaciones de hardware en la fase de diseño
- Documentación continua durante el desarrollo (no solo al final)

---

## Demostración del Incremento

El incremento entregado incluye:

1. **Sistema funcional end-to-end:**
   - Usuario → API FastAPI → GraphAgent → vLLM → Respuesta
   
2. **Capacidades demostradas:**
   - Conversaciones con memoria a corto plazo
   - Uso de herramientas mediante arquitectura ReAct
   - Endpoints RESTful operativos

3. **Infraestructura desplegable:**
   - `podman-compose up` levanta todo el sistema
   - Servicios independientes y escalables

---

## Próximos Pasos

Para el siguiente sprint se consideran las siguientes mejoras:
- Expansión del conjunto de herramientas disponibles
- Optimización del rendimiento del modelo
- Ampliación de la cobertura de tests

---

## Conclusión

El Sprint 1 ha sido completado exitosamente, alcanzando el objetivo de implementar un chatbot básico ReAct funcional. A pesar de los obstáculos técnicos relacionados con las limitaciones de hardware y la selección del modelo, se logró entregar un incremento de producto completamente funcional con todos los componentes esenciales: agente de IA, sistema de memoria, herramientas, API backend y arquitectura de microservicios.

El producto está listo para ser utilizado como base para iteraciones futuras y cumple con los criterios de aceptación definidos en la Sprint Planning.

---

**Versión del producto:** v0.1.2  
**Estado:** ✅ Completado  
**Fecha de revisión:** 11 de octubre de 2025
