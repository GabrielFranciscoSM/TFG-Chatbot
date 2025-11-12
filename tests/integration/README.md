# Integration Tests

Este directorio contiene tests de integración que validan el funcionamiento end-to-end de los servicios del proyecto.

## Estructura de Tests

```
tests/integration/
├── conftest.py              # Configuración y fixtures para tests de integración
├── test_backend.py          # Tests de integración del backend/chatbot
└── test_rag_service.py      # Tests de integración del servicio RAG
```

## Requisitos Previos

Los tests de integración requieren que todos los servicios estén corriendo. Antes de ejecutar los tests:

1. **Levantar los servicios con Docker Compose:**

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d
```

2. **Verificar que los servicios estén disponibles:**

```bash
# Backend
curl http://localhost:8080/health

# RAG Service
curl http://localhost:8081/health
```

3. **Inicializar Ollama con el modelo de embeddings (primera vez):**

```bash
# Ejecutar el script de inicialización
./scripts/init_ollama.sh
```

## Ejecución de Tests

### Ejecutar Todos los Tests de Integración

```bash
# Desde el directorio raíz del proyecto
pytest tests/integration/ -m integration

# Con verbose para ver más detalles
pytest tests/integration/ -m integration -v

# Con output en tiempo real
pytest tests/integration/ -m integration -s
```

### Ejecutar Tests de un Servicio Específico

```bash
# Solo tests del backend
pytest tests/integration/test_backend.py -m integration

# Solo tests del servicio RAG
pytest tests/integration/test_rag_service.py -m integration
```

### Ejecutar un Test Específico

```bash
# Ejecutar un test individual
pytest tests/integration/test_rag_service.py::test_rag_index_and_search_workflow -m integration
```

## Variables de Entorno

Puedes configurar los tests mediante variables de entorno:

```bash
# URL del backend (por defecto: http://localhost:8080)
export API_BASE_URL="http://localhost:8080"

# URL del servicio RAG (por defecto: http://localhost:8081)
export RAG_BASE_URL="http://localhost:8081"

# Timeout para peticiones HTTP en segundos (por defecto: 30)
export API_TIMEOUT="60"
```

## Tests del Backend (`test_backend.py`)

Validan la funcionalidad del chatbot a través de la API:

- ✅ Conversación básica con el chatbot
- ✅ Uso de herramientas (calculadora)
- ✅ Memoria de conversación entre mensajes
- ✅ Separación de contexto entre sesiones
- ✅ Manejo de mensajes vacíos
- ✅ Cálculos complejos
- ✅ Validación de payloads inválidos

**Ejemplo de ejecución:**
```bash
pytest tests/integration/test_backend.py::test_chat_endpoint_with_memory -v
```

## Tests del Servicio RAG (`test_rag_service.py`)

Validan la funcionalidad completa del servicio RAG con Qdrant y Ollama:

### Tests de Endpoints Básicos
- ✅ Health check del servicio
- ✅ Endpoint raíz
- ✅ Información de la colección Qdrant

### Tests de Indexación y Búsqueda
- ✅ Flujo completo: indexar → buscar documentos
- ✅ Búsqueda con filtros de metadata
- ✅ Búsqueda con umbral de similitud
- ✅ Búsqueda con múltiples filtros
- ✅ Chunking de documentos largos
- ✅ Búsqueda sin resultados
- ✅ Indexación de lista vacía

### Tests de Gestión de Archivos
- ✅ Subida de archivos de texto
- ✅ Subida de archivos markdown
- ✅ Listado de archivos
- ✅ Listado con filtros
- ✅ Subida sin indexación automática

### Tests de Metadata
- ✅ Listado de asignaturas
- ✅ Listado de tipos de documentos

### Tests de Validación
- ✅ Query vacía (debe fallar con 422)
- ✅ Payload de búsqueda inválido
- ✅ Payload de indexación inválido

**Ejemplo de ejecución:**
```bash
pytest tests/integration/test_rag_service.py::test_rag_index_and_search_workflow -v -s
```

## Troubleshooting

### Error: "ConnectionError" al ejecutar los tests

**Problema:** Los servicios no están disponibles.

**Solución:**
```bash
# Verificar que los contenedores estén corriendo
docker-compose ps

# Si no están corriendo, levantarlos
docker-compose up -d

# Verificar logs si hay problemas
docker-compose logs backend
docker-compose logs rag_service
```

### Error: "Failed to connect to Ollama"

**Problema:** El modelo de embeddings no está inicializado en Ollama.

**Solución:**
```bash
# Ejecutar el script de inicialización
./scripts/init_ollama.sh

# O manualmente
docker exec ollama-service ollama pull nomic-embed-text
```

### Tests muy lentos

**Problema:** Los embeddings y búsquedas vectoriales pueden ser lentas la primera vez.

**Solución:**
- Es normal que los primeros tests sean más lentos
- Aumentar el timeout: `export API_TIMEOUT="60"`
- Ejecutar menos tests en paralelo

### Error: "Collection not found"

**Problema:** La colección de Qdrant puede necesitar reiniciarse.

**Solución:**
```bash
# Reiniciar el servicio de Qdrant
docker-compose restart qdrant

# O limpiar completamente los datos
docker-compose down -v
docker-compose up -d
```

## Buenas Prácticas

1. **Ejecutar tests en orden:** Los tests de integración pueden ser dependientes del estado del sistema.

2. **Limpiar estado entre ejecuciones:** Si los tests fallan de forma inconsistente, considera reiniciar los servicios:
   ```bash
   docker-compose restart rag_service qdrant
   ```

3. **Revisar logs:** Si un test falla, revisar los logs del servicio correspondiente:
   ```bash
   docker-compose logs -f rag_service
   ```

4. **Timeout adecuado:** Algunos tests pueden tardar más debido a:
   - Generación de embeddings
   - Indexación de documentos largos
   - Primera ejecución (carga de modelos)

5. **Ejecución selectiva:** Durante el desarrollo, ejecutar solo los tests relevantes:
   ```bash
   # Solo tests de búsqueda
   pytest tests/integration/test_rag_service.py -k "search" -v
   ```

## Métricas de Cobertura

Para ejecutar los tests con reporte de cobertura:

```bash
pytest tests/integration/ -m integration --cov=backend --cov=rag_service --cov-report=html
```

El reporte se generará en `htmlcov/index.html`.

## Continuous Integration

Estos tests están diseñados para ejecutarse en CI/CD pipelines. Configuración recomendada:

```yaml
# Ejemplo para GitHub Actions
- name: Run integration tests
  run: |
    docker-compose up -d
    sleep 30  # Esperar que los servicios estén listos
    pytest tests/integration/ -m integration --maxfail=5
  env:
    API_TIMEOUT: 60
```

## Contribuir

Al agregar nuevos tests de integración:

1. Marca el test con `@pytest.mark.integration`
2. Usa los fixtures existentes (`api_base_url`, `rag_base_url`, `api_timeout`)
3. Documenta el propósito del test con un docstring claro
4. Sigue el patrón AAA (Arrange, Act, Assert)
5. Limpia recursos si el test crea datos (archivos, índices, etc.)
6. Actualiza este README con la nueva funcionalidad testeada
