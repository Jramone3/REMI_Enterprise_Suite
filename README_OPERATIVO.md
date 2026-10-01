REMI Enterprise Suite — README Operativo

Resumen
-------
Este README operativo explica cómo levantar, probar y validar localmente la REMI Enterprise Suite en modo contenedores (docker-compose) y en modo desarrollo directo con Python/Streamlit.

Requisitos previos
------------------
- Docker & Docker Compose (v2+) si usas contenedores
- Python 3.10 si ejecutas localmente
- Git

Variables de entorno (mínimas)
------------------------------
- REMI_PAYMENT_ADDRESS  -> Dirección de recepción de pagos (obligatoria)
- BASE_RPC_URL          -> RPC para la red Base (ej: https://mainnet.base.org)
- MONGO_URI             -> Cadena de conexión a Mongo (ej: mongodb://mongo:27017)
- REMI_DB_NAME          -> Nombre de la base de datos (por defecto remi_enterprise)
- EXPECTED_TOKEN_ADDRESS-> Dirección del token ERC-20 si validas tokens (vacío para nativo ETH)
- EXPECTED_TOKEN_DECIMALS -> Decimales del token (6 para USDT/USDC)
- LLM_HOST              -> URL del servicio LLM local

Modo 1 — Levantar con Docker Compose
------------------------------------
1. Copiar el ejemplo de entorno:
   cp .env.example .env
2. Construir y levantar servicios:
   docker compose up --build -d
3. Accede a la UI: http://localhost:8501

Modo 2 — Ejecución local (sin Docker)
-------------------------------------
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
streamlit run app.py
