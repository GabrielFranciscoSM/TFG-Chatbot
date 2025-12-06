---
layout: default
title: Sprint 3
parent: Sprint Retrospectives
grand_parent: DevLog
---

# Retrospectiva - Sprint 3 (11 Nov 2025 — 22 Nov 2025)

## Resumen ejecutivo

En el Sprint 3 el foco principal fue la **Gestión de Sesiones** y la estabilización del **CI/CD**. Se implementó la lógica completa de sesiones en el backend (CRUD, persistencia en MongoDB), permitiendo historiales de chat persistentes. Paralelamente, se realizó un esfuerzo significativo para arreglar y mejorar los pipelines de integración continua (GitHub Actions), resolviendo problemas de dependencias y aislamiento de tests en `rag_service` y `backend`. La infraestructura de contenedores se validó para incluir el nuevo servicio `chatbot`.

---

## Qué funcionó bien ✅

- **Gestión de Sesiones (Backend):**
  - Implementación exitosa de `backend/routers/sessions.py` con endpoints para crear, listar, obtener y eliminar sesiones.
  - Integración con MongoDB para persistencia de metadatos de sesión.
  - Actualización de `chat.py` para vincular interacciones a sesiones específicas.

- **Estabilización de Tests y CI:**
  - Resolución de fallos críticos en los tests de `rag_service` mediante el uso correcto de **mocks** para servicios externos (Qdrant, Ollama).
  - Solución a problemas de permisos en tests que intentaban escribir en directorios de sistema (`/app`), migrando a fixtures de directorios temporales.
  - Configuración correcta de `pytest-cov` en `pyproject.toml` para reportes de cobertura.

- **Infraestructura y Workflows:**
  - Actualización de workflows de GitHub Actions (`unit-tests.yml`, `build-containers.yml`) para soportar la arquitectura de 3 servicios (`backend`, `rag_service`, `chatbot`).
  - Verificación de builds de contenedores Docker/Podman exitosa.

---

## Qué no funcionó / Qué salió mal ❌

- **Infierno de Dependencias en CI:**
  - Se perdió tiempo depurando fallos de CI causados por dependencias de desarrollo faltantes (`pytest-cov`) en `pyproject.toml`, que no se manifestaban en el entorno local de la misma manera.
  
- **Aislamiento de Tests:**
  - Los tests iniciales de `rag_service` no estaban suficientemente aislados, intentando conectar a servicios reales o escribir en disco, lo que causó fallos en entornos limpios/CI. Fue necesario un refactor de `conftest.py` y varios tests.

- **Advertencias de Compatibilidad:**
  - Persisten warnings de `Pydantic V1` provenientes de librerías de terceros (`langsmith`), generando ruido en los logs de tests.

---

## Lecciones aprendidas 🧠

- **Mocking por Defecto:** Los tests unitarios no deben depender nunca de la disponibilidad de servicios externos (DBs, LLMs). El uso de `unittest.mock` y fixtures debe ser la norma desde el principio.
  
- **Entornos de CI vs Local:** Las discrepancias entre el entorno de desarrollo (a menudo "sucio" o con permisos completos) y el de CI (limpio, restringido) deben minimizarse. Probar la instalación de dependencias desde cero (`pip install .[dev]`) localmente ayuda a detectar problemas antes.

- **Gestión de Rutas en Tests:** Nunca asumir rutas absolutas o permisos de escritura en el código de tests. Usar siempre las fixtures de `tmp_path` de pytest.

---

## Acciones a tomar (Sprint 4 / ASAP) ⏭️

1. **Integración Frontend de Sesiones (Prioridad Alta)**
   - Actualizar la interfaz de usuario para permitir crear, seleccionar y borrar sesiones de chat, consumiendo los nuevos endpoints del backend.
   - Responsable: Gabriel.

2. **Autenticación Completa (Prioridad Alta)**
   - Finalizar el flujo de autenticación (JWT) en la rama `feature/autentication`. Asegurar que las sesiones estén estrictamente vinculadas a usuarios autenticados.
   - Responsable: Gabriel.

3. **Cobertura de Tests Chatbot (Prioridad Media)**
   - Extender la cobertura de tests unitarios al servicio `chatbot`, aplicando las lecciones aprendidas en `rag_service` (mocks para LangGraph/LLMs).
   - Responsable: Gabriel.

4. **Limpieza de Dependencias (Prioridad Baja)**
   - Revisar y actualizar dependencias para mitigar warnings de deprecación (Pydantic V1/V2), o configurar filtros de logs adecuados.
   - Responsable: Gabriel.

---

## Métricas y estado del Sprint 📈

- **Estado principal:**
  - Gestión de Sesiones: ✅ Completado (Backend).
  - CI/CD Pipelines: ✅ Reparados y funcionales.
  - Tests Unitarios: ✅ Pasando en Backend y RAG Service.
  - Autenticación: 🔶 En progreso (rama feature).

---

**Elaborado por:** Gabriel Francisco (con asistencia de GitHub Copilot)
**Sprint:** Sprint 3 (11/11/2025 — 22/11/2025)
**Fecha de creación:** 23 de noviembre de 2025
