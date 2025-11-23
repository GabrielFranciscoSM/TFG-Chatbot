# Usar imagen base de Python 3.14
FROM python:3.14-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Build args to control optional dev dependency installation
ARG INSTALL_DEV=false

# Copiar el código del backend (incluye pyproject.toml)
# Copiar el código del chatbot (incluye pyproject.toml)
COPY chatbot chatbot/

# Upgrade pip/build tools and install the chatbot package so pip reads
# dependencies from chatbot/pyproject.toml. If INSTALL_DEV=true, install
# the optional 'dev' extras declared in pyproject.toml (e.g. pytest).
RUN pip install --upgrade pip setuptools wheel && \
	if [ "$INSTALL_DEV" = "true" ]; then \
		echo "Installing dev extras for chatbot" && \
		pip install "./chatbot[dev]"; \
	else \
		pip install ./chatbot; \
	fi

# Exponer el puerto en el que correrá la API (puedes cambiarlo según necesites)
EXPOSE 8080

# Comando para ejecutar la aplicación con uvicorn
CMD ["uvicorn", "chatbot.api:app", "--host", "0.0.0.0", "--port", "8080"]
