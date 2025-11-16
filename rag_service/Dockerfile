# Dockerfile for RAG Service
FROM python:3.14-slim

WORKDIR /app

# Build arg to enable optional dev dependencies installation
ARG INSTALL_DEV=false

# Upgrade pip/build tools and install the package (this will install dependencies
# declared in pyproject.toml via the build backend).
# Copy the build context into /app so the package files live directly at /app.
# Installing from /app removes ambiguity about nested paths and makes the
# `rag_service` package importable as `rag_service` at runtime.
# Copy the package sources
COPY rag_service rag_service/

# Install build tools and the package. If INSTALL_DEV=true, install the
# optional 'dev' extras declared in rag_service/pyproject.toml
RUN pip install --upgrade pip setuptools wheel && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        echo "Installing dev extras for rag_service" && \
        pip install "./rag_service[dev]"; \
    else \
        pip install ./rag_service; \
    fi

# Expose API port
EXPOSE 8081

# Run the API. After installing the package from /app, the module path
# `rag_service.api:app` should be importable by uvicorn.
CMD ["uvicorn", "rag_service.api:app", "--host", "0.0.0.0", "--port", "8081"]
