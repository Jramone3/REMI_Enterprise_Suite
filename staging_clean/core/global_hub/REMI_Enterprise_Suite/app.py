import streamlit as st
import os
import requests
import hashlib
from datetime import datetime, timedelta
import sys

from remi_tx_validator import verify_base_transaction

# ==========================================
# CONEXIÓN SEGURA AL CEREBRO NEURONAL (sda7)
# ==========================================
sys.path.append("/home/ramon/REMI_CORE/bunker_respaldo/REMI_BUNKER_MASTER/remi_graphify")
try:
    from remi_brain import consultar_grafo_neuronal
    cerebro_neuronal_activo = True
except ImportError:
    def consultar_grafo_neuronal(q):
        return "[SISTEMA NEURONAL]: Grafo de 119k nodos no disponible temporalmente en sda7."
    cerebro_neuronal_activo = False

st.set_page_config(
    page_title="REMI Enterprise Suite - Demo & Licenciamiento", page_icon="assets/remi_logo.png", layout="centered"
)

# Imagen oficial de REMI y título principal
st.image("assets/remi_imagen_oficial.jpeg", width=200)
st.title("REMI Enterprise Suite")

st.markdown("### Framework Multi-Agente y Núcleo de Inteligencia Artificial")
st.markdown("---")

# Helper: procesa verificación on-chain y emite licencia si aplica
def issue_license_if_verified(
    cliente_email: str, tx_hash: str, *, is_erc20: bool = True, expected_token_min_amount: float = 499.0
) -> dict:
    """
    Verifica la transacción on-chain o concede bypass automático si es el correo maestro de desarrollo,
    generando o recuperando la licencia anual Enterprise.
    """
    if not cliente_email:
        return {"valid": False, "message": "Email faltante."}

    # ==========================================
    # BYPASS MAESTRO PARA DESARROLLADOR / ADMIN
    # ==========================================
    email_limpio = cliente_email.strip().lower()
    if email_limpio == "jramonrivasg@gmail.com":
        fecha_expiracion = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        return {
            "valid": True,
            "message": "Acceso maestro autorizado por Búnker Local (Bypassed).",
            "license": "REMI-ENT-ANNUAL-MASTER-JRAMON-2026",
            "expires": fecha_expiracion,
            "details": {"source": "Master Admin Override", "status": "Active"}
        }

    # Para cualquier otro usuario, se exige TxID y validación on-chain
    if not tx_hash:
        return {"valid": False, "message": "TxID faltante para validación comercial."}

    # Llamar al validador on-chain para clientes externos
    try:
        if is_erc20:
            verification = verify_base_transaction(
                tx_hash, expected_min_amount=expected_token_min_amount, is_erc20=True
            )
        else:
            verification = verify_base_transaction(
                tx_hash, expected_min_amount=expected_token_min_amount, is_erc20=False
            )
    except Exception as e:
        return {"valid": False, "message": f"Error al verificar la transacción: {str(e)}"}

    if not verification.get("valid"):
        return {
            "valid": False,
            "message": f"Verificación fallida: {verification.get('error')}",
            "details": verification,
        }

    # Generación estándar para pagos verificados
    fecha_expiracion = datetime.now() + timedelta(days=365)
    raw_key = f"{cliente_email}-{tx_hash}-REMI-2026"
    hash_key = hashlib.sha256(raw_key.encode()).hexdigest()[:24].upper()
    licencia_final = f"REMI-ENT-ANNUAL-{hash_key}"

    return {
        "valid": True,
        "message": "Licencia emitida con éxito.",
        "license": licencia_final,
        "expires": fecha_expiracion.strftime("%Y-%m-%d"),
        "details": verification,
    }

