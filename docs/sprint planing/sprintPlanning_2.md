---
layout: default
title: Sprint Planning 2
parent: Sprint Planning
grand_parent: DevLog
---

# Sprint Planning - Sprint 2

## Información General

- **Sprint:** Sprint 2
- **Fecha de inicio:** 14 de octubre de 2025
- **Fecha de finalización:** 28 de octubre de 2025
- **Duración:** 2 semanas (15 días laborables)
- **Equipo:** Gabriel Francisco

---

## Objetivo del Sprint (Sprint Goal)

> **Enriquecer el chatbot con herramientas educativas específicas, implementando un sistema RAG y capacidades de acceso a información académica de la UGR, mejorando significativamente la calidad y contextualización de las respuestas.**

El sprint se enfoca en transformar el chatbot básico en un asistente educativo más robusto y especializado, proporcionando acceso a información fiable, contextualizada y útil para el ámbito académico universitario.

---

## Alcance del Sprint

### Milestone Asociado
- **Milestone 2:** Agente con herramientas específicas educativas

### Historias de Usuario (User Stories)

#### HU #4: Información de Fuentes Fiables
> Como profesor quiero que mis alumnos obtengan información de fuentes fiables para que no se desinformen.

**Relación con Issues:** #29, #30

#### HU #5: Información Básica de Asignaturas
> Como estudiante quiero que el chatbot me dé información básica sobre la asignatura para acceder fácilmente a esta.

**Relación con Issues:** #31

#### HU #6: Tests Interactivos para Estudio
> Como estudiante quiero que el chatbot me ayude a estudiar con tests interactivos para comprobar mi conocimiento.

**Relación con Issues:** #33, #34

### Funcionalidades Planificadas

#### 1. Sistema RAG (Retrieval-Augmented Generation)
**Objetivo:** Implementar un servicio independiente de RAG para proporcionar contexto específico y fiable a las respuestas del agente.

- Diseñar arquitectura del servicio RAG como microservicio
- Implementar pipeline de indexación de documentos
- Configurar base de datos vectorial (ChromaDB, Qdrant, o similar)
- Implementar modelo de embeddings (local o API)
- Crear herramienta de búsqueda semántica para el agente
- Contenerización del servicio RAG
- Integración con Docker Compose
- Tests de recuperación de información

#### 2. Herramienta: Web Scraper de Guías Docentes UGR
**Objetivo:** Extraer y procesar información administrativa y académica de las guías docentes de la Universidad de Granada.

- Investigar estructura del sitio web de guías docentes UGR
- Implementar scraper con Beautiful Soup / Scrapy
- Parsear información relevante:
  - Objetivos y competencias
  - Contenidos temáticos
  - Bibliografía
  - Criterios de evaluación
  - Horarios y profesorado
- Estructurar datos para indexación en RAG
- Implementar caché para evitar scraping repetitivo
- Manejar errores y páginas no disponibles
- Tests de scraping y parsing

#### 3. Herramienta: Generador de Tests Básicos
**Objetivo:** Crear tests de autoevaluación a partir de contenidos de las asignaturas.

- Diseñar formato de tests (opción múltiple, verdadero/falso, respuesta corta)
- Implementar lógica de generación usando el LLM
- Utilizar contexto del RAG para generar preguntas relevantes
- Implementar sistema de validación de respuestas (básico, sin interfaz)
- Almacenar tests generados para reutilización
- Tests unitarios de generación

#### 4. Mejora Continua del System Prompt
**Objetivo:** Optimizar iterativamente el comportamiento del agente mediante refinamiento del prompt del sistema.

- Definir criterios de evaluación de calidad de respuestas:
  - Precisión académica
  - Claridad y pedagogía
  - Uso apropiado de herramientas
  - Tono educativo
- Implementar versiones del system prompt:
  - v1: Énfasis en fuentes fiables y RAG
  - v2: Mejora de instrucciones de uso de herramientas
  - v3: Optimización de tono educativo y pedagógico
  - v4+: Ajustes según feedback y testing
- Documentar cambios y resultados de cada iteración
- A/B testing manual de diferentes versiones
- Establecer prompt final para el sprint

#### 5. Resolución de Issues de Calidad
**Objetivo:** Abordar problemas identificados en la iteración anterior.

- **#29:** Evitar desinformación de búsquedas generales
  - Priorizar uso de RAG sobre búsqueda web
  - Validar fuentes antes de presentar información
  
- **#30:** Mitigar información sesgada o incompleta
  - Implementar citas de fuentes en respuestas
  - Indicar nivel de confianza en la información
  
