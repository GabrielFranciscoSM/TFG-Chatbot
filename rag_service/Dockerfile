# =============================================================================
# Stage 1: Build dependencies
# =============================================================================
FROM python:3.13-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy only pyproject.toml first for better caching
COPY rag_service/pyproject.toml rag_service/
COPY rag_service/__init__.py rag_service/

# Install dependencies (cached if pyproject.toml unchanged)
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir "./rag_service[dev]"; \
    else \
        pip install --no-cache-dir ./rag_service; \
    fi

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY rag_service rag_service/

# Create directories and non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/documents && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8081

CMD ["uvicorn", "rag_service.api:app", "--host", "0.0.0.0", "--port", "8081"]
