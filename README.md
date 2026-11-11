# REMI Enterprise Suite

Framework multi-agente basado en FastAPI, MongoDB y Docker, diseñado para la automatización de procesos backend y verificación de licencias.

## Requisitos del Entorno
- Python 3.10+
- Docker & Docker Compose
- MongoDB (local o URI remota)

## Configuración Local y Pruebas

1. **Instalar dependencias:**

python -m pip install --upgrade pip
pip install -r requirements.txt

2. **Ejecutar la suite de pruebas unitarias con cobertura:**

PYTHONPATH=".:auth_gateways" pytest tests/ --cov=auth_gateways --cov-report=term-missing --cov-fail-under=35 -p no:pytest_ethereum

## Despliegue con Docker

1. **Construir la imagen:**

docker build -f devops_config/Dockerfile -t remi-enterprise:latest .

2. **Ejecutar el contenedor localmente:**

docker run -d --network host -e MONGO_URI="mongodb://localhost:27017" --name remi-app remi-enterprise:latest


