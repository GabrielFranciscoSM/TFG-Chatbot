# RAG Service Deployment

This document covers deploying the RAG service in Docker and production environments.

## Docker Deployment

### Dockerfile

The service uses a multi-stage build for efficiency:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.14-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY rag_service/pyproject.toml rag_service/
COPY rag_service/__init__.py rag_service/
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir "./rag_service[dev]"; \
    else \
        pip install --no-cache-dir ./rag_service; \
    fi

# Stage 2: Runtime
FROM python:3.14-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY rag_service rag_service/
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/documents && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 8081
CMD ["uvicorn", "rag_service.api:app", "--host", "0.0.0.0", "--port", "8081"]
```

### Build Commands

```bash
# Production build
docker build -f rag_service/Dockerfile -t rag-service:latest .

# Development build (with test dependencies)
docker build -f rag_service/Dockerfile \
  --build-arg INSTALL_DEV=true \
  -t rag-service:dev .
```

---

## Docker Compose

### Service Configuration

```yaml
# docker-compose.yml
rag_service:
  build:
    context: .
    dockerfile: ./rag_service/Dockerfile
  container_name: rag_service
  environment:
    - QDRANT_HOST=qdrant
    - QDRANT_PORT=6333
    - OLLAMA_HOST=ollama
    - OLLAMA_PORT=11434
    - OLLAMA_MODEL=nomic-embed-text
    - DOCUMENTS_PATH=/app/documents
    - TOP_K_RESULTS=5
    - SIMILARITY_THRESHOLD=0.5
  ports:
    - "8081:8081"
  volumes:
    - ./rag_service/documents:/app/documents
  depends_on:
    - qdrant
    - ollama
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### Dependent Services

```yaml
qdrant:
  image: qdrant/qdrant:latest
  container_name: qdrant
  ports:
    - "6333:6333"
    - "6334:6334"  # gRPC
  volumes:
    - qdrant_storage:/qdrant/storage
  restart: unless-stopped

ollama:
  image: ollama/ollama:latest
  container_name: ollama
  ports:
    - "11435:11434"
  volumes:
    - ollama_models:/root/.ollama
  restart: unless-stopped

volumes:
  qdrant_storage:
  ollama_models:
```

### Deploy Commands

```bash
# Start all services
docker compose up -d qdrant ollama rag_service

# Initialize embedding model
docker exec ollama ollama pull nomic-embed-text

# Check status
docker compose ps
docker compose logs -f rag_service
```

---

## Production Considerations

### Resource Limits

```yaml
rag_service:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.25'
```

### Health Checks

The service exposes a health endpoint:

```bash
# Check health
curl http://localhost:8081/health

# Response
{
  "status": "healthy",
  "qdrant_connected": true,
  "collection": {
    "name": "academic_documents",
    "points_count": 156,
    "status": "green"
  }
}
```

### Logging

Configure structured JSON logging for production:

```python
# logging_config.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        })
```

---

## Volumes and Persistence

### Document Storage

```yaml
volumes:
  - ./documents:/app/documents        # Local dev
  - documents_data:/app/documents     # Named volume
```

### Qdrant Data

```yaml
volumes:
  - qdrant_storage:/qdrant/storage    # Vector data
```

### Ollama Models

```yaml
volumes:
  - ollama_models:/root/.ollama       # Model cache
```

---

## Environment Configuration

### Production Environment

```bash
# .env.production
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=academic_documents

OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=nomic-embed-text

EMBEDDING_DIMENSION=768
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.5

CHUNK_SIZE=1000
CHUNK_OVERLAP=200

DOCUMENTS_PATH=/app/documents
CORS_ORIGINS=["https://your-domain.com"]
```

### Using Environment File

```yaml
rag_service:
  env_file:
    - .env.production
```

---

## Scaling

### Horizontal Scaling

The RAG service is stateless and can be scaled horizontally:

```yaml
rag_service:
  deploy:
    replicas: 3
```

### Load Balancing

Use Nginx or Traefik for load balancing:

```nginx
upstream rag_service {
    server rag_service_1:8081;
    server rag_service_2:8081;
    server rag_service_3:8081;
}

server {
    location /rag/ {
        proxy_pass http://rag_service/;
    }
}
```

### Qdrant Scaling

For high-volume deployments, consider Qdrant cluster mode:

```yaml
qdrant:
  environment:
    - QDRANT__CLUSTER__ENABLED=true
```

---

## Monitoring

### Prometheus Metrics

The service exposes metrics at `/metrics`:

```bash
curl http://localhost:8081/metrics
```

Available metrics:
- `http_requests_total` - Request count by path/status
- `http_request_duration_seconds` - Latency histogram
- `http_requests_in_progress` - Active requests

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'rag_service'
    static_configs:
      - targets: ['rag_service:8081']
    metrics_path: /metrics
```

### Grafana Dashboard

Key panels:
- Request rate by endpoint
- Error rate
- P95 latency
- Active connections

---

## Security

### Non-Root User

The container runs as non-root user:

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### CORS Configuration

Restrict origins in production:

```bash
CORS_ORIGINS=["https://your-frontend.com"]
```

### Network Isolation

Use Docker networks:

```yaml
networks:
  backend:
    driver: bridge

services:
  rag_service:
    networks:
      - backend
  qdrant:
    networks:
      - backend
```

### Secrets Management

Use Docker secrets for sensitive data:

```yaml
secrets:
  api_key:
    file: ./secrets/api_key.txt

services:
  rag_service:
    secrets:
      - api_key
```

---

## Backup and Recovery

### Qdrant Backup

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/academic_documents/snapshots

# List snapshots
curl http://localhost:6333/collections/academic_documents/snapshots

# Restore from snapshot
curl -X PUT http://localhost:6333/collections/academic_documents/snapshots/recover \
  -H "Content-Type: application/json" \
  -d '{"location": "http://storage/snapshot.tar"}'
```

### Document Backup

```bash
# Backup documents volume
docker run --rm \
  -v rag_documents:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/documents.tar.gz -C /data .

# Restore
docker run --rm \
  -v rag_documents:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/documents.tar.gz -C /data
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/build-rag.yml
name: Build RAG Service

on:
  push:
    paths:
      - 'rag_service/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build image
        run: |
          docker build -f rag_service/Dockerfile \
            -t rag-service:${{ github.sha }} .
      
      - name: Run tests
        run: |
          docker run --rm rag-service:${{ github.sha }} \
            pytest tests/ -m "not integration"
```

### Image Publishing

```yaml
- name: Push to registry
  run: |
    docker tag rag-service:${{ github.sha }} \
      ghcr.io/${{ github.repository }}/rag-service:latest
    docker push ghcr.io/${{ github.repository }}/rag-service:latest
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs rag_service

# Common issues:
# - Qdrant not ready: Check depends_on and health
# - Port conflict: Change port mapping
# - Missing model: Run ollama pull
```

### Connection Issues

```bash
# Verify networking
docker exec rag_service ping qdrant
docker exec rag_service ping ollama

# Check service discovery
docker exec rag_service nslookup qdrant
```

### Performance Issues

```bash
# Check resource usage
docker stats rag_service

# Increase memory if needed
deploy:
  resources:
    limits:
      memory: 4G
```

---

## Related Documentation

- [Configuration](configuration.md) - Environment variables
- [Development](development.md) - Local setup
- [Architecture](architecture.md) - System design
- [Infrastructure](../infrastructure/docker-compose.md) - Full stack deployment
