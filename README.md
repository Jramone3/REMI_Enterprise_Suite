# REMI Enterprise Suite

[![REMI Enterprise CI](https://github.com/Jramone3/REMI_Enterprise_Suite/actions/workflows/ci.yml/badge.svg)](https://github.com/Jramone3/REMI_Enterprise_Suite/actions/workflows/ci.yml)

Framework multi-agente basado en FastAPI, MongoDB y Docker, diseñado para la automatización de procesos backend, pasarelas de autenticación y verificación de licencias on-chain.

---

## 📂 Estructura del Proyecto

text
REMI_CORE/
├── .github/workflows/ci.yml     # Pipeline de integración continua (CI/CD)
├── auth_gateways/               # Módulos de lógica central y pasarelas
│   ├── db.py                    # Conexión resiliente a MongoDB
│   ├── license_service.py       # Servicio de gestión y validación de licencias
│   ├── remi_token_gateway.py    # Pasarela de tokens
│   └── remi_tx_validator.py     # Validador de transacciones
├── devops_config/               # Configuración de Docker y despliegue
├── tests/                       # Suite completa de pruebas con pytest
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Documentación principal

---

## ⚙️ Requisitos del Entorno

- **Python** 3.10 o superior
- **Docker** y Docker Compose
- **MongoDB** (instancia local ejecutándose en el puerto `27017` o URI remota)

---

## 🛠️ Configuración Local y Pruebas

1. **Clonar e instalar dependencias:**

bash
python -m pip install --upgrade pip
pip install -r requirements.txt

2. **Ejecutar la suite de pruebas unitarias con cobertura:**
El proyecto exige un umbral mínimo de cobertura del 35% en los módulos críticos

bash
PYTHONPATH=".:auth_gateways" pytest tests/ --cov=auth_gateways --cov-report=term-missing --cov-fail-under=35 -p no:pytest_ethereum.

---

## 🐳 Despliegue con Docker

1. **Construir la imagen de producción:**

bash
docker build -f devops_config/Dockerfile -t remi-enterprise:latest .

2. **Ejecutar el contenedor localmente con conectividad de red:**

bash
docker run -d --network host -e MONGO_URI="mongodb://localhost:27017" --name remi-app remi-enterprise:latest

3. **Verificar el estado del servicio:**

bash
curl http://localhost:5000/

---

## 🚀 CI/CD y Calidad de Código
El repositorio cuenta con integración continua automatizada a través de GitHub Actions que ejecuta:
- Instalación de dependencias y validación estricta de sintaxis.
- Pruebas unitarias e integración con cobertura mediante `pytest-cov`.
- Pruebas de integración containerizadas con Docker y control de tiempos de espera (*healthcheck* con reintentos).


