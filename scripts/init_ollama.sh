#!/bin/bash

# Script para inicializar el modelo de embeddings en Ollama
# Ejecutar después de levantar docker-compose

echo "🚀 Inicializando modelos de embeddings en Ollama..."

# Esperar a que Ollama esté listo
echo "⏳ Esperando a que Ollama esté disponible..."
until docker exec ollama-service ollama list &> /dev/null; do
    echo "   Ollama aún no está listo, esperando..."
    sleep 2
done

echo "✅ Ollama está listo"

# Descargar el modelo para RAG service
echo "📥 Descargando modelo nomic-embed-text (RAG service)..."
docker exec ollama-service ollama pull nomic-embed-text

# Descargar el modelo para Math service
echo "📥 Descargando modelo qwen3-embedding:0.6b (Math service)..."
docker exec ollama-service ollama pull qwen3-embedding:0.6b

echo "✅ Modelos descargados correctamente"

# Verificar que los modelos están disponibles
echo "🔍 Verificando modelos instalados..."
docker exec ollama-service ollama list

echo ""
echo "✨ Inicialización completada!"
echo "   RAG service → nomic-embed-text"
echo "   Math service → qwen3-embedding:0.6b"
