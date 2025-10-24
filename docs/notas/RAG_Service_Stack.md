---
layout: default
title: RAG Service - Stack Tecnológico
parent: Notas
---

# RAG Service - Stack Tecnológico y Arquitectura

**Fecha de decisión**: 14 de Octubre 2025  
**Sprint**: Sprint 2  
**Responsable**: Gabriel Francisco

---

## 🎯 Objetivo

Implementar un servicio RAG (Retrieval-Augmented Generation) para el chatbot educativo que permita:
- Búsqueda semántica en documentos académicos
- Filtrado por metadata (asignatura, tipo de documento, etc.)
- Integración agéntica con el LLM principal
- Escalabilidad y mantenibilidad

---

## ✅ Decisiones Técnicas

### 1. Base de Datos Vectorial: **Qdrant**

**Elección**: Qdrant  
**Alternativa considerada**: ChromaDB

#### Justificación:
- ✅ **Performance superior** en búsquedas con metadata filtering
- ✅ **Escalabilidad** - diseñado para producción desde el inicio
- ✅ **Metadata filtering avanzado** - crucial para filtrar por asignatura
- ✅ **API gRPC y HTTP** - flexibilidad en la comunicación
- ✅ **Persistencia robusta** - mejor manejo de datos en volumen
- ✅ **Documentación excelente** y comunidad activa

#### Despliegue:
```yaml
# Contenedor Podman independiente
qdrant:
  image: qdrant/qdrant:latest
  container_name: qdrant-service
  ports:
    - "6333:6333"  # HTTP API
    - "6334:6334"  # gRPC API
  volumes:
    - ./qdrant_storage:/qdrant/storage
```

