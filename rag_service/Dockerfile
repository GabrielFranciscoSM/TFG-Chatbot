# Dockerfile for RAG Service
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt rag_service/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout=300 --retries=5 -r rag_service/requirements.txt

# Copy application code as rag_service module
COPY . rag_service/

# Expose API port
EXPOSE 8081

# Run the API (now rag_service is a proper module)
CMD ["uvicorn", "rag_service.api:app", "--host", "0.0.0.0", "--port", "8081"]
