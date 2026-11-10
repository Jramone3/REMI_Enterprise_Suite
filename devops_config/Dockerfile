FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY . .

# Variables de entorno por defecto
ENV PORT=5000
EXPOSE 5000

# Comando canónico de arranque unificado apuntando a auth_gateways.license_service
CMD ["uvicorn", "auth_gateways.license_service:app", "--host", "0.0.0.0", "--port", "5000"]
