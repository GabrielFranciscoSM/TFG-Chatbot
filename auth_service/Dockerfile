FROM python:3.14-slim

WORKDIR /app

ARG INSTALL_DEV=false

COPY auth_service auth_service/

RUN pip install --upgrade pip setuptools wheel && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        pip install "./auth_service[dev]"; \
    else \
        pip install ./auth_service; \
    fi

EXPOSE 8083

CMD ["uvicorn", "auth_service.api:app", "--host", "0.0.0.0", "--port", "8083"]
