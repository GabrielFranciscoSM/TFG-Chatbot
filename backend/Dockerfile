# =============================================================================
# Stage 1: Build dependencies
# =============================================================================
FROM python:3.14-slim AS builder

WORKDIR /build

# Install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy only pyproject.toml first for better caching
COPY backend/pyproject.toml backend/
COPY backend/__init__.py backend/

# Install dependencies (cached if pyproject.toml unchanged)
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir "./backend[dev]"; \
    else \
        pip install --no-cache-dir ./backend; \
    fi

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.14-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY backend backend/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
