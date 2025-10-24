#!/bin/bash

# Script para inicializar el modelo de embeddings en Ollama
# Ejecutar después de levantar docker-compose

echo "🚀 Inicializando modelo de embeddings en Ollama..."

# Esperar a que Ollama esté listo
echo "⏳ Esperando a que Ollama esté disponible..."
until podman exec ollama-service ollama list &> /dev/null; do
    echo "   Ollama aún no está listo, esperando..."
    sleep 2
done

echo "✅ Ollama está listo"

# Descargar el modelo nomic-embed-text
echo "📥 Descargando modelo nomic-embed-text..."
podman exec ollama-service ollama pull nomic-embed-text

echo "✅ Modelo descargado correctamente"

# Verificar que el modelo está disponible
echo "🔍 Verificando modelos instalados..."
podman exec ollama-service ollama list

echo ""
echo "✨ Inicialización completada!"
echo "   El servicio RAG ya puede usar el modelo nomic-embed-text"