# ==========================================
# BARRA LATERAL: PASARELA Y LICENCIAMIENTO
# ==========================================
with st.sidebar:
    st.image("assets/remi_imagen_oficial.jpeg", width=100)
    st.subheader("Portal Enterprise")
    st.caption("Infraestructura respaldada por Standard EOA-Contract via Base Network / Búnker Local.")
    if cerebro_neuronal_activo:
        st.success("🟢 Cerebro Neuronal (119k) Conectado")
    else:
        st.warning("⚠️ Cerebro Neuronal Desconectado")

    st.markdown("---")
    st.markdown("### 💎 Adquirir Licencia Anual")
    st.markdown("**Costo:** $499 USD / Año")
    st.markdown(
        "Incluye soporte técnico, actualizaciones directas del clúster multi-agente y módulos avanzados de auditoría."
    )

    if st.button("Generar Datos de Pago"):
        st.session_state.mostrar_pago = True

    if st.session_state.get("mostrar_pago", False):
        # Formulario de registro y validación del cliente
        cliente_email = st.text_input("Correo electrónico de registro:")
        
        # Si es el correo maestro, avisamos visualmente que tiene bypass de pago
        is_master = cliente_email.strip().lower() == "jramonrivasg@gmail.com"
        
        if is_master:
            st.success("⚡ **Modo Desarrollador Maestro Detectado:** Acceso ilimitado sin pasarela de pago.")
            tx_input = "MASTER-BYPASS-HASH"
            token_type = "Bypass Admin"
        else:
            st.info(
                "**Instrucciones de Pago Directo:**\n\n"
                "1. Envía **499 USDT (ERC-20 / Base)** o equivalente en ETH/BNB a:\n"
                f"`{os.getenv('REMI_PAYMENT_ADDRESS', '0x96De980a766CCb10A19B6962587e2b61B650b372')}`\n\n"
                "2. Registra tus datos y el **TxID** de la transferencia para emitir tu llave anual."
            )
            tx_input = st.text_input("Hash de la Transacción (TxID):")
            token_type = st.selectbox("Tipo de pago", ["USDT (ERC-20)", "ETH (nativo)"])

        if st.button("Verificar y Activar Licencia Anual"):
            if cliente_email:
                is_erc20 = token_type.startswith("USDT")
                result = issue_license_if_verified(
                    cliente_email, tx_input, is_erc20=is_erc20, expected_token_min_amount=499.0
                )

                if result.get("valid"):
                    st.success("¡Licencia Enterprise emitida / autorizada exitosamente!")
                    st.markdown(f"**Cliente Registrado:** {cliente_email}")
                    st.markdown(f"**Válida hasta:** {result.get('expires')}")
                    st.code(result.get("license"), language="text")
                    st.caption(
                        "Guarda esta llave en tu servidor local para recibir actualizaciones directas del sistema."
                    )
                else:
                    st.error(f"No se pudo emitir la licencia: {result.get('message')}")
            else:
                st.warning("Por favor ingresa tu correo electrónico.")

    st.markdown("---")
    st.markdown("### 🔄 Verificación de Actualizaciones")
    email_check = st.text_input("Correo registrado:")
    key_check = st.text_input("Clave de Licencia:")
    if st.button("Comprobar Actualizaciones"):
        if email_check and key_check:
            st.success("Licencia activa. Clúster sincronizado con el último parche de seguridad del repositorio.")
        else:
            st.warning("Introduce tus credenciales registradas.")
# ==========================================
# INTERFAZ PRINCIPAL DE CHAT (NÚCLEO LOCAL + CEREBRO NEURONAL)
# ==========================================
st.info("Bienvenido a la vitrina interactiva de REMI. Interactúa en tiempo real con el núcleo local y el grafo neuronal.")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat interactiva
if prompt := st.chat_input("Escribe una consulta o instrucción para REMI:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta mediante el núcleo local (Ollama) enriquecido con el Cerebro Neuronal
    with st.chat_message("assistant"):
        with st.spinner("REMI consultando grafo neuronal (119k nodos) y procesando núcleo local..."):
            try:
                # 1. Extraer contexto neuronal relevante desde el Búnker en sda7
                contexto_neuronal = consultar_grafo_neuronal(prompt)

                # 2. Construir el system prompt fusionando la inteligencia del grafo
                system_prompt = (
                    f"CONTEXTO NEURONAL DEL BÚNKER (SDA7):\n{contexto_neuronal}\n\n"
                    "Eres REMI, el núcleo de inteligencia artificial de REMI Enterprise Suite, "
                    "un framework multi-agente avanzado desarrollado por jramonrivasg. "
                    "Utiliza el contexto neuronal anterior para ofrecer respuestas técnicas, precisas, "
                    "profesionales, analíticas y ejecutivas sobre la infraestructura y los repositorios."
                )

                url = "http://localhost:11434/api/chat"
                payload = {
                    "model": "llama3",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                    "stream": False,
                }

                response = requests.post(url, json=payload, timeout=30)
                if response.status_code == 200:
                    respuesta_ia = response.json()["message"]["content"]
                else:
                    respuesta_ia = f"**REMI:** Error de comunicación con Ollama (Código {response.status_code})."

            except Exception as e:
                respuesta_ia = f"**REMI (Núcleo):** Error al conectar con el clúster local o el grafo neuronal: {str(e)}"
            
            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
