# Dockerfile for RAG Service
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code and install Python dependencies from pyproject.toml
# Copy the rag_service package (contains pyproject.toml and source)
COPY rag_service/ rag_service/

# Upgrade pip/build tools and install the package (this will install dependencies
# declared in rag_service/pyproject.toml via the build backend).
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir ./rag_service

# Expose API port
EXPOSE 8081

# Run the API (now rag_service is a proper module)
CMD ["uvicorn", "rag_service.api:app", "--host", "0.0.0.0", "--port", "8081"]