- **#31:** Acceso fácil a información académica UGR
  - Herramienta de scraping de guías docentes
  - Indexación en RAG
  
- **#32:** Respuestas contextualizadas por asignatura
  - RAG con documentos específicos por asignatura
  - Filtrado por metadatos (asignatura, curso, grado)
  
- **#33:** Expandir interacción más allá de texto
  - Generación de tests (sin interfaz aún)
  - Preparación para futuras mejoras multimedia
  
- **#34:** Medir utilidad de conversaciones
  - Diseñar métricas de evaluación
  - Implementar logging estructurado de interacciones

---

## Product Backlog Items Seleccionados

### Issues Comprometidos

| ID | Título | Tipo | Estimación | Prioridad | User Story |
|----|--------|------|------------|-----------|------------|
| #29 | Una búsqueda general en google puede dar como resultado desinformación | Feature | M | Alta | #4 |
| #30 | La información de internet puede estar sesgada o incompleta | Feature | M | Alta | #4 |
| #31 | El chatbot no tiene fácil acceso a información administrativa y académica de las asignaturas de la UGR | Feature | L | Alta | #5 |
| #32 | El chatbot no responde de forma contextualizada y personalizada para todas mis asignaturas | Feature | L | Alta | #5 |
| #33 | La interacción con el chatbot está limitada a enviar y recibir texto | Feature | M | Media | #6 |
| #34 | No puedo medir si las conversaciones que tengo con el chatbot me son útiles | Feature | S | Media | #6 |
| #4 | [HU 004] Como profesor quiero que mis alumnos obtengan información de fuentes fiables | User Story | - | Alta | - |
| #5 | [HU 005] Como estudiante quiero que el chatbot me dé información básica sobre la asignatura | User Story | - | Alta | - |
| #6 | [HU 006] Como estudiante quiero que el chatbot me ayude a estudiar con tests interactivos | User Story | - | Media | - |

**Total de Issues:** 9 (6 features + 3 user stories)

### Estimación de Esfuerzo
- **Small (S):** 1-2 días
- **Medium (M):** 2-4 días
- **Large (L):** 4-6 días

---

## Criterios de Aceptación

### Para el Sprint

El sprint se considerará exitoso cuando:

1. ✅ Exista un servicio RAG funcional integrado en la arquitectura de microservicios
2. ✅ El agente pueda consultar el RAG para obtener contexto específico en sus respuestas
3. ✅ La herramienta de scraping pueda extraer información de guías docentes de la UGR
4. ✅ La información de guías docentes esté indexada y disponible en el RAG
5. ✅ El agente pueda generar tests básicos de autoevaluación
6. ✅ El system prompt haya sido mejorado y optimizado al menos 3 veces
7. ✅ Las respuestas del chatbot citen fuentes y sean más contextualizadas
8. ✅ Existan métricas básicas para evaluar la utilidad de las conversaciones
9. ✅ Todo el sistema ampliado esté contenerizado y desplegable
10. ✅ La documentación refleje las nuevas capacidades

### Por Issue

#### Issue #29: Evitar desinformación de búsquedas generales
- [ ] RAG implementado como fuente primaria de información
- [ ] Sistema de priorización: RAG > fuentes verificadas > web general
- [ ] Warnings cuando la información viene de fuentes no verificadas
- [ ] Tests de comparación de calidad de respuestas

#### Issue #30: Mitigar información sesgada/incompleta
- [ ] Sistema de citación de fuentes en respuestas
- [ ] Indicadores de nivel de confianza
- [ ] Múltiples fuentes para información crítica
- [ ] Documentación de limitaciones conocidas

#### Issue #31: Acceso a información académica UGR
- [ ] Scraper funcional para guías docentes
- [ ] Al menos 5 guías docentes scrapeadas exitosamente
- [ ] Información estructurada y parseada correctamente
- [ ] Datos indexados en RAG
- [ ] Tests de extracción de información

#### Issue #32: Respuestas contextualizadas por asignatura
- [ ] RAG soporta filtrado por asignatura
- [ ] Metadatos de asignatura en documentos indexados
- [ ] Agente utiliza contexto de asignatura en respuestas
- [ ] Tests con queries específicas de asignaturas

#### Issue #33: Generación de tests interactivos
- [ ] Herramienta de generación de tests implementada
- [ ] Soporte para al menos 2 tipos de preguntas (ej: múltiple opción, V/F)
- [ ] Generación basada en contexto del RAG
- [ ] Sistema básico de validación de respuestas
- [ ] Al menos 3 tests de ejemplo generados

