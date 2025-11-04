# Infrastructure Tests

Este directorio contiene tests de infraestructura que verifican que cada contenedor/servicio está corriendo correctamente y puede realizar operaciones básicas.

## Estructura de Tests

```
tests/infrastructure/
├── test_backend_container.py      # Tests del contenedor backend/FastAPI (4 tests)
├── test_mongo_container.py         # Tests del contenedor MongoDB (10 tests)
├── test_ollama_container.py        # Tests del contenedor Ollama (12 tests)
├── test_qdrant_container.py        # Tests del contenedor Qdrant (8 tests)
├── test_rag_service_container.py   # Tests del contenedor RAG Service (10 tests)
└── test_vllm_container.py          # Tests del contenedor vLLM (6 tests)
```

**Total: 50 tests de infraestructura**

## Requisitos Previos

Todos los contenedores deben estar corriendo:

```bash
# Levantar todos los servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

## Ejecución de Tests

### Ejecutar Todos los Tests de Infraestructura

```bash
# Desde el directorio raíz del proyecto
pytest tests/infrastructure/ -v

# Con output en tiempo real
pytest tests/infrastructure/ -s
```

### Ejecutar Tests de un Servicio Específico

```bash
# Tests del backend
pytest tests/infrastructure/test_backend_container.py -v

# Tests de MongoDB
pytest tests/infrastructure/test_mongo_container.py -v

# Tests de Ollama
pytest tests/infrastructure/test_ollama_container.py -v

# Tests de Qdrant
pytest tests/infrastructure/test_qdrant_container.py -v

# Tests del servicio RAG
pytest tests/infrastructure/test_rag_service_container.py -v

# Tests de vLLM
pytest tests/infrastructure/test_vllm_container.py -v
```

## Tests del Backend (`test_backend_container.py`)

Validan que el contenedor del backend está funcionando:

- ✅ Contenedor está corriendo y responde al health check
- ✅ Endpoint raíz retorna información de la API
- ✅ Acepta peticiones de chat
- ✅ Valida payloads correctamente (retorna 422 para datos inválidos)

**URL:** `http://localhost:8080`

## Tests de MongoDB (`test_mongo_container.py`)

Validan operaciones básicas de MongoDB:

- ✅ Contenedor está corriendo y acepta conexiones
- ✅ Puede listar bases de datos
- ✅ Puede crear bases de datos y colecciones
- ✅ Puede realizar consultas (find con filtros)
- ✅ Puede actualizar documentos
- ✅ Puede eliminar documentos
- ✅ Soporta índices
- ✅ Soporta operaciones de agregación
- ✅ Requiere autenticación
- ✅ Proporciona información del servidor

**URL:** `localhost:27017`  
**Credenciales:** Definidas en `.env` (`MONGO_ROOT_USERNAME`, `MONGO_ROOT_PASSWORD`)

## Tests de Ollama (`test_ollama_container.py`)

Validan la generación de embeddings con Ollama:

- ✅ Contenedor está corriendo
- ✅ API de versión responde
- ✅ Puede listar modelos instalados
- ✅ Modelo de embeddings (`nomic-embed-text`) está disponible
- ✅ Puede generar embeddings
- ✅ Embeddings tienen dimensión correcta (768)
- ✅ Genera embeddings consistentes para el mismo texto
- ✅ Puede generar múltiples embeddings
- ✅ Maneja textos vacíos
- ✅ Maneja textos largos
- ✅ Rechaza modelos inválidos
- ✅ Maneja caracteres especiales y acentos

**URL:** `http://localhost:11435`  
**Modelo:** `nomic-embed-text` (768 dimensiones)

## Tests de Qdrant (`test_qdrant_container.py`)

Validan operaciones del vector store:

- ✅ Contenedor está corriendo
- ✅ Health endpoint responde
- ✅ Puede crear colecciones
- ✅ Puede insertar y buscar vectores
- ✅ Puede filtrar por metadata
- ✅ Proporciona información de colecciones
- ✅ Puede listar colecciones
- ✅ REST API funciona correctamente

**URL:** `http://localhost:6333`

## Tests del Servicio RAG (`test_rag_service_container.py`)

Validan el API del servicio RAG:

