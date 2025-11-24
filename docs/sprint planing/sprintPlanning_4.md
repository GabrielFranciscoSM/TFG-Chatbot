---
layout: default
title: Sprint Planning 4 - UI Frontend
parent: Sprint Planning
grand_parent: DevLog
---

# Sprint Planning - Sprint 4 (UI Frontend)

## Información General

- **Sprint:** Sprint 4
- **Fecha de inicio:** 2 de diciembre de 2025
- **Fecha de finalización:** 23 de diciembre de 2025
- **Duración:** 3 semanas
- **Equipo:** Gabriel Francisco

---

## Objetivo del Sprint (Sprint Goal)

> Crear una interfaz frontend pulida y funcional en React para el TFG Chatbot, cubriendo Autenticación, Interacción de Chat y Dashboards de Profesor.

El objetivo es proporcionar una experiencia de usuario completa y profesional, permitiendo a los estudiantes interactuar con el chatbot y a los profesores gestionar sus clases y configuraciones.

---

## Alcance

- **Stack Tecnológico:** Definición y configuración del entorno (React, Vite, Tailwind, Shadcn).
- **Autenticación:** Implementación de flujos de Login y Registro.
- **Chat:** Interfaz de chat completa con historial y renderizado de Markdown.
- **Dashboard:** Panel de control para profesores con estadísticas y gestión de alumnos.
- **Configuración:** Interfaz para ajustar el comportamiento del agente y subir documentos (RAG).

### Stack Tecnológico Seleccionado
- **Framework:** React + Vite (TypeScript)
- **Styling:** Tailwind CSS
- **UI:** ShadCN UI
- **Forms:** React Hook Form + Zod
- **Navigation:** React Router DOM
- **Data/API:** TanStack Query + Axios
- **Auth:** Custom Context (JWT en localStorage/cookie)
- **Charts:** Recharts
- **Icons:** Lucide React

---

## Historias de Usuario (HU) asociadas

- **HU #12** — [HU 009] Como estudiante quiero que el chatbot tenga una interfaz amigable y se adapte a mis necesidades.
- **HU #13** — [HU 010] Como profesor quiero poder acceder facilmente a mis clases y ajustar opciones de uso del agente.

---

## Criterios de Aceptación

- **General:**
  - [ ] El proyecto frontend está inicializado y configurado con el stack seleccionado.
  - [ ] La navegación entre páginas es fluida y las rutas privadas están protegidas.

- **Autenticación (HU #12, #13):**
  - [ ] Los usuarios pueden registrarse con validación de contraseña.
  - [ ] Los usuarios pueden iniciar sesión y son redirigidos correctamente.

- **Chat (HU #12):**
  - [ ] El estudiante puede ver su historial de sesiones.
  - [ ] El estudiante puede enviar mensajes y recibir respuestas (con streaming si aplica).
  - [ ] Las respuestas del bot se renderizan correctamente (Markdown).

- **Dashboard y Configuración (HU #13):**
  - [ ] El profesor puede ver estadísticas de uso (gráficos).
  - [ ] El profesor puede ver la lista de estudiantes.
  - [ ] El profesor puede modificar el System Prompt y la temperatura.
  - [ ] El profesor puede subir archivos para el contexto (RAG).

---

## Tareas (desglose)

### Semana 1: Fundamentos y Autenticación
1. **Investigación y Configuración del Stack**
    - Revisar documentación (Shadcn, TanStack Query, React Router).
    - Inicializar proyecto (Vite + React TS).
    - Configurar Tailwind CSS y Shadcn/ui.
    - Instalar dependencias core (`axios`, `react-hook-form`, `zod`, `lucide-react`).
2. **Layout y Enrutamiento**
    - Implementar `AppShell` (Sidebar/Header).
    - Crear Route Guards (`RequireAuth`).
    - Definir rutas (`/login`, `/register`, `/chat`, `/admin/...`).
3. **Autenticación**
    - Crear formularios de Login y Registro con validación (`zod`).
    - Integrar con endpoints de backend (`/auth`).
    - Gestionar estado de sesión (Context + JWT).

### Semana 2: La Experiencia de Chat
4. **Layout del Chat**
    - Sidebar con historial de sesiones (`ScrollArea`).
    - Área principal de mensajes y entrada de texto.
5. **Lógica del Chat**
    - Componente de Mensaje (Estilos User vs AI, Markdown).
    - Gestión de sesiones (Crear, Cambiar).
    - Manejo de estados de carga/streaming.
6. **Integración Chat**
    - Conectar con `backend/routers/chat.py` y `sessions.py`.
    - Implementar Skeletons de carga.

### Semana 3: Dashboard de Profesor y Configuración
7. **Dashboard de Gestión**
    - Tarjetas de estadísticas (Estudiantes, Sesiones).
    - Tabla de estudiantes (Paginación/Búsqueda).
    - Gráficos de análisis (`Recharts`).
8. **Configuración del Agente**
    - Formulario de ajustes (System Prompt, Temperatura, Modelo).
    - Zona de carga de archivos (Drag & drop).
    - Integración con `backend/routers/admin.py`.
9. **Pulido Final**
    - Manejo de errores (Toasts).
    - Revisión de diseño responsivo.
    - Limpieza de código.

---

## Estimaciones (puntos)

- Configuración y Stack: 3
- Autenticación y Routing: 5
- Interfaz de Chat: 8
- Dashboard y Gráficos: 5
- Configuración y Archivos: 5
- Pulido y Tests: 4
- **Total aproximado:** 30 puntos (Sprint de 3 semanas)

---

## Riesgos y dependencias

- **Curva de aprendizaje:** El uso de Shadcn y TanStack Query puede requerir tiempo de adaptación.
- **Integración Backend:** Posibles problemas de CORS o formatos de respuesta no alineados.
- **Diseño UI:** Riesgo de dedicar demasiado tiempo a detalles visuales ("pixel perfect") en lugar de funcionalidad.

---

## Definition of Done

- Aplicación React funcional y desplegable localmente.
- Todos los flujos críticos (Auth, Chat, Config) funcionan contra el backend.
- Código limpio y organizado siguiendo las mejores prácticas del stack elegido.
- Documentación básica de cómo ejecutar el frontend.

---

## Backlog del sprint (prioridad)

- Issue #79 — [DEV PROBLEM] No existe una interfaz gráfica para el registro y el log in. Enlace: [#79](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/79)
- Issue #78 — [DEV PROBLEM] No existe una interfaz para poder interactuar con el chatbot. Enlace: [#78](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/78)
- Issue #81 — [DEV PROBLEM] No existe una interfaz gráfica para el manejo de una clase en su conjunto. Enlace: [#81](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/81)
- Issue #80 — [DEV PROBLEM] No existe una configuración básica sobre el comportamiento del agente. Enlace: [#80](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/80)
- Issue #12 — [HU 009] Como estudiante quiero que el chatbot tenga una interfaz amigable y se adapte a mis necesidades. Enlace: [#12](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/12)
- Issue #13 — [HU 010] Como profesor quiero poder acceder facilmente a mis clases y ajustar opciones de uso del agente. Enlace: [#13](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/13)

---

**Elaborado por:** Gabriel Francisco

**Fecha:** 24 de noviembre de 2025

---
