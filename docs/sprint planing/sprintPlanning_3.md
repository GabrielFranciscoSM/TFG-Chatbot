---
layout: default
title: Sprint Planning 3
parent: Sprint Planning
grand_parent: DevLog
---

# Sprint Planning - Sprint 3

## Información General

- **Sprint:** Sprint 3
- **Fecha de inicio:** 17 de noviembre de 2025
- **Fecha de finalización:** 1 de diciembre de 2025
- **Duración:** 2 semanas 
- **Equipo:** Gabriel Francisco

---

## Objetivo del Sprint (Sprint Goal)

> Implementar un sistema de autenticación y autorización que permita distinguir y gestionar accesos para `estudiante` y `profesor` en el TFG Chatbot.

El objetivo es asegurar que las rutas y funcionalidades sensibles estén protegidas y que existan flujos claros de registro, inicio de sesión y control de permisos.

---

## Alcance

- Registro e inicio de sesión (email + contraseña).
- Autorización por rol (`estudiante`, `profesor`).
- Endpoints protegidos y dependencias para verificación de token.
- Pruebas unitarias e integración para los flujos de autenticación.

---

## Historias de Usuario (HU) asociadas

- **HU #7 y #8** — Registro / Login para estudiantes
- **HU #13** — Diferenciar permisos entre estudiantes y profesores; autorización por rol

---

## Criterios de Aceptación

- HU #7 y #8:
  - [ ] Un estudiante se puede registrar con email y contraseña.
  - [ ] El estudiante puede iniciar sesión y recibir un token válido.
  - [ ] Rutas de estudiante requieren autenticación.
  - [ ] Un profesor puede registrarse o ser registrado por un administrador.
  - [ ] El profesor inicia sesión y obtiene token con rol `profesor`.
  - [ ] Rutas de profesor requieren rol `profesor`.

- HU #13:
  - [ ] El sistema diferencia roles y aplica autorización por rol.
  - [ ] Tests para rutas protegidas y casos de permisos incorrectos.

---

## Tareas (desglose)

1. Diseño
    - Definir esquema de `User` (email, hashed_password, role, created_at).
    - Decidir mecanismo de tokens (JWT) y estrategia de expiración/refresh.

2. Backend — Implementación
    - Crear servicio de backend real
    - `POST /auth/register` (registro).
    - `POST /auth/login` (autenticación).
    - `GET /auth/me` (datos del usuario autenticado).
    - Hashing de contraseñas (usar `passlib` o `bcrypt`).
    - Generación y verificación de JWT (usar `python-jose` o similar).
    - Dependencia/middleware para rutas protegidas y verificación de roles.

3. Session-management
    - Crear un servicio para almacenar datos de sesión de cada alumno
    - Almacenar datos de sesión y configuración de profesores

3. Tests
    - Unitarios para registro y login.
    - Integración: acceso a rutas protegidas según rol.

4. Documentación y despliegue
    - Documentar endpoints en `README` y `docs`.
    - Añadir variables de entorno necesarias y actualizar `docker-compose` si procede.

---

## Estimaciones (puntos)

- Diseño: 2
- Backend implementación: 8
- Tests: 3
- Documentación/despliegue: 1
- **Total aproximado:** 14 puntos

---


## Riesgos y dependencias

- Dependencia de la base de datos para almacenar usuarios (ajustar si es MongoDB).
- Riesgo de seguridad si el hashing o manejo de tokens se configura mal.
- Integración con SSO o proveedores externos queda fuera de este sprint.

---

## Definition of Done

- Endpoints de registro/login implementados y documentados.
- Tokens generados y verificados correctamente en pruebas automatizadas.
- Rutas protegidas devuelven `401/403` cuando corresponde.
- Code review completado y merge en rama de desarrollo.

---

## Backlog del sprint (prioridad)
- Issue #67 — [DEV PROBLEM] No existe un esquema de usuario: No existe un esquema de usuario que normalice qué información debe guardarse / usarse. Enlace: [#67](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/67)
- Issue #68 — [DEV PROBLEM] No debemos guardar datos sensibles sin anonimizar: Hay datos que deben ser anonimizados y protegidos antes de almacenarse. Enlace: [#68](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/68)
- Issue #69 — [DEV PROBLEM] No existe una base de datos dónde poder guardar la información de autenticación: Necesitamos una base de datos adecuada para local, fácil configuración y compatible con microservicios para almacenar credenciales y perfiles. Enlace: [#69](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/69)
- Issue #70 — [DEV PROBLEM] Se deben de proteger acciones sólo disponibles para profesores: Implementar autorización por rol para evitar que alumnos accedan a funcionalidades de profesor. Enlace: [#70](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/70)
- Issue #71 — [DEV PROBLEM] Cada estudiante debe de tener asociado una sesión con sus chatbots activos y su configuración: Cada estudiante necesita sesiones persistentes para sus chatbots y configuración individual. Enlace: [#71](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/71)

> Nota: He actualizado los marcadores con los títulos y resúmenes extraídos de cada issue (todas están en estado `OPEN`). Puedo incluir más detalles del cuerpo de cada issue si lo deseas.
---

**Elaborado por:** Gabriel Francisco

**Fecha:** 17 de noviembre de 2025

---

