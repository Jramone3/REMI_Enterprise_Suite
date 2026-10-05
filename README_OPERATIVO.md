REMI Enterprise Suite — README Operativo

Resumen
-------
Este README operativo explica cómo levantar, probar y validar localmente la REMI Enterprise Suite en modo contenedores (docker-compose), en modo desarrollo directo con Python/Streamlit, y el microservicio de licencias FastAPI.

Requisitos previos
------------------
- Docker & Docker Compose (v2+) si usas contenedores
- Python 3.10 si ejecutas localmente
- Git
- (Opcional) gh CLI para crear PRs/branches

Variables de entorno (mínimas y obligatorias)
--------------------------------------------
Asegúrate de definir al menos las variables siguientes antes de ejecutar la aplicación (el validador estricto detendrá el arranque si falta alguna crítica):
- REMI_PAYMENT_ADDRESS -> Dirección de recepción de pagos (obligatoria; no usar la dirección por defecto en producción)
- BASE_RPC_URL         -> RPC para la red Base (por ejemplo https://mainnet.base.org)
- MONGO_URI            -> Cadena de conexión a Mongo (ej: mongodb://mongo:27017 cuando usas docker-compose)
- REMI_DB_NAME         -> Nombre de la base de datos (por defecto remi_enterprise)
- GITHUB_BOT_TOKEN     -> Token de acceso personal de GitHub para automatización de Issues y PRs
- EXPECTED_TOKEN_ADDRESS-> Dirección del token ERC-20 si validas tokens (vacío para nativo ETH)
- EXPECTED_TOKEN_DECIMALS -> Decimales del token (6 para USDT/USDC)
- LLM_HOST             -> URL del servicio LLM local (por defecto http://host.docker.internal:11434)

Modo 1 — Levantar con Docker Compose (recomendado para dev reproducible)
------------------------------------------------------------------------
1. Copiar el ejemplo de entorno y editar variables:
   cp .env.example .env
   # Edita .env o exporta variables en tu entorno

2. Construir y levantar servicios:
   docker compose up --build -d

3. Ver logs:
   docker compose logs -f streamlit
   # o
   docker compose logs -f mongo

4. Accede a la UI: http://localhost:8501

Modo 2 — Ejecución local (sin Docker)
-------------------------------------
1. Crear y activar entorno virtual:
   python -m venv .venv
   source .venv/bin/activate

2. Instalar dependencias:
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

3. Exportar variables de entorno (ejemplo):
   export MONGO_URI=mongodb://localhost:27017
   export REMI_DB_NAME=remi_enterprise
   export REMI_PAYMENT_ADDRESS=0x96De980a766CCb10A19B6962587e2b61B650b372
   export BASE_RPC_URL=https://mainnet.base.org
   export GITHUB_BOT_TOKEN=tu_token_aqui
   export LLM_HOST=http://localhost:11434

4. Ejecutar la app (Streamlit):
   streamlit run app.py

5. Ejecutar el microservicio de licencias (FastAPI):
   uvicorn license_service:app --host 0.0.0.0 --port 8000 --reload

Pruebas y calidad de código
---------------------------
Ejecuta la suite de pruebas y linters antes de abrir un PR.
# Tests unitarios
python -m unittest discover -s tests -p "test_*.py"

CI
--
La carpeta .github/workflows contiene un flujo CI que ejecuta validaciones y pruebas en Python 3.10. Asegúrate de que requirements-dev.txt esté actualizado.

Notas operativas / troubleshooting
---------------------------------
- Asegúrate que REMI_PAYMENT_ADDRESS esté configurada; la app se detendrá de forma segura si no está presente.
- Si la verificación on-chain falla, revisa que BASE_RPC_URL apunte a un proveedor RPC válido y accesible.
- LLM: la UI espera un servicio LLM disponible en LLM_HOST.
- Mongo: comprueba que el servicio esté en ejecución y que la colección licenses reciba documentos tras emitir una licencia.

Comandos útiles
---------------
- Levantar en primer plano: docker compose up --build
- Parar y limpiar: docker compose down -v
- Ver logs: docker compose logs -f
- Crear branch y PR (con gh):
  git checkout -b feat/remi-updates
  git add .
  git commit -m "feat: actualizacion integral de microservicio, ui y docs"
  git push origin main

Contacto y soporte
------------------
- Para soporte operativo y despliegues: soporte@remi-enterprise.com
- Para ventas/SLAs: commercial@remi-enterprise.com


REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg

---

## 📈 Historial de Cambios y Reporte Técnico: Versión 2.2.0 (Edición Comercial)

### 📋 Resumen Ejecutivo
Se ha completado la refactorización integral, unificación de código y actualización del portal frontend de **REMI Enterprise Suite** (`app.py`). La nueva versión fusiona de manera transparente las capacidades de IA soberana local (Ollama/Llama3), el monitoreo del backend en tiempo real, el sistema avanzado de licenciamiento dual (On-Chain/Stripe) y la automatización de issues en GitHub dentro de un diseño visual unificado de nivel ejecutivo (Modo Búnker / Tech Dark).

### 🛠️ Cambios Realizados
- **Unificación de Interfaz y Diseño UI/UX (`app.py`)**: Consolidación de un diseño de estilo corporativo oscuro optimizado para contenedores y escritorios Linux (`ramon-desktop`), usando tarjetas métricas estilizadas y botones interactivos responsivos.
- **Módulos Operativos Integrados en Pestañas**:
  - **💬 Centro de Comando (Chat)**: Integración nativa con el motor local Ollama (`llama3`) con system prompt especializado.
  - **🔑 Adquisición de Licencias Enterprise**: Interfaz de doble carril (Pago Cripto on-chain en red Base y Pago Fiduciario vía Stripe).
  - **🔍 Verificador de Estado de Licencia**: Consulta en tiempo real sobre la base de datos MongoDB.
  - **🐙 Automatización GitHub**: Creación automatizada de issues técnicos conectados al repositorio oficial.
- **Diagnóstico de Conectividad**: Módulo de sondeo de estado (*Health Check*) en barra lateral para verificar la disponibilidad del microservicio backend (`API_BASE_URL`).

### 🚀 Control de Versiones
- **Commit unificado de frontend**: `2b2568f`
- **Rama**: `main`
- **Repositorio**: [Jramone3/REMI_Enterprise_Suite](https://github.com/Jramone3/REMI_Enterprise_Suite.git)
