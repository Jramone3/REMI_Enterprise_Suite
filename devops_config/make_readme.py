content = """# 🛡️ REMI Enterprise Suite — README Operativo

## Resumen
Este README operativo explica cómo levantar, probar y validar localmente la REMI Enterprise Suite en modo contenedores (`docker-compose`), en modo desarrollo directo con Python/Streamlit, y el microservicio de licencias basado en FastAPI.

---

## ⚙ Requisitos previos
- Docker & Docker Compose (v2+) si usas contenedores
- Python 3.10 si ejecutas localmente
- Git

---

## 🔐 Variables de entorno (Crítico)
El sistema valida estrictamente la presencia de variables de entorno críticas al arrancar; si falta alguna obligatoria, el proceso se detendrá de forma segura para evitar fallos operativos en producción.

Copia el archivo de ejemplo y configura tus valores reales:
```bash
cp .env.example .env
Variables obligatorias (.env):
REMI_PAYMENT_ADDRESS: Dirección EOA o contrato de recepción de pagos (obligatoria; no usar valores por defecto en producción).

BASE_RPC_URL: Endpoint RPC para la red Base (por ejemplo, https://mainnet.base.org).

MONGO_URI: Cadena de conexión a MongoDB (ej. mongodb://localhost:27017 o mongodb://mongo:27017 con Docker).

REMI_DB_NAME: Nombre de la base de datos (por defecto remi_enterprise).

GITHUB_BOT_TOKEN: Token de acceso personal de GitHub para la automatización e integración de Issues y PRs.

LLM_HOST: URL del servicio LLM local (por defecto http://localhost:11434 o http://host.docker.internal:11434).

🚀 Modo 1 — Levantar con Docker Compose (Recomendado)
Configura tu archivo .env basado en .env.example.

Construye y levanta los servicios en segundo plano:

Bash
docker compose up --build -d
Monitorea los logs de los contenedores:

Bash
docker compose logs -f streamlit
Accede a la interfaz de Streamlit en: http://localhost:8501

💻 Modo 2 — Ejecución local (Sin Docker)
Crear y activar el entorno virtual:

Bash
python -m venv .venv
source .venv/bin/activate
Instalar dependencias:

Bash
pip install --upgrade pip
pip install -r requirements.txt
Exportar o configurar las variables de entorno en tu shell o archivo .env.

Ejecutar la interfaz principal (Streamlit):

Bash
streamlit run app.py
Ejecutar el microservicio de licencias (FastAPI):

Bash
uvicorn license_service:app --host 0.0.0.0 --port 8000 --reload
🧪 Pruebas y Calidad de Código
Ejecuta la suite de pruebas unitarias antes de integrar cambios:

Bash
python -m unittest discover -s tests -p "test_*.py"
🛠️ Notas Operativas / Troubleshooting
Validador de entorno: Si la app se detiene al iniciar con un error crítico, verifica que REMI_PAYMENT_ADDRESS y BASE_RPC_URL estén correctamente definidas en tu entorno.

Conectividad Blockchain: Si la emisión de licencias on-chain falla, comprueba que el RPC de Base responda adecuadamente y que el tx_hash sea válido.

MongoDB: Asegúrate de que el servicio de base de datos esté activo para que la persistencia automática de licencias y la validación en el búnker funcionen correctamente.

REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg
"""

with open("README_OPERATIVO.md", "w", encoding="utf-8") as f:
f.write(content)

print("¡README_OPERATIVO.md generado de forma íntegra y perfecta!")
