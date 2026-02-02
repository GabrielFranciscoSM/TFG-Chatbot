---
layout: default
title: Developer Guide
nav_order: 2
has_children: true
---

# Developer Guide

Comprehensive documentation for developers and users of the TFG Pedagogical Chatbot project.

## Overview

TFG-Chatbot is a dual-degree thesis project (Computer Science + Mathematics) from the University of Granada:

- **Computer Science TFG**: A pedagogical chatbot using LangGraph for AI orchestration with a microservices architecture
- **Mathematics TFG**: Document clustering research (K-Means, Fuzzy C-Means, NMF) to enhance question classification

## Architecture

The system follows a microservices architecture:

```mermaid
flowchart LR
    subgraph Services
        FE[Frontend<br/>React/TS<br/>:3000]
        BE[Backend<br/>Gateway<br/>:8000]
        CB[Chatbot<br/>LangGraph<br/>:8080]
        RAG[RAG Service<br/>Semantic<br/>:8081]
    end

    subgraph Infrastructure
        MONGO[(MongoDB<br/>:27017)]
        LLM[LLM<br/>Gemini]
        QDRANT[(Qdrant<br/>:6333)]
        OLLAMA[Ollama<br/>:11434]
    end

    FE --> BE --> CB --> RAG
    BE --> MONGO
    CB --> LLM
    RAG --> QDRANT
    RAG --> OLLAMA
```

## Quick Links

| Section | Description |
|---------|-------------|
| [Installation](installation.html) | Prerequisites and setup instructions |
| [Quick Start](quickstart.html) | Get running in minutes |
| [Scripts](scripts.html) | Utility scripts reference |
| [Testing](testing.html) | Testing strategies and commands |
| [Configuration](configuration.html) | Environment variables and settings |
| [Monitoring](monitoring.html) | Grafana, Phoenix, and observability |
| [User Guide](user-guide.html) | How to use the web interface |
| [Troubleshooting](troubleshooting.html) | Common issues and solutions |

## Key Technologies

| Component | Technology Stack |
|-----------|-----------------|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| **Backend Gateway** | FastAPI, PyMongo, JWT, RBAC |
| **Chatbot Agent** | LangChain, LangGraph, Gemini/vLLM |
| **RAG Service** | FastAPI, Sentence Transformers, Qdrant |
| **Databases** | MongoDB (data), Qdrant (vectors), SQLite (checkpoints) |
| **Observability** | Grafana, Prometheus, Loki, Phoenix |
| **Infrastructure** | Docker Compose, GitHub Actions |

