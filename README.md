# REMI Enterprise Suite

[![REMI Enterprise CI](https://github.com/Jramone3/REMI_Enterprise_Suite/actions/workflows/ci.yml/badge.svg)](https://github.com/Jramone3/REMI_Enterprise_Suite/actions/workflows/ci.yml)

[🇪🇸 Español](#español) | [🇬🇧 English](#english)

---

<a name="español"></a>
## 🇪🇸 Español

Framework multi-agente basado en FastAPI, MongoDB y Docker, diseñado para la automatización de procesos backend, auditorías de ciberinteligencia, pasarelas de autenticación y verificación de licencias on-chain.

### 📂 Estructura del Repositorio
```text
REMI_Enterprise_Suite/
├── .github/workflows/ci.yml     # Pipeline de integración continua (CI/CD)
├── auth_gateways/               # Pasarelas de autenticación y validación de tokens
├── core/                        # Motor principal, lifespan y orquestador
├── modules/                     # Módulos especializados de ciberinteligencia y auditoría
├── reports_analytics/           # Generación de reportes B2B y analíticas
├── devops_config/               # Configuración de Docker, Dockerfiles y despliegue
├── tests/                       # Suite completa de pruebas unitarias con pytest
├── requirements.txt             # Dependencias principales del proyecto
└── README.md                    # Documentación principal
```

### ⚙️ Requisitos del Entorno
- **Python** 3.10 o superior
- **Docker** y Docker Compose
- **MongoDB** (instancia local ejecutándose en el puerto `27017` o URI remota)

### 🛠️ Configuración Local y Pruebas

1. **Clonar e instalar dependencias:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. **Ejecutar la suite de pruebas unitarias con cobertura (mínimo 35%):**
```bash
PYTHONPATH=".:auth_gateways:core" pytest tests/ --cov=auth_gateways --cov-report=term-missing --cov-fail-under=35 -p no:pytest_ethereum
```

### 🐳 Despliegue con Docker

1. **Construir la imagen de producción:**
```bash
docker build -f devops_config/Dockerfile -t remi-enterprise:latest .
```

2. **Ejecutar el contenedor localmente:**
```bash
docker run -d --network host -e MONGO_URI="mongodb://localhost:27017" --name remi-app remi-enterprise:latest
```

3. **Verificar el estado del servicio:**
```bash
curl http://localhost:5000/
```

---

<a name="english"></a>
## 🇬🇧 English

Multi-agent framework powered by FastAPI, MongoDB, and Docker, engineered for backend automation, cyber intelligence audits, authentication gateways, and on-chain license verification.

### 📂 Repository Structure
```text
REMI_Enterprise_Suite/
├── .github/workflows/ci.yml     # CI/CD automation pipeline
├── auth_gateways/               # Authentication gateways & token validation
├── core/                        # Main engine, lifespan, and orchestrator
├── modules/                     # Cyber intelligence and audit specialized modules
├── reports_analytics/           # B2B report generation and analytics
├── devops_config/               # Docker configurations, Dockerfiles, and deployment
├── tests/                       # Complete unit test suite with pytest
├── requirements.txt             # Project main dependencies
└── README.md                    # Main documentation
```

### ⚙️ Environment Requirements
- **Python** 3.10 or higher
- **Docker** & Docker Compose
- **MongoDB** (local instance running on port `27017` or remote URI)

### 🛠️ Local Setup & Testing

1. **Clone and install dependencies:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. **Run unit tests with coverage (minimum 35% threshold):**
```bash
PYTHONPATH=".:auth_gateways:core" pytest tests/ --cov=auth_gateways --cov-report=term-missing --cov-fail-under=35 -p no:pytest_ethereum
```

### 🐳 Docker Deployment

1. **Build the production image:**
```bash
docker build -f devops_config/Dockerfile -t remi-enterprise:latest .
```

2. **Run the container locally:**
```bash
docker run -d --network host -e MONGO_URI="mongodb://localhost:27017" --name remi-app remi-enterprise:latest
```

3. **Verify service health:**
```bash
curl http://localhost:5000/
```

---

## 🚀 CI/CD & Code Quality
Automated continuous integration via GitHub Actions executing syntax validation, unit testing with pytest-cov, and containerized integration checks.
