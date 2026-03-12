# Math Service Documentation Index

Documentación completa del microservicio Math del sistema TFG-Chatbot.

## Archivos de documentación

### 1. **[README.md](./README.md)** — Visión general y Quick Start

Punto de entrada para una introducción de alto nivel y guía de inicio rápido.

**Incluye:**
- Visión general del servicio y características principales
- Estructura de directorios
- Quick start (setup local en 5 minutos)
- Acceso a la documentación de la API
- Flujo de solicitudes
- Tareas comunes (cURL snippets)
- Troubleshooting

**Leer cuando:** Quieras una introducción rápida al Math Service

---

### 2. **[architecture.md](./architecture.md)** — Diseño del sistema

Análisis profundo de cómo está diseñado y estructurado el Math Service.

**Incluye:**
- Diagrama de arquitectura de alto nivel
- Componentes principales (API, Config, Servicios, Modelos)
- Modelos de datos (FAQ, TopicResult, ConceptMap)
- Flujo de generación de FAQs
- Flujo de extracción de tópicos
- Patrones de diseño utilizados
- Integración con `math_investigation`
- Colecciones MongoDB (`faqs`, `topics`)

**Leer cuando:** Quieras entender el diseño del sistema o añadir nuevas funcionalidades

---

### 3. **[api-endpoints.md](./api-endpoints.md)** — Referencia completa de la API

Documentación detallada de cada endpoint de la API.

**Incluye:**
- Endpoints generales (`GET /`, `GET /health`)
- Endpoints de FAQs (`POST /faqs/generate`, `GET /faqs/{subject}`, `PUT`, `PATCH`, `DELETE`)
- Endpoints de tópicos (`POST /topics/extract`, `GET /topics/{subject}`)
- Modelos de request/response para cada endpoint
- Ejemplos con cURL
- Códigos de error y respuestas

**Leer cuando:** Necesites llamar a un endpoint o integrar con la API

---

### 4. **[algorithms.md](./algorithms.md)** — Algoritmos matemáticos

Referencia de los algoritmos matemáticos del TFG-Matemáticas que usa este servicio.

**Incluye:**
- Fuzzy C-Means (FCM) — fundamentos matemáticos y implementation
- Non-negative Matrix Factorization (NMF) — topic modeling
- Vectorizadores TF-IDF y BoW
- Determinación del K óptimo (elbow method)
- SphericalFuzzyCMeans (variante para embeddings)
- Coherencia de tópicos
- Hiperparámetros y guías de uso

**Leer cuando:** Necesites entender los fundamentos matemáticos o ajustar los algoritmos

---

### 5. **[configuration.md](./configuration.md)** — Entorno y ajustes

Referencia completa de configuración del Math Service.

**Incluye:**
- Variables de entorno con valores por defecto Docker
- Configuración de MongoDB (URI, credenciales)
- Configuración de Ollama (host, puerto, modelos)
- Configuración de Mistral API
- Configuración del RAG Service
- Ejemplo de archivo `.env`
- Configuración por entorno (desarrollo/producción)
- Errores comunes de configuración

**Leer cuando:** Necesites configurar el servicio o resolver problemas de configuración

---

### 6. **[development.md](./development.md)** — Setup de desarrollo local

Guía completa para desarrollar el Math Service localmente.

**Incluye:**
- Prerrequisitos y setup del proyecto
- Creación del entorno virtual con `uv`
- Instalación de dependencias
- Creación del archivo `.env`
- Arrancar el servidor de desarrollo
- Flujo de trabajo de desarrollo
- Añadir nuevos endpoints
- Escribir tests (fixtures, mocking MongoDB)
- Técnicas de depuración
- Comandos útiles

**Leer cuando:** Quieras desarrollar localmente o contribuir código

---

### 7. **[deployment.md](./deployment.md)** — Despliegue en producción

Guía completa para desplegar el Math Service.

**Incluye:**
- Despliegue con Docker Compose (principal)
- Construcción de imagen Docker
- Dependencias de arranque (MongoDB, Ollama, RAG Service)
- Health check y arranque degradado
- Variables de entorno en producción
- Monitorización y métricas Prometheus

**Leer cuando:** Necesites desplegar o gestionar la infraestructura

---

## Navegación rápida por tarea

### Quiero...

**Empezar rápido:**
→ Leer [README.md](./README.md) (5 min)

**Entender el sistema:**
→ Leer [architecture.md](./architecture.md) (15 min)

**Llamar a un endpoint:**
→ Leer [api-endpoints.md](./api-endpoints.md) o usar Swagger UI en `/docs`

**Entender los algoritmos:**
→ Leer [algorithms.md](./algorithms.md)

**Configurar el servicio:**
→ Leer [configuration.md](./configuration.md)

**Desarrollar localmente:**
→ Leer [development.md](./development.md)

**Desplegar en producción:**
→ Leer [deployment.md](./deployment.md)
