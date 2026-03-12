# Math Service — Despliegue

Guía de despliegue y ejecución del Math Service en distintos entornos.

## Despliegue con Docker Compose (principal)

El método recomendado para desarrollo y puesta en marcha del stack completo.

### Arrancar solo el Math Service y sus dependencias

```bash
docker compose up -d mongo ollama rag_service math_service
```

### Arrancar el stack completo

```bash
docker compose up -d
```

El servicio estará disponible en `http://localhost:8083`.

### Construir con dependencias de desarrollo

```bash
INSTALL_DEV=true docker compose build math_service
docker compose up -d math_service
```

### Verificar estado

```bash
# Health check
curl http://localhost:8083/health

# Logs en tiempo real
docker logs -f math-service

# Estado de todos los servicios
docker compose ps
```

---

## Definición en `docker-compose.yml`

```yaml
math_service:
  build:
    context: .
    dockerfile: math_service/Dockerfile
    args:
      INSTALL_DEV: ${INSTALL_DEV:-false}
  container_name: math-service
  env_file:
    - .env
  environment:
    MONGO_HOSTNAME: mongo
    OLLAMA_HOST: ollama
    RAG_SERVICE_URL: http://rag_service:8081
  ports:
    - "8083:8083"
  depends_on:
    - mongo
    - ollama
    - rag_service
  restart: unless-stopped
```

Las variables en `environment` sobreescriben las del `.env` de forma que el servicio siempre apunta a los contenedores correctos en la red Docker interna.

---

## Dockerfile — Build multietapa

El Dockerfile usa un build en dos etapas para optimizar el tamaño de la imagen final:

```
Stage 1: builder  (python:3.14-slim)
  └─ instala dependencias con pip
  └─ acepta ARG INSTALL_DEV para incluir dependencias de test

Stage 2: runtime  (python:3.14-slim)
  └─ copia site-packages del builder (sin build tools)
  └─ copia el código fuente
  └─ crea usuario no-root (UID 1000)
  └─ EXPOSE 8083
  └─ CMD: uvicorn math_service.api:app --host 0.0.0.0 --port 8083
```

### Construir manualmente

```bash
# Build desde la raíz del proyecto (el contexto debe ser la raíz)
docker build -t tfg-math-service:latest \
  -f math_service/Dockerfile \
  .

# Con dependencias de desarrollo
docker build -t tfg-math-service:dev \
  -f math_service/Dockerfile \
  --build-arg INSTALL_DEV=true \
  .
```

### Ejecutar el contenedor manualmente

```bash
docker run -d \
  --name math-service \
  -p 8083:8083 \
  -e MONGO_HOSTNAME=host.docker.internal \
  -e OLLAMA_HOST=host.docker.internal \
  -e RAG_SERVICE_URL=http://host.docker.internal:8081 \
  -e MISTRAL_API_KEY=tu_api_key \
  tfg-math-service:latest
```

---

## Dependencias de arranque

El servicio necesita que estén disponibles:

| Servicio | Puerto | Impacto si no disponible |
|---------|--------|--------------------------|
| **MongoDB** | `27017` | El servicio no puede leer conversaciones ni persistir FAQs/tópicos. Arranca pero todas las operaciones de DB fallarán. |
| **Ollama** | `11434` | La generación de FAQs falla: no se pueden obtener embeddings. |
| **RAG Service** | `8081` | La extracción de tópicos falla: no hay chunks de documentos. |

Si algún servicio no está disponible al arrancar, el Math Service inicia igualmente. El endpoint `/health` reflejará el estado con `status: "degraded"`.

```
GET /health → {"status": "degraded", "mongo_connected": false, ...}
```

---

## URLs por entorno

| Entorno | URL |
|---------|-----|
| Docker Compose (interno) | `http://math_service:8083` |
| Docker Compose (externo) | `http://localhost:8083` |
| Desarrollo local | `http://localhost:8083` |
| Swagger UI | `http://localhost:8083/docs` |
| ReDoc | `http://localhost:8083/redoc` |
| Métricas Prometheus | `http://localhost:8083/metrics` |

---

## Monitorización

### Prometheus

El servicio expone métricas automáticas en `/metrics`:

- `http_requests_total` — número de requests por endpoint y código de estado
- `http_request_duration_seconds` — histograma de latencias
- Métricas del proceso Python (GC, memoria, CPU)

La integración con Prometheus está configurada en `prometheus.yml` en la raíz del proyecto:

```yaml
scrape_configs:
  - job_name: math_service
    static_configs:
      - targets: ["math_service:8083"]
```

### Grafana

Los dashboards de Grafana se provisionan automáticamente desde `grafana/provisioning/`. Ver [infrastructure/monitoring.md](../infrastructure/monitoring.md) para detalles.

### Logs JSON estructurados

Todos los logs del servicio se emiten en formato JSON con correlation ID, facilitando su ingesta en Loki/Promtail:

```json
{
  "timestamp": "2026-03-12T10:30:00Z",
  "level": "INFO",
  "logger": "math_service.services.faq_service",
  "message": "Gathered 87 student questions (subject=iv)",
  "correlation_id": "abc123"
}
```

---

## Gestión de errores en producción

El servicio **no interrumpe el arranque** si los servicios dependientes no están listos (fail-open). Esto permite:

- Despliegues independientes de cada microservicio
- Reintentos automáticos por `restart: unless-stopped`
- Visibilidad del estado en `/health` sin necesidad de revisar logs

Si el RAG Service o MongoDB no están disponibles durante una operación, el endpoint devolverá `500` con el mensaje de error específico.

---

## Actualizar el servicio

```bash
# Reconstruir la imagen tras cambios en el código
docker compose build math_service

# Reiniciar con la nueva imagen
docker compose up -d --no-deps math_service

# Ver los últimos logs para confirmar que arrancó bien
docker logs --tail 20 math-service
```
