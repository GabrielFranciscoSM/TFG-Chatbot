# Usar imagen base de Python 3.12
FROM python:3.12-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /backend

# Copiar los archivos de requisitos primero (para aprovechar caché de Docker)
COPY backend/requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend .

# Exponer el puerto en el que correrá la API (puedes cambiarlo según necesites)
EXPOSE 8080

# Comando para ejecutar la aplicación con uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