#### Issue #34: Métricas de utilidad de conversaciones
- [ ] Sistema de logging estructurado implementado
- [ ] Métricas definidas: relevancia, precisión, uso de herramientas
- [ ] Almacenamiento de métricas en base de datos
- [ ] Dashboard o reporte básico de métricas

---

## Riesgos Identificados

### Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Scraping bloqueado por el sitio de la UGR | Media | Alto | Implementar delays, respetar robots.txt, caché agresivo, considerar APIs oficiales |
| Rendimiento del RAG afecta tiempo de respuesta | Alta | Medio | Optimizar embeddings, usar índices eficientes, considerar caché de búsquedas frecuentes |
| Modelo de embeddings consume demasiados recursos | Media | Medio | Usar modelos ligeros, considerar API de embeddings, batch processing |
| Calidad de tests generados insuficiente | Media | Medio | Prompt engineering específico, validación humana inicial, templates de preguntas |
| Complejidad de integración RAG excede estimación | Media | Alto | Usar frameworks probados (LangChain, LlamaIndex), simplificar alcance inicial |

### Riesgos de Datos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Estructura de guías docentes cambia entre facultades | Alta | Medio | Parser flexible, múltiples estrategias de extracción, logging de errores |
| Información de guías docentes desactualizada | Media | Bajo | Timestamp de última actualización, sistema de re-scraping periódico |
| Volumen de datos para RAG muy grande | Baja | Medio | Estrategia de indexación incremental, limitación inicial a facultad/grado específico |

### Riesgos de Proceso

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Scope creep en mejoras de prompts | Alta | Medio | Limitar a 4 iteraciones máximo, definir criterios claros de "suficientemente bueno" |
| Tiempo de desarrollo de RAG subestimado | Media | Alto | Priorizar funcionalidad core, postponer optimizaciones avanzadas |

---

## Definición de "Hecho" (Definition of Done)

Una funcionalidad se considera "Hecha" cuando:

1. ✅ El código está escrito y commiteado
2. ✅ Existen tests que validan la funcionalidad (unitarios y/o integración)
3. ✅ Los tests pasan exitosamente
4. ✅ El código está integrado en la rama principal
5. ✅ La documentación está actualizada (README, CHANGELOG, docstrings)
6. ✅ La funcionalidad funciona en el entorno Docker/Compose
7. ✅ No existen bugs críticos conocidos
8. ✅ La funcionalidad ha sido probada manualmente con casos reales
9. ✅ Las métricas de rendimiento están dentro de límites aceptables

---

## Plan de Trabajo

### Semana 1 (14 Oct - 18 Oct)

#### Días 1-2: Setup RAG y primera iteración de prompts
- Investigar y seleccionar stack de RAG (ChromaDB/Qdrant + embeddings)
- Implementar estructura básica del servicio RAG
- Dockerizar servicio RAG
- **Iteración 1 de system prompt:** Enfoque en uso de RAG y fuentes fiables
- Tests básicos de RAG

#### Días 3-4: Scraper de guías docentes
- Análisis de estructura HTML de guías docentes UGR
- Implementar scraper básico
- Parsear información principal (objetivos, contenidos, bibliografía)
- **Iteración 2 de system prompt:** Mejora de instrucciones para herramientas
- Tests de scraping

#### Día 5: Integración RAG + Guías docentes
- Indexar guías docentes en RAG
- Crear herramienta de búsqueda en guías para el agente
- Pruebas de consultas específicas
- **Iteración 3 de system prompt:** Optimización de tono educativo

### Semana 2 (21 Oct - 28 Oct)

#### Días 6-7: Generador de tests básicos
- Diseñar estructura de tests
- Implementar generación con LLM + contexto RAG
- Sistema de validación básico
- Tests unitarios

#### Días 8-9: Métricas y logging
- Implementar sistema de logging estructurado
- Definir y capturar métricas de utilidad
- Crear reporte básico de métricas
- **Iteración 4 de system prompt:** Ajustes finales según testing

#### Días 10-11: Mejoras de calidad y citación de fuentes
- Implementar sistema de citación
- Indicadores de confianza en respuestas
- Validación de fuentes
- Testing end-to-end

#### Días 12-13: Integración final y testing
- Integración completa en Docker Compose
- Testing de todos los componentes juntos
- Ajustes de rendimiento
- Documentación técnica

#### Días 14-15: Documentación, release y cierre
- Actualizar README con nuevas capacidades
- Actualizar CHANGELOG
- Preparar release v0.2.0
- Sprint Review y retrospectiva

---

## Tareas Técnicas Identificadas

