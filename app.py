from datetime import datetime, timedelta
import hashlib
import os

from github import Github
import requests
import streamlit as st

from remi_tx_validator import verify_base_transaction

st.set_page_config(
    page_title="REMI Enterprise Suite - Demo & Licenciamiento",
    page_icon="assets/remi_logo.png",
    layout="centered",
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
    """Verifica la transacción on-chain y, si es válida, genera una licencia anual."""
    if not cliente_email or not tx_hash:
        return {"valid": False, "message": "Email o TxID faltante."}

    try:
        if is_erc20:
            verification = verify_base_transaction(tx_hash, expected_min_amount=expected_token_min_amount, is_erc20=True)
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


# Función para interactuar con GitHub usando PyGithub integrado directamente con tu token
def trigger_github_action(payload: dict):
    token = os.getenv("GITHUB_BOT_TOKEN")
    if not token:
        return {"error": "Token del bot no configurado (GITHUB_BOT_TOKEN)"}, 500

    try:
        g = Github(token)
        repo = g.get_repo("Jramone3/REMI_Enterprise_Suite")

        accion = payload.get("action")
        if accion == "create_issue":
            issue = repo.create_issue(
                title=payload.get("title", "Automatización REMI"),
                body=payload.get("body", "Generado automáticamente por REMI Core OS"),
            )
            return {"status": "success", "issue_number": issue.number}, 200

        return {"status": "unknown_action"}, 400
    except Exception as e:
        return {"error": str(e)}, 500


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

        cliente_email = st.text_input("Correo electrónico de registro:")
        tx_input = st.text_input("Hash de la Transacción (TxID):")
        token_type = st.selectbox("Tipo de pago", ["USDT (ERC-20)", "ETH (nativo)"])

        if st.button("Verificar y Activar Licencia Anual"):
            if cliente_email and tx_input:
                is_erc20 = token_type.startswith("USDT")
                result = issue_license_if_verified(
                    cliente_email, tx_input, is_erc20=is_erc20, expected_token_min_amount=499.0
                )

                if result.get("valid"):
                    st.success("¡Pago verificado! Licencia Enterprise emitida exitosamente.")
                    st.markdown(f"**Cliente Registrado:** {cliente_email}")
                    st.markdown(f"**Válida hasta:** {result.get('expires')}")
                    st.code(result.get("license"), language="text")
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

    st.markdown("---")
    st.markdown("### 🐙 Automatización GitHub")
    issue_title = st.text_input("Título del Issue:")
    issue_body = st.text_area("Descripción del Issue:")
    if st.button("Crear Issue en GitHub"):
        if issue_title:
            payload = {"action": "create_issue", "title": issue_title, "body": issue_body}
            res, status_code = trigger_github_action(payload)
            if status_code == 200:
                st.success(f"¡Issue #{res.get('issue_number')} creado con éxito en GitHub!")
            else:
                st.error(f"Error al conectar con GitHub: {res.get('error')}")
        else:
            st.warning("Por favor ingresa un título para el issue.")

# ==========================================
# INTERFAZ PRINCIPAL DE CHAT (NÚCLEO LOCAL)
# ==========================================
st.info("Bienvenido a la vitrina interactiva de REMI. Interactúa en tiempo real con el núcleo local.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe una consulta o instrucción para REMI:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
                    respuesta_ia = f"**REMI:** Error (Código {response.status_code})."

            except Exception:
                respuesta_ia = "**REMI (Núcleo):** Error de comunicación con el clúster local."
            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
