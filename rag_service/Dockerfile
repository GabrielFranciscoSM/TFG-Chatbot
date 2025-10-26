# Dockerfile for RAG Service
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Upgrade pip/build tools and install the package (this will install dependencies
# declared in rag_service/pyproject.toml via the build backend).
# Copy the build context into a subdirectory named `rag_service` so the package
# is importable as `rag_service` (uvicorn expects `rag_service.api:app`).
COPY . /app/rag_service/

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir /app/rag_service

# Expose API port
EXPOSE 8081

# Run the API (now rag_service is a proper module)
## The project layout places the FastAPI app module at the repository root (`api.py`).
## Importing `rag_service.api` from the image can fail because the project root
## itself is the package directory. Run uvicorn against the local `api` module
## (present at /app/api.py) to avoid import issues.
## Use the installed package entrypoint now: pip install . installs the package
## so the fully-qualified module path `rag_service.api:app` should be importable.
CMD ["uvicorn", "rag_service.api:app", "--host", "0.0.0.0", "--port", "8081"]