### Servicio RAG
- [ ] Seleccionar e instalar base de datos vectorial
- [ ] Configurar modelo de embeddings
- [ ] Implementar API del servicio RAG (endpoints: /index, /search)
- [ ] Crear Dockerfile para servicio RAG
- [ ] Añadir servicio RAG a docker-compose.yml
- [ ] Implementar pipeline de indexación de documentos
- [ ] Tests de indexación y búsqueda
- [ ] Documentar API del servicio RAG

### Scraper de Guías Docentes
- [ ] Investigar URLs y estructura HTML
- [ ] Crear `tools/ugr_scraper.py`
- [ ] Implementar extracción de metadatos (asignatura, curso, grado)
- [ ] Parsear contenido académico
- [ ] Implementar sistema de caché
- [ ] Manejo de errores y logging
- [ ] Tests con guías docentes reales
- [ ] Documentar uso del scraper

### Generador de Tests
- [ ] Diseñar esquema de tests (JSON/dict)
- [ ] Crear `tools/test_generator.py`
- [ ] Implementar prompts para generación de preguntas
- [ ] Integrar con RAG para contexto
- [ ] Sistema de validación de respuestas
- [ ] Tests unitarios de generación
- [ ] Ejemplos y documentación

### System Prompts
- [ ] Crear carpeta `logic/prompts/versions/`
- [ ] Implementar system_prompt_v1.py (énfasis RAG)
- [ ] Implementar system_prompt_v2.py (instrucciones herramientas)
- [ ] Implementar system_prompt_v3.py (tono educativo)
- [ ] Implementar system_prompt_v4.py (ajustes finales)
- [ ] Documentar cambios entre versiones
- [ ] Tests comparativos A/B

### Métricas y Logging
- [ ] Implementar logger estructurado
- [ ] Definir esquema de métricas
- [ ] Capturar eventos: consulta, respuesta, herramientas usadas, tiempo
- [ ] Almacenar en base de datos (MongoDB/PostgreSQL)
- [ ] Crear script de análisis básico
- [ ] Dashboard simple (opcional)

### Calidad de Respuestas
- [ ] Implementar `utils/citation_formatter.py`
- [ ] Añadir metadatos de fuente a respuestas RAG
- [ ] Formatear citas en respuestas del agente
- [ ] Indicadores de nivel de confianza
- [ ] Tests de formato de citación

### Integración y Deploy
- [ ] Actualizar docker-compose.yml con servicio RAG
- [ ] Variables de entorno para configuración RAG
- [ ] Script de setup inicial (indexación de datos base)
- [ ] Tests de integración end-to-end
- [ ] Documentación de deployment

---

## Recursos Necesarios

### Hardware
- Máquina con GPU (≥5 GB VRAM para desarrollo)
- Espacio en disco para base de datos vectorial (≥10 GB recomendado)
- Conexión a internet para scraping

### Software
- **Existentes:** Docker/Podman, Python 3.12+, vLLM, LangGraph, FastAPI
- **Nuevos:**
  - Base de datos vectorial (ChromaDB, Qdrant, o Faiss)
  - Beautiful Soup / Scrapy (web scraping)
  - Modelo de embeddings (sentence-transformers, OpenAI API, etc.)
  - LangChain o LlamaIndex (opcional, para RAG)
  - Requests / httpx (para scraping)

### Conocimiento
- Arquitecturas RAG (Retrieval-Augmented Generation)
- Web scraping y parsing HTML
- Bases de datos vectoriales y embeddings
- Prompt engineering avanzado
- Testing de modelos de lenguaje

### Datos
- Acceso a guías docentes de la UGR
- Documentos académicos para indexar en RAG (libros, apuntes, etc.)
- Ejemplos de tests educativos para referencia

---

## Dependencias Externas

1. **Sitio web de guías docentes UGR:** Disponibilidad y estabilidad - crítico para scraping
2. **Base de datos vectorial:** Rendimiento y escalabilidad - crítico para RAG
3. **Modelo de embeddings:** Calidad y velocidad - importante para RAG
4. **Hardware:** GPU y espacio en disco suficientes - crítico
5. **Documentos académicos:** Disponibilidad de material para indexar - importante

---

## Ceremonias del Sprint

### Daily Scrum
- **Frecuencia:** Diario (cuando sea posible)
- **Formato:** Documentado en markdown en `devLog/daily scrum/octubre/`
- **Contenido:**
  - ¿Qué hice ayer?
  - ¿Qué haré hoy?
  - ¿Qué obstáculos encontré?
  - Aprendizajes y links de interés
  - Iteración actual de prompts (si aplica)

