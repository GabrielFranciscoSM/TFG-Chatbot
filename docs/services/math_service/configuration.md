# Math Service — Configuración

Referencia completa de variables de entorno y ajustes del Math Service.

## Cómo funciona la configuración

El servicio usa `pydantic-settings BaseSettings` (clase `Settings` en `config.py`). Las variables se cargan en este orden de prioridad:

1. Variables de entorno del sistema/proceso
2. Archivo `.env` en la raíz del proyecto
3. Valores por defecto definidos en la clase

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
```

---

## Variables de entorno

### MongoDB

| Variable | Default (Docker) | Descripción |
|----------|-----------------|-------------|
| `MONGO_URI` | `None` | URI completo de MongoDB. Si se define, tiene prioridad sobre HOSTNAME+PORT. |
| `MONGO_HOSTNAME` | `"mongo"` | Host del servidor MongoDB. |
| `MONGO_PORT` | `"27017"` | Puerto de MongoDB. |
| `MONGO_ROOT_USERNAME` | `None` | Usuario de autenticación MongoDB. |
| `MONGO_ROOT_PASSWORD` | `None` | Contraseña de MongoDB (`SecretStr`). |
| `MONGO_AUTH_DB` | `None` | Base de datos de autenticación (e.g., `"admin"`). |
| `DB_NAME` | `"tfg_chatbot"` | Nombre de la base de datos. |

La URI se construye internamente con `settings.get_mongo_uri()`:

```python
# Sin credenciales
mongodb://mongo:27017

# Con credenciales y authSource
mongodb://user:password@mongo:27017/?authSource=admin

# URI directa (prioridad)
MONGO_URI=mongodb://user:pass@mongo:27017/tfg_chatbot
```

---

### Ollama

| Variable | Default (Docker) | Descripción |
|----------|-----------------|-------------|
| `OLLAMA_HOST` | `"ollama"` | Host del servidor Ollama. |
| `OLLAMA_PORT` | `11434` | Puerto de Ollama. |
| `OLLAMA_MODEL` | `"nomic-embed-text"` | Modelo para generación de embeddings. |
| `OLLAMA_GENERATION_MODEL` | `"qwen3.5:0.8b"` | Modelo de generación de texto (reservado para uso futuro). |

> Ollama se usa para obtener embeddings de preguntas en el pipeline de generación de FAQs.

---

### Mistral

| Variable | Default | Descripción |
|----------|---------|-------------|
| `MISTRAL_API_KEY` | `None` | API key de Mistral AI (`SecretStr`). Necesaria para generación de títulos de tópicos. |
| `MISTRAL_MODEL` | `"mistral-small-latest"` | Modelo Mistral a usar. |

> Si `MISTRAL_API_KEY` no está definida, la generación de títulos de tópicos usará un nombre genérico (`"Tópico N"`).

---

### RAG Service

| Variable | Default (Docker) | Descripción |
|----------|-----------------|-------------|
| `RAG_SERVICE_URL` | `"http://rag_service:8081"` | URL base del RAG Service. |

> El RAG Service es necesario para los endpoints de extracción de tópicos (`/topics/extract`).

---

### API

| Variable | Default | Descripción |
|----------|---------|-------------|
| `API_HOST` | `"0.0.0.0"` | Dirección de escucha del servidor. |
| `API_PORT` | `8083` | Puerto de escucha. |
| `CORS_ORIGINS` | `["*"]` | Lista de orígenes CORS permitidos. |

> En producción, restringir `CORS_ORIGINS` al dominio del frontend.

---

## Ejemplo de archivo `.env`

### Desarrollo local

```env
# MongoDB
MONGO_HOSTNAME=localhost
MONGO_PORT=27017

# Ollama
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=nomic-embed-text

# Mistral (opcional para títulos de tópicos)
MISTRAL_API_KEY=tu_api_key_aqui

# RAG Service
RAG_SERVICE_URL=http://localhost:8081

# API
API_HOST=0.0.0.0
API_PORT=8083
```

### Docker Compose

En Docker Compose los valores por defecto son correctos, solo hace falta añadir credenciales si MongoDB tiene auth habilitada:

```env
# MongoDB con autenticación
MONGO_HOSTNAME=mongo
MONGO_PORT=27017
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=secret
MONGO_AUTH_DB=admin

# Mistral
MISTRAL_API_KEY=tu_api_key_aqui
```

### Producción

```env
# MongoDB Atlas o MongoDB con credenciales
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/tfg_chatbot

# Ollama en servidor dedicado
OLLAMA_HOST=ollama.internal
OLLAMA_MODEL=nomic-embed-text

# Mistral
MISTRAL_API_KEY=...

# RAG Service
RAG_SERVICE_URL=http://rag_service:8081

# Restringir CORS
CORS_ORIGINS=["https://tfg-chatbot.example.com"]
```

---

## Configuración por entorno

| Variable | Desarrollo local | Docker Compose | Producción |
|----------|-----------------|---------------|------------|
| `MONGO_HOSTNAME` | `localhost` | `mongo` | — |
| `MONGO_URI` | — | — | URI de Atlas/MongoDB |
| `OLLAMA_HOST` | `localhost` | `ollama` | host interno |
| `RAG_SERVICE_URL` | `http://localhost:8081` | `http://rag_service:8081` | URL interna |
| `API_PORT` | `8083` | `8083` | `8083` |
| `CORS_ORIGINS` | `["*"]` | `["*"]` | Restringido |

---

## Errores comunes de configuración

### `MONGO_HOSTNAME` no definido y no hay `MONGO_URI`

El servicio usará `mongodb://localhost:27017` como fallback. Verificar que el string sea correcto.

### Ollama no alcanzable

Si `OLLAMA_HOST` o `OLLAMA_PORT` son incorrectos, el health check mostrará `ollama_connected: false` y la generación de FAQs fallará con error de NLP.

Verificar:
```bash
curl http://${OLLAMA_HOST}:${OLLAMA_PORT}/api/tags
```

### `MISTRAL_API_KEY` vacía

La extracción de tópicos funcionará pero los nombres de los tópicos serán genéricos (`"Tópico 1"`, `"Tópico 2"`, etc.) en lugar de títulos descriptivos generados por IA.

### RAG Service no responde

La extracción de tópicos fallará con `500 RAG service unavailable`. Verificar:
```bash
curl ${RAG_SERVICE_URL}/health
```

---

## Validar la configuración

Iniciar el servicio y usar el endpoint de health check para verificar que todos los componentes están disponibles:

```bash
curl http://localhost:8083/health | python3 -m json.tool
```

Respuesta esperada en un entorno completamente funcional:

```json
{
  "status": "healthy",
  "mongo_connected": true,
  "ollama_connected": true,
  "rag_service_connected": true,
  "message": "MongoDB: OK, Ollama: OK, RAG: OK"
}
```

---

## Prácticas de seguridad

- **Nunca** incluir `MISTRAL_API_KEY` o `MONGO_ROOT_PASSWORD` en código fuente ni en imágenes Docker
- Usar `docker secret` o el gestor de secretos de Kubernetes en entornos productivos
- Restringir `CORS_ORIGINS` al dominio del frontend en producción
- Usar `MONGO_URI` con TLS (`mongodb+srv://`) en producción