- ✅ Contenedor está corriendo y responde al health check
- ✅ Endpoint raíz retorna información del servicio
- ✅ Acepta peticiones de búsqueda
- ✅ Acepta peticiones de indexación
- ✅ Valida payloads de búsqueda
- ✅ Valida payloads de indexación
- ✅ Puede obtener información de la colección
- ✅ Puede listar asignaturas
- ✅ Puede listar tipos de documentos
- ✅ Puede listar archivos

**URL:** `http://localhost:8081`

## Tests de vLLM (`test_vllm_container.py`)

Validan el servicio de inferencia LLM:

- ✅ Health endpoint responde
- ✅ Puede generar chat completions
- ✅ Soporta tool calling
- ✅ Rechaza modelos inválidos
- ✅ Valida formato de mensajes
- ✅ Valida definiciones de herramientas

**URL:** `http://localhost:8000`  
**Modelo:** Configurado en `.env` (variable `MODEL_PATH`)

## Variables de Entorno

Los tests utilizan las siguientes variables de entorno:

```bash
# MongoDB
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=example

# vLLM
VLLM_MAIN_PORT=8000
MODEL_PATH=/models/your-model

# Otros puertos (por defecto)
BACKEND_PORT=8080
RAG_SERVICE_PORT=8081
QDRANT_PORT=6333
OLLAMA_PORT=11435
```

## Troubleshooting

### Error: "ConnectionError" en los tests

**Problema:** Los contenedores no están disponibles.

**Solución:**
```bash
# Verificar que los contenedores estén corriendo
docker-compose ps

# Si no están corriendo, levantarlos
docker-compose up -d

# Ver logs de un contenedor específico
docker-compose logs backend
docker-compose logs rag_service
```

### Error: "Authentication failed" en MongoDB

**Problema:** Credenciales incorrectas.

**Solución:**
```bash
# Verificar que las variables de entorno están configuradas
cat .env | grep MONGO

# O configurarlas manualmente
export MONGO_ROOT_USERNAME=root
export MONGO_ROOT_PASSWORD=example
```

### Error: "Model not found" en Ollama

**Problema:** El modelo de embeddings no está descargado.

**Solución:**
```bash
# Ejecutar el script de inicialización
./scripts/init_ollama.sh

# O descargar manualmente
docker exec ollama-service ollama pull nomic-embed-text
```

### Tests de Qdrant fallan con "Collection not found"

**Problema:** Los tests crean y eliminan colecciones temporales que pueden persistir.

**Solución:**
```bash
# Reiniciar Qdrant
docker-compose restart qdrant

# O limpiar completamente los datos
docker-compose down -v
docker-compose up -d
```

## Notas Importantes

1. **Orden de ejecución:** Los tests de infraestructura son independientes y pueden ejecutarse en cualquier orden.

2. **Datos de prueba:** Los tests crean y limpian sus propios datos de prueba (colecciones temporales, documentos, etc.).

3. **Timeouts:** Algunos tests tienen timeouts largos (30-60s) porque:
   - La primera generación de embeddings puede ser lenta
   - Los modelos LLM pueden tardar en responder
   - MongoDB puede tardar en autenticarse

4. **Dependencias:** 
   - Los tests de MongoDB requieren `pymongo`
   - Los tests de Qdrant requieren `qdrant-client`
   - Los tests usan `requests` para HTTP
   - Todas las dependencias están en `pyproject.toml`

## Continuous Integration

Los tests de infraestructura están diseñados para ejecutarse en CI/CD:

```yaml
# Ejemplo para GitHub Actions
- name: Start services
  run: docker-compose up -d

- name: Wait for services
  run: sleep 30

- name: Run infrastructure tests
  run: pytest tests/infrastructure/ -v
```

## Métricas

```
Total tests:     50
Por servicio:
  - Backend:     4 tests
  - MongoDB:     10 tests
  - Ollama:      12 tests
  - Qdrant:      8 tests
  - RAG Service: 10 tests
  - vLLM:        6 tests
```

## Contribuir

Al agregar nuevos tests de infraestructura:

1. Sigue el patrón existente de los tests
2. Usa nombres descriptivos para las funciones de test
3. Incluye docstrings que expliquen qué se está verificando
4. Limpia los recursos creados (colecciones, documentos, etc.)
5. Actualiza este README con el nuevo test
6. Usa timeouts apropiados para operaciones lentas