### Sprint Review
- **Fecha:** 29 de octubre de 2025 (día posterior al cierre)
- **Objetivo:** Demostrar el incremento completado
- **Entregables:**
  - Demostración del RAG en acción
  - Ejemplos de scraping de guías docentes
  - Tests generados por el sistema
  - Comparación de versiones de prompts
  - Métricas recopiladas durante el sprint
  - CHANGELOG actualizado
  - Release v0.2.0

### Sprint Retrospective
- **Integrada en Sprint Review**
- **Temas a cubrir:**
  - Efectividad de las iteraciones de prompts
  - Desafíos técnicos del RAG
  - Lecciones aprendidas del scraping
  - Calidad de los tests generados
  - Áreas de mejora para Sprint 3

---

## Métricas de Éxito

### Métricas Cuantitativas
- **Velocity:** 9 issues (6 features + 3 user stories)
- **Iteraciones de prompt:** Mínimo 3, objetivo 4
- **Guías docentes scrapeadas:** Mínimo 5, objetivo 10+
- **Tests generados:** Mínimo 10 tests de ejemplo
- **Cobertura de tests de código:** >70%
- **Tiempo de respuesta con RAG:** <5 segundos
- **Precisión de recuperación RAG:** >80% de relevancia

### Métricas Cualitativas
- Respuestas más contextualizadas y precisas vs Sprint 1
- Citación clara de fuentes en respuestas
- Tests generados son pedagógicamente útiles
- Documentación clara de las nuevas capacidades
- Sistema RAG es reutilizable para otros dominios
- Código modular y bien estructurado

### Métricas de Usuario (iniciales)
- Relevancia percibida de respuestas (evaluación manual)
- Utilidad de información de guías docentes
- Calidad de tests generados (evaluación por experto)

---

## Notas Adicionales

### Consideraciones Técnicas

#### Sobre el RAG
- Comenzar con un dataset pequeño para validar pipeline
- Considerar chunking strategies para documentos largos
- Evaluar trade-off entre precisión y velocidad
- Documentar configuración de embeddings para reproducibilidad

#### Sobre el Scraping
- Respetar robots.txt y políticas del sitio
- Implementar delays entre requests (rate limiting)
- Caché agresivo para evitar re-scraping innecesario
- Considerar contactar con UGR para acceso a APIs oficiales en el futuro

#### Sobre los Prompts
- Mantener historial de todas las versiones
- Documentar decisiones de diseño de cada iteración
- Usar ejemplos concretos para evaluar mejoras
- Considerar crear suite de test cases para prompts

#### Sobre las Métricas
- Empezar simple, iterar después
- Priorizar métricas accionables
- Considerar privacidad en logging de conversaciones
- Preparar infraestructura para análisis futuro

### Gestión del Proyecto
- Priorizar funcionalidad core sobre perfección
- RAG básico funcional es más valioso que RAG perfecto sin terminar
- Documentar decisiones técnicas importantes (ADRs si es necesario)
- Mantener comunicación constante mediante daily scrums

### Extensibilidad Futura
- El servicio RAG debe ser reutilizable para otros tipos de documentos
- El scraper debe ser adaptable a otras fuentes (ej: bibliotecas, repositorios)
- El generador de tests debe soportar fácilmente nuevos tipos de preguntas
- Las métricas deben ser extensibles para análisis más profundo

---

## Compromisos del Equipo

**Como equipo de desarrollo, nos comprometemos a:**

1. Entregar un chatbot enriquecido con capacidades RAG y herramientas educativas específicas
2. Iterar el system prompt al menos 3 veces basándose en evidencia y testing
3. Priorizar calidad y utilidad pedagógica sobre cantidad de features
4. Mantener documentación actualizada de decisiones técnicas
5. Respetar buenas prácticas de web scraping y uso ético de datos
6. Implementar tests que garanticen la calidad de las nuevas funcionalidades
7. Buscar feedback temprano y ajustar según sea necesario

---

## Aprendizajes Esperados

Al final de este sprint, se espera haber adquirido conocimiento en:

- Arquitecturas y mejores prácticas de RAG
- Web scraping robusto y manejo de datos semi-estructurados
- Prompt engineering avanzado e iterativo
- Evaluación de calidad de respuestas de LLMs
- Integración de múltiples microservicios complejos
- Métricas y observabilidad en aplicaciones de IA

---

**Elaborado por:** Gabriel Francisco  
**Fecha:** 14 de octubre de 2025  
**Última actualización:** 14 de octubre de 2025  
**Estado:** ✅ Aprobado
