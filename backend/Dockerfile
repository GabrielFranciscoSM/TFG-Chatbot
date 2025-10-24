# Usar imagen base de Python 3.12
FROM python:3.12-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el código del backend (incluye pyproject.toml)
COPY backend backend/

# Upgrade pip/build tools and install the backend package so pip reads
# dependencies from backend/pyproject.toml
RUN pip install --upgrade pip setuptools wheel && \
	pip install --no-cache-dir ./backend

# Exponer el puerto en el que correrá la API (puedes cambiarlo según necesites)
EXPOSE 8080

# Comando para ejecutar la aplicación con uvicorn
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8080"]
