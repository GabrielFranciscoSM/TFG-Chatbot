---
layout: default
title: Sprint Retrospective 2
parent: Sprint Retrospective
grand_parent: DevLog
---

# Retrospectiva - Sprint 2 (14 Oct 2025 — 28 Oct 2025)

## Resumen ejecutivo

Durante el Sprint 2 se avanzó de forma significativa en la implementación de un servicio RAG y en la preparación de herramientas educativas clave (scraper de guías docentes, integración con el grafo y generador de tests). Se implementó la primera iteración del microservicio RAG (API, chunking, embeddings, indexación y búsqueda), se dockerizó el stack y se definieron las decisiones técnicas principales (Qdrant, `nomic-embed-text`, LangChain, FastAPI). También se diseñó y comenzó el scraper para guías docentes (5 guías de prueba recogidas) y se refactorizó el grafo para admitir herramientas con metadata y flujos compuestos.

---

## Qué funcionó bien ✅

- Implementación rápida y modular del servicio RAG:
  - Endpoints `/index`, `/search`, `/health`, `/collection/info` ya disponibles.
  - Chunking inteligente (configurable) y preservación de metadata en chunks.
  - Integración inicial con Qdrant y embeddings (`nomic-embed-text`) mediante Ollama.
  - Documentación y Dockerización preparadas (servicio `rag-service`, `qdrant`, `ollama`).

- Refactor del grafo (`backend/logic/graph.py`) para admitir herramientas más ricas y multi-step, facilitando la integración del RAG como herramienta reusable.

- Progresos en el scraper de guías docentes:
  - Identificación de patrones en la UGR, recolección de ~5 guías HTML para pruebas.
  - Diseño del esquema JSON de salida (metadatos y secciones académicas).

- Buenas prácticas adoptadas:
  - Diseño modular separado entre embeddings, vector store y procesador de documentos.
  - Uso de Pydantic para configuración y modelos (planificado/implementado en parte).
  - Logging estructurado y documentación técnica (notas del RAG Service Stack).

---

## Qué no funcionó / Qué salió mal ❌

- Suite de tests incompleta: aunque el servicio está implementado, faltan tests unitarios e integración robustos. Esto reduce confianza para cambios agresivos.

- Dependencias de infra no totalmente verificadas en entorno automatizado:
  - Falta confirmar que Ollama tenga el modelo `nomic-embed-text` pre-cargado en todos los entornos (script `init_ollama.sh` necesita validación adicional).

- Estrategia de generación de IDs para vectores aún no estabilizada (riesgo de colisiones en reindexaciones).

- Variabilidad en el HTML de las guías UGR implica que el scraper requiere adaptadores o heurísticas más robustas; el scraping aún no está totalmente automatizado ni testeado en producción.

- Falta de pruebas end-to-end que cubran la integración completa RAG → grafo → respuesta final del agente.

---

## Lecciones aprendidas 🧠

- Priorizar tests tempranos: implementar una suite mínima antes de expandir funcionalidades facilita refactorizaciones seguras.

- Elegir un stack probado y modular facilita iterar rápido (decisión acertada: Qdrant + LangChain + FastAPI).

- Chunking y metadatos son críticos para la relevancia del RAG; el tamaño/overlap debe validarse con datos reales.

- Mantener separación de responsabilidades (embeddings, vector store, processor) reduce acoplamientos y facilita debugging.

- Incluso en proyectos individuales, documentar decisiones técnicas (ADRs/notes) amortigua la deuda técnica futura.

---

## Acciones a tomar (Sprint 3 / ASAP) ⏭️

1. Tests y calidad (Prioridad Alta)
   - Crear y asegurar tests unitarios para: `document_processor`, `embeddings`, `vector_store` y endpoints del RAG.
   - Implementar tests de integración básicos (indexación → búsqueda → retrieval) con datos de ejemplo.
   - Cobertura objetivo inicial: >= 70% en módulos críticos.
   - Responsable: Gabriel.

2. Robustecer infra y bootstrap (Prioridad Alta)
   - Verificar y automatizar la carga del modelo en Ollama en `init_ollama.sh` (comprobación y error claro si falta el modelo).
   - Implementar generación de IDs robusta (UUID o hash de doc+chunk) para evitar colisiones en reindexaciones.
   - Responsable: Gabriel.

3. Scraper de guías docentes (Prioridad Media-Alta)
   - Finalizar `tools/ugr_scraper.py` con manejo de variabilidad (selectores por facultad, heurísticas, fallback de texto), caching y respeto a `robots.txt`.
   - Escribir tests unitarios con HTML de ejemplo y guardar HTML crudo en `rag_service/documents/raw/ugr/`.
   - Indexar las 5 guías de prueba en el RAG y evaluar relevancia de recuperaciones.
   - Responsable: Gabriel.

4. Integración grafo ↔ RAG (Prioridad Media)
   - Definir Pydantic models claros para entradas/salidas del RAG y del grafo.
   - Añadir tests de integración que cubran registro/invocación de la herramienta RAG desde el grafo.
   - Si surgen incompatibilidades, añadir adaptadores de compatibilidad.
   - Responsable: Gabriel.

5. Observabilidad y métricas (Prioridad Media)
   - Implementar logging estructurado para medir latencias, tasa de aciertos (manuales iniciales), y uso de herramientas.
   - Empezar a capturar métricas básicas: tiempo indexado, tiempo búsqueda, número de documentos indexados, relevancia manual spot-check.
   - Responsable: Gabriel.

6. Refinamiento del prompt y evaluación (Prioridad Media)
   - Continuar iteraciones del System Prompt (v2, v3...) y mantener un pequeño set de casos de prueba para comparar calidad.
   - Documentar cambios y resultados (A/B manual).
   - Responsable: Gabriel.

---

## Métricas y estado del Sprint 📈

- Issues comprometidos: 9 (6 features + 3 user stories) — según Sprint Planning.
- Estado principal:
  - RAG service: Implementado (primer iter) — ✅ funcional pero sin tests completos.
  - Scraper: Esqueleto implementado y 5 guías recogidas — 🔶 en progreso.
  - Grafo adaptado para herramientas: ✅ refactor realizado.
- Prioridad inmediata: completar tests y automatizar bootstrapping de infra.

---

## Acciones concretas con plazos y definición de "Hecho"

- Tests unitarios para RAG: implementar durante la primera semana del Sprint 3. Hecho cuando la suite pasa en CI/local y cobertura mínima alcanzada.
- Validación de Ollama/modelos: script `init_ollama.sh` actualizado y probado — Hecho cuando detecte y cargue o falle con mensaje instructivo.
- Scraper robusto: Hecho cuando 5 guías puedan procesarse automáticamente y sus datos indexarse en RAG sin intervención manual.
- Integración grafo↔RAG: Hecho cuando exista un test E2E que demuestre retrieval → generation vía grafo.

---

## Reconocimientos 🙌

- Buen avance en poco tiempo: la implementación inicial del servicio RAG fue ambiciosa y significativamente completa para un primer iter.
- La documentación y Dockerización permiten reproducir y continuar trabajo con menos fricción.

---

## Próximos pasos (breve)

1. Priorizar y completar la suite de tests.
2. Harden infra (Ollama + modelos, ID strategy).
3. Finalizar scraper y comenzar indexación real de guías docentes.
4. Añadir pruebas de integración que cubran el flujo RAG → grafo → respuesta.
5. Iterar prompts y medir calidad con casos de prueba.

---

**Elaborado por:** Gabriel Francisco  
**Sprint:** Sprint 2 (14/10/2025 — 8/11/2025)  
**Fecha de creación:** 12 de noviembre de 2025
