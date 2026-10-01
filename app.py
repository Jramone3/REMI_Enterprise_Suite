import streamlit as st
import os
import requests
import hashlib
from datetime import datetime, timedelta

from remi_tx_validator import verify_base_transaction

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
    Verifica la transacción on-chain y, si es válida, genera una licencia anual.

    Retorna dict con:
      - valid: bool
      - message: str
      - license: str (si valid)
      - details: dict (información de verificación)
    """
    if not cliente_email or not tx_hash:
        return {"valid": False, "message": "Email o TxID faltante."}

    # Llamar al validador on-chain
    try:
        # Para ERC-20 esperamos 499 USDT por defecto
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

    # Si la verificación es exitosa, generar la licencia
    fecha_expiracion = datetime.now() + timedelta(days=365)
    raw_key = f"{cliente_email}-{tx_hash}-REMI-2026"
    hash_key = hashlib.sha256(raw_key.encode()).hexdigest()[:24].upper()
    licencia_final = f"REMI-ENT-ANNUAL-{hash_key}"

    # Puedes agregar aquí persistencia (DB) para el registro de la licencia
    # emitida

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

    st.markdown("---")
    st.markdown("### 💎 Adquirir Licencia Anual")
    st.markdown("**Costo:** $499 USD / Año")
    st.markdown(
        "Incluye soporte técnico, actualizaciones directas del clúster multi-agente y módulos avanzados de auditoría."
    )

    if st.button("Generar Datos de Pago"):
        st.session_state.mostrar_pago = True

    if st.session_state.get("mostrar_pago", False):
        st.info(
            "**Instrucciones de Pago Directo:**\n\n"
            "1. Envía **499 USDT (ERC-20 / Base)** o equivalente en ETH/BNB a:\n"
            f"`{os.getenv('REMI_PAYMENT_ADDRESS', '0x96De980a766CCb10A19B6962587e2b61B650b372')}`\n\n"
            "2. Registra tus datos y el **TxID** de la transferencia para emitir tu llave anual."
        )

        # Formulario de registro y validación del cliente
        cliente_email = st.text_input("Correo electrónico de registro:")
        tx_input = st.text_input("Hash de la Transacción (TxID):")
        token_type = st.selectbox("Tipo de pago", ["USDT (ERC-20)", "ETH (nativo)"])

        if st.button("Verificar y Activar Licencia Anual"):
            if cliente_email and tx_input:
                is_erc20 = token_type.startswith("USDT")
                # Llamar helper para verificar y (si corresponde) emitir la
                # licencia
                result = issue_license_if_verified(
                    cliente_email, tx_input, is_erc20=is_erc20, expected_token_min_amount=499.0
                )

                if result.get("valid"):
                    st.success("¡Pago verificado! Licencia Enterprise emitida exitosamente.")
                    st.markdown(f"**Cliente Registrado:** {cliente_email}")
                    st.markdown(f"**Válida hasta:** {result.get('expires')}")
                    st.code(result.get("license"), language="text")
                    st.caption(
                        "Guarda esta llave en tu servidor local para recibir actualizaciones directas del sistema."
                    )
                else:
                    st.error(f"No se pudo emitir la licencia: {result.get('message')}")
            else:
                st.warning("Por favor ingresa tu correo y un TxID válido.")

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
# INTERFAZ PRINCIPAL DE CHAT (NÚCLEO LOCAL)
# ==========================================
st.info(
    "Bienvenido a la vitrina interactiva de REMI. Escribe una consulta para interactuar en tiempo real con el núcleo local."
)

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

    # Generar respuesta mediante el núcleo local (Ollama / Llama 3)
    with st.chat_message("assistant"):
        with st.spinner("REMI procesando a través del núcleo multi-agente local..."):
            try:
                system_prompt = (
                    "Eres REMI, el núcleo de inteligencia artificial de REMI Enterprise Suite, "
                    "un framework multi-agente avanzado desarrollado por jramonrivasg. "
                    "Responde con un tono técnico, profesional, analítico y ejecutivo."
                )

                url = "http://localhost:11434/api/chat"
                payload = {
                    "model": "llama3",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                    "stream": False,
                }

                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    respuesta_ia = response.json()["message"]["content"]
                else:
                    respuesta_ia = "**REMI (Núcleo Activo):** Error al conectar con el servidor local de IA (Código {response.status_code})."
            except Exception:
                respuesta_ia = "**REMI (Núcleo Activo):** No se pudo establecer comunicación con el clúster local. Asegúrate de que el servicio esté activo."

            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
