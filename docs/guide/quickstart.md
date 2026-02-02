---
layout: default
title: Quick Start
parent: Developer Guide
nav_order: 2
---

# Quick Start

Get the TFG-Chatbot running in minutes.

---

## Option A: Using Containers (Recommended)

This is the fastest way to get all services running:

```bash
# 1. Start all services
docker compose up -d

# 2. Wait for services to be healthy (check logs)
docker compose logs -f

# 3. Initialize Ollama with embeddings model (first time only)
./scripts/init_ollama.sh

# 4. Seed demo users (optional)
python scripts/seed_users.py
```

### Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | [http://localhost:3000](http://localhost:3000) | Web interface |
| **Backend API** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger documentation |
| **Chatbot API** | [http://localhost:8080/docs](http://localhost:8080/docs) | Internal chatbot API |
| **RAG Service** | [http://localhost:8081/docs](http://localhost:8081/docs) | RAG operations API |

### Demo Credentials

| User | Password | Role |
|------|----------|------|
| `admin` | `admin123` | Admin |
| `profesor` | `admin123` | Professor (subject: ISE) |
| `estudiante` | `admin123` | Student (subject: ISE) |

---

## Option B: Local Development (Without Containers)

For development with hot-reloading:

### Start Infrastructure Services

```bash
# Start MongoDB, Qdrant, and Ollama containers only
docker compose up -d mongo qdrant ollama
```

### Start Backend Services

Open separate terminals for each service:

**Terminal 1: Backend Gateway**
```bash
cd backend
uv run uvicorn backend.api:app --reload --port 8000
```

**Terminal 2: Chatbot Service**
```bash
cd chatbot
uv run uvicorn chatbot.api:app --reload --port 8080
```

**Terminal 3: RAG Service**
```bash
cd rag_service
uv run uvicorn rag_service.api:app --reload --port 8081
```

**Terminal 4: Frontend**
```bash
cd frontend
npm run dev
```

---

## Option C: Quick Test with Script

For quick testing of the backend only:

```bash
./scripts/run_fastAPI.sh
```

This starts the backend gateway on port 8080 with hot-reload.

---

## Verify Services

### Check Health Endpoints

```bash
# Backend
curl http://localhost:8000/health

# Chatbot
curl http://localhost:8080/health

# RAG Service
curl http://localhost:8081/health
```

### Check Container Status

```bash
docker compose ps
```

Expected output:
```
NAME             STATUS          PORTS
tfg-gateway      Up (healthy)    0.0.0.0:8000->8000/tcp
tfg-chatbot      Up (healthy)    0.0.0.0:8080->8080/tcp
rag-service      Up (healthy)    0.0.0.0:8081->8081/tcp
frontend         Up              0.0.0.0:3000->80/tcp
mongo-service    Up              0.0.0.0:27017->27017/tcp
qdrant-service   Up              0.0.0.0:6333->6333/tcp
ollama-service   Up              0.0.0.0:11434->11434/tcp
```

---

## First Steps After Setup

### 1. Access the Frontend

Open [http://localhost:3000](http://localhost:3000) and log in with demo credentials.

### 2. Try the Chat

Send a message to the chatbot. Try questions like:
- "¿Qué es Docker?"
- "Explica qué es un contenedor"
- "¿Cuál es la diferencia entre Docker y una máquina virtual?"

### 3. Explore the API

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see all available endpoints.

### 4. Upload Documents (Optional)

Use the RAG Service API to upload documents for semantic search:

```bash
curl -X POST http://localhost:8081/index \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "subject=ISE"
```

---

## Stopping Services

```bash
# Stop all containers
docker compose down

# Stop and remove volumes (clean reset)
docker compose down -v
```

---

## Next Steps

- [Scripts Reference](scripts.html) - Learn about available utility scripts
- [Testing Guide](testing.html) - Run and write tests
- [Configuration](configuration.html) - Advanced configuration options