**Links**:
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Podman Setup](https://qdrant.tech/documentation/guides/installation/#docker)

---

### 2. Embeddings: **Ollama + nomic-embed-text**

**Elección**: Ollama con modelo `nomic-embed-text`  
**Alternativas consideradas**: Sentence Transformers (all-MiniLM-L6-v2), OpenAI embeddings

#### Especificaciones del modelo:
- **Parámetros**: 137M
- **Dimensionalidad**: 768
- **Contexto máximo**: 8192 tokens
- **Ventajas**:
  - ✅ Optimizado para búsqueda semántica
  - ✅ Funciona completamente local/offline
  - ✅ Excelente relación calidad/recursos
  - ✅ Integración sencilla con Ollama
  - ✅ Sin costes de API externa

#### Despliegue:
```yaml
# Contenedor Docker independiente
ollama:
  image: ollama/ollama:latest
  container_name: ollama-service
  ports:
    - "11434:11434"
  volumes:
    - ./ollama_models:/root/.ollama
```

**Comando para descargar el modelo**:
```bash
podman exec -it ollama-service ollama pull nomic-embed-text
```

**Links**:
- [Nomic Embed Text - Ollama](https://ollama.com/library/nomic-embed-text)
- [Nomic AI Documentation](https://docs.nomic.ai/)

---

### 3. Framework RAG: **LangChain**

**Elección**: LangChain  
**Alternativas consideradas**: LlamaIndex, implementación custom

#### Justificación:
- ✅ **Ya integrado en el proyecto** - usamos LangChain + LangGraph
- ✅ **Integración nativa con Qdrant** (`langchain-qdrant`)
- ✅ **Soporte para Ollama embeddings** (`langchain-ollama`)
- ✅ **RAG agéntico** - fácil integración como herramienta del agente
- ✅ **Metadata filtering** - soporte directo para filtros
- ✅ **Ecosistema maduro** - muchos ejemplos y documentación

#### Dependencias necesarias:
```python
# requirements.txt para rag-service
langchain==0.3.0
langchain-qdrant==0.2.0
langchain-ollama==0.2.0
langchain-core==0.3.0
qdrant-client==1.11.0
```

**Links**:
- [LangChain Qdrant Integration](https://python.langchain.com/docs/integrations/vectorstores/qdrant)
- [LangChain Ollama Embeddings](https://python.langchain.com/docs/integrations/text_embedding/ollama)

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────┐
│                   Backend API                   │
│              (FastAPI + LangGraph)              │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Agente llama herramienta RAG
                    ↓
┌─────────────────────────────────────────────────┐
│                 RAG Service                     │
│           (Microservicio Python)                │
│                                                 │
│  ┌────────────────────────────────────────┐     │
│  │  LangChain RAG Pipeline                │     │
│  │  - Query processing                    │     │
│  │  - Metadata filtering                  │     │
│  │  - Semantic search                     │     │
│  └────────────────────────────────────────┘     │
└──────┬────────────────────────────┬─────────────┘
       │                            │
       │ Embeddings                 │ Vector search
       ↓                            ↓
┌─────────────────┐         ┌─────────────────┐
│  Ollama Service │         │ Qdrant Service  │
│  nomic-embed-   │         │  Vector Store   │
│  text model     │         │  + Metadata     │
└─────────────────┘         └─────────────────┘
```

### Flujo de Datos

1. **Usuario** hace pregunta al chatbot
2. **Agente (LangGraph)** decide si necesita contexto de documentos
3. **Herramienta RAG** es llamada con:
   - Query del usuario
   - Metadata filters (ej: `asignatura="Lógica Difusa"`)
4. **RAG Service**:
   - Genera embedding de la query con Ollama
   - Busca en Qdrant con filtros de metadata
   - Retorna documentos relevantes + metadata
5. **Agente** usa el contexto para generar respuesta

---

## 📋 Metadata Schema

Cada documento indexado tendrá la siguiente metadata:

```python
{
    "asignatura": str,          # Ej: "Lógica Difusa", "Álgebra"
    "tipo_documento": str,      # Ej: "apuntes", "ejercicios", "examen"
    "fecha": str,               # ISO format: "2025-10-14"
    "autor": str,               # Opcional
    "tema": str,                # Ej: "Conjuntos difusos"
    "fuente": str,              # Ej: "PRADO UGR", "Wikipedia"
    "chunk_id": int,            # ID del chunk dentro del documento
}
```

---

## 🚀 Próximos Pasos

### Fase 1: Setup Básico
- [ ] Actualizar `docker-compose.yml` con Qdrant y Ollama
- [ ] Crear estructura de carpetas `rag-service/`
- [ ] Configurar requirements.txt

### Fase 2: Implementación Core
- [ ] Implementar cliente Qdrant con LangChain
- [ ] Implementar generación de embeddings con Ollama
- [ ] Crear pipeline de indexación de documentos
- [ ] Implementar búsqueda con metadata filtering

### Fase 3: Integración Agéntica
- [ ] Crear herramienta RAG para el agente (LangGraph)
- [ ] Añadir a `backend/logic/tools.py`
- [ ] Actualizar System Prompt para uso de RAG

### Fase 4: Testing y Optimización
- [ ] Tests unitarios del RAG service
- [ ] Tests de integración con el agente
- [ ] Benchmarking de performance
- [ ] Ajuste de parámetros (top_k, similarity threshold)

---

## 📚 Referencias Adicionales

- [Building RAG with LangChain and Qdrant](https://qdrant.tech/documentation/tutorials/rag/)
- [Ollama Python Library](https://github.com/ollama/ollama-python)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Metadata Filtering Best Practices](https://qdrant.tech/documentation/concepts/filtering/)

---

## 🔍 Consideraciones de Recursos

### Estimación de uso:
- **Qdrant**: ~100MB base + tamaño de documentos
- **Ollama (nomic-embed-text)**: ~274MB modelo descargado
- **RAM**: ~1-2GB para operación normal del RAG service

### Compatibilidad con recursos actuales:
- ✅ Compatible con GPU actual (usada por vLLM)
- ✅ Ollama puede usar CPU para embeddings
- ✅ Qdrant es ligero en recursos
- ⚠️ Validar espacio en disco para persistencia

