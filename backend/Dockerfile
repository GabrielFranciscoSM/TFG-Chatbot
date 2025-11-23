FROM python:3.14-slim

WORKDIR /app

ARG INSTALL_DEV=false

COPY backend backend/

RUN pip install --upgrade pip setuptools wheel && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        pip install "./backend[dev]"; \
    else \
        pip install ./backend; \
    fi

EXPOSE 8000

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
