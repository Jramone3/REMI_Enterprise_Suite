# REMI Enterprise Suite

Framework modular de IA multiagente para entornos empresariales, seguros y listos para producción.

REMI Enterprise Suite está diseñado para organizaciones que necesitan desplegar, administrar y escalar ecosistemas de IA multiagente en un entorno seguro y trazable. El proyecto combina un portal operativo basado en Streamlit, un microservicio de licencias en FastAPI, validación de pagos on-chain, persistencia con MongoDB e integración local con Ollama para ofrecer una plataforma empresarial completa.

## Resumen general

REMI Enterprise Suite ofrece un entorno operativo unificado para:
- orquestación multiagente y ejecución inteligente de tareas
- emisión y verificación segura de licencias
- validación de pagos on-chain en Base
- soporte de pagos fiduciarios mediante Stripe
- monitoreo operativo y registro de auditoría
- automatización de issues de GitHub para flujo de trabajo técnico

La arquitectura está diseñada para soportar despliegues empresariales con separación clara entre:
- presentación visual
- lógica de backend
- verificación de transacciones
- persistencia de datos
- automatización operativa

## Características principales

### Operación multiagente
La plataforma incluye un centro de comando para operaciones interactivas guiadas por IA y flujos empresariales. Se conecta con un endpoint local de LLM mediante Ollama y el modelo llama3, permitiendo chat operativo y asistencia inteligente.

### Gestión de licencias
El proyecto incluye un flujo de licenciamiento protegido:
- validación del cliente
- verificación de transacciones
- emisión de licencias
- consulta por correo
- control de expiración
- almacenamiento de auditoría en MongoDB

### Validación blockchain
Las transacciones se validan mediante RPC de Base, revisando el recibo de la transacción y los logs de transferencias ERC-20. Esto permite verificar transferencias de tokens, montos mínimos y destinatario final.

### Soporte Stripe / fiat
El sistema incluye un flujo comercial para pagos fiduciarios con pasarela Stripe y webhooks para emisión automática de licencias tras una compra exitosa.

### Integración con GitHub
El proyecto incluye automatización para crear issues utilizando un token de bot de GitHub, permitiendo gestionar tareas técnicas directamente desde la plataforma.

## Arquitectura del sistema

El repositorio está organizado en torno a una arquitectura modular empresarial:

- `app.py` — interfaz principal con Streamlit para control operativo y licenciamiento
- `license_service.py` — backend FastAPI para emisión y validación de licencias
- `remi_tx_validator.py` — lógica de validación on-chain en Base
- `db.py` — acceso a MongoDB, almacenamiento de licencias y auditoría
- `Dockerfile` / `docker-compose.yml` — soporte de despliegue mediante contenedores
- `scripts/` — utilidades operativas y de automatización
- `tests/` — pruebas y validaciones

## Stack tecnológico

- Python
- Streamlit
- FastAPI
- Uvicorn
- MongoDB / PyMongo
- Requests
- Web3 / eth-utils
- Docker / Docker Compose
- Ollama
- Scripts en Shell

## Requisitos previos

Para desarrollo local, asegúrate de contar con:
- Python 3.10+
- Git
- Docker y Docker Compose (opcional pero recomendado)
- Instancia de MongoDB
- Acceso a un endpoint RPC de Base
- Dirección de pago o billetera para validación
- Token de GitHub para automatización

## Variables de entorno

La aplicación depende de varias variables de entorno para operar de forma segura.

Variables obligatorias:
- `MONGO_URI`
- `REMI_DB_NAME`
- `REMI_PAYMENT_ADDRESS`
- `BASE_RPC_URL`
- `REMI_API_KEY`
- `LLM_HOST`

Variables opcionales:
- `EXPECTED_TOKEN_ADDRESS`
- `EXPECTED_TOKEN_DECIMALS`
- `GITHUB_BOT_TOKEN`
- `TEST_MODE`

Ejemplo:
```bash
export MONGO_URI="mongodb://localhost:27017"
export REMI_DB_NAME="remi_enterprise"
export REMI_PAYMENT_ADDRESS="0x96De980a766CCb10A19B6962587e2b61B650b372"
export BASE_RPC_URL="[https://mainnet.base.org](https://mainnet.base.org)"
export REMI_API_KEY="tu_clave_administrador"
export LLM_HOST="http://localhost:11434"
export GITHUB_BOT_TOKEN="tu_token_aqui"
