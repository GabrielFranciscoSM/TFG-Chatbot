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
COPY chatbot/pyproject.toml chatbot/
COPY chatbot/__init__.py chatbot/

# Install dependencies (cached if pyproject.toml unchanged)
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir "./chatbot[dev]"; \
    else \
        pip install --no-cache-dir ./chatbot; \
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
COPY chatbot chatbot/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["uvicorn", "chatbot.api:app", "--host", "0.0.0.0", "--port", "8080"]
