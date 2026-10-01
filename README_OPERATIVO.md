REMI Enterprise Suite — README Operativo

Resumen
-------
Este README operativo explica cómo levantar, probar y validar localmente la REMI Enterprise Suite en modo contenedores (docker-compose) y en modo desarrollo directo con Python/Streamlit.

Requisitos previos
------------------
- Docker & Docker Compose (v2+) si usas contenedores
- Python 3.10 si ejecutas localmente
- Git
- (Opcional) gh CLI para crear PRs/branches

Variables de entorno (mínimas)
------------------------------
Asegúrate de definir al menos las variables siguientes antes de ejecutar la aplicación.
- REMI_PAYMENT_ADDRESS  -> Dirección de recepción de pagos (obligatoria; no usar la dirección por defecto en producción)
- BASE_RPC_URL          -> RPC para la red Base (por ejemplo https://mainnet.base.org)
- MONGO_URI             -> Cadena de conexión a Mongo (ej: mongodb://mongo:27017 cuando usas docker-compose)
- REMI_DB_NAME          -> Nombre de la base de datos (por defecto remi_enterprise)
- EXPECTED_TOKEN_ADDRESS-> Dirección del token ERC-20 si validas tokens (vacío para nativo ETH)
- EXPECTED_TOKEN_DECIMALS -> Decimales del token (6 para USDT/USDC)
- LLM_HOST              -> URL del servicio LLM local (por defecto http://host.docker.internal:11434)

Modo 1 — Levantar con Docker Compose (recomendado para dev reproducible)
------------------------------------------------------------------------
1. Copiar el ejemplo de entorno y editar variables:

```bash
cp .env.example .env
# Edita .env o exporta variables en tu entorno
```

2. Construir y levantar servicios:

```bash
docker compose up --build -d
```

3. Ver logs:

```bash
docker compose logs -f streamlit
# o
docker compose logs -f mongo
```

4. Accede a la UI: http://localhost:8501

Modo 2 — Ejecución local (sin Docker)
-------------------------------------
1. Crear y activar entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. Exportar variables de entorno (ejemplo):

```bash
export MONGO_URI=mongodb://localhost:27017
export REMI_DB_NAME=remi_enterprise
export REMI_PAYMENT_ADDRESS=0xYOUR_PAYMENT_ADDRESS
export BASE_RPC_URL=https://mainnet.base.org
export LLM_HOST=http://localhost:11434
```

4. Ejecutar la app:

```bash
streamlit run app.py
```

Pruebas y calidad de código
---------------------------
Ejecuta la suite de pruebas y linters antes de abrir un PR.

```bash
# Tests
pytest -q

# Linter
flake8 . --max-line-length=120
```

CI
--
La carpeta .github/workflows contiene un flujo CI que ejecuta flake8 y pytest en Python 3.10. Asegúrate de que requirements-dev.txt esté actualizado para incluir dependencias de test (pymongo, pytest-mock, etc.).

Notas operativas / troubleshooting
---------------------------------
- Asegúrate que REMI_PAYMENT_ADDRESS esté configurada; la app debería advertir o fallar si no está presente.
- Si la verificación on-chain falla, revisa que BASE_RPC_URL apunte a un proveedor RPC válido y accesible desde el contenedor.
- LLM: la UI espera un servicio LLM disponible en LLM_HOST. Si usas contenedores, en Windows/Mac usar host.docker.internal para direccionar a la máquina host. Alternativamente, desplegar el LLM en una IP accesible y actualizar LLM_HOST.
- Mongo: comprueba que el servicio esté en ejecución y que la colección licenses reciba documentos tras emitir una licencia.

Comandos útiles
---------------
- Levantar en primer plano: docker compose up --build
- Parar y limpiar: docker compose down -v
- Ver logs: docker compose logs -f
- Crear branch y PR (con gh):
  git checkout -b feat/persist-licenses
  git add .
  git commit -m "feat: persistencia de licencias (MongoDB)"
  git push origin feat/persist-licenses
  gh pr create --title "feat: persistencia de licencias" --body "Agrega persistencia MongoDB para licencias" --base main

Contacto y soporte
------------------
- Para soporte operativo y despliegues: soporte@remi-enterprise.com
- Para ventas/SLAs: commercial@remi-enterprise.com

