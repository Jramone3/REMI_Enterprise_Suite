k# app.py - Frontend Streamlit definitivo para REMI Enterprise Suite
import os
import requests
import streamlit as st

# Configuración de página
logo_path = "assets/remi_logo.png"
favicon_arg = logo_path if os.path.exists(logo_path) else None

st.set_page_config(
    page_title="REMI Enterprise Suite - Portal y Clúster",
    page_icon=favicon_arg,
    layout="centered",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Imagen oficial de REMI
img_path = "assets/remi_imagen_oficial.jpeg"
if os.path.exists(img_path):
    st.image(img_path, width=200)
else:
    st.markdown("### 🛡️ REMI Enterprise Core")

st.title("💎 REMI Enterprise Suite")
st.markdown("### Framework Multi-Agente y Núcleo de Inteligencia Artificial")
st.markdown("---")

# ==========================================
# BARRA LATERAL: PASARELA Y MICROSERVICIO
# ==========================================
with st.sidebar:
    if os.path.exists(img_path):
        st.image(img_path, width=100)

    st.subheader("Portal Enterprise")
    st.caption("Infraestructura conectada al microservicio FastAPI.")

    # Verificación de Estado del Backend en tiempo real
    try:
        health_resp = requests.get(f"{API_BASE_URL}/", timeout=2)
        if health_resp.status_code == 200:
            st.success("🟢 Backend API: Conectado")
        else:
            st.warning("🟡 Backend API: Respuesta inusual")
    except Exception:
        st.error("🔴 Backend API: Desconectado")

    st.markdown("---")
    st.markdown("### 💎 Adquirir Licencia Anual")
    st.markdown("**Costo:** $499 USD / Año")
    st.markdown("Incluye soporte técnico y clúster multi-agente avanzado.")

    if st.button("Generar Datos de Pago"):
        st.session_state.mostrar_pago = True

    if st.session_state.get("mostrar_pago", False):
        st.info(
            "**Instrucciones de Pago Directo:**\n\n"
            "1. Envía **499 USDT (ERC-20 / Base)** a:\n"
            f"`{os.getenv('REMI_PAYMENT_ADDRESS', '0x96De980a766CCb10A19B6962587e2b61B650b372')}`\n\n"
            "2. Registra tus datos y el **TxID** de la transferencia."
        )

        cliente_email = st.text_input("Correo electrónico de registro:", key="reg_email")
        tx_input = st.text_input("Hash de la Transacción (TxID):", key="reg_tx")
        tier_choice = st.selectbox("Nivel de Licencia", ["standard", "enterprise"], key="reg_tier")
        admin_key_input = st.text_input("API Key de Activación (Admin)", type="password", key="reg_adm_key")

        # Emisión de Licencia conectada al Microservicio FastAPI mediante POST con X-API-Key
        if st.button("Registrar y Activar Licencia (Microservicio)"):
            if cliente_email and tx_input and admin_key_input:
                headers = {"X-API-Key": admin_key_input, "Content-Type": "application/json"}
                payload = {"email": cliente_email, "tx_hash": tx_input, "tier": tier_choice}
                try:
                    resp = requests.post(f"{API_BASE_URL}/licenses/issue", json=payload, headers=headers, timeout=5)
                    if resp.status_code == 200:
                        data_resp = resp.json()
                        st.success("¡Licencia emitida y registrada con éxito en el búnker!")
                        st.markdown(f"**Clave de Licencia:** `{data_resp.get('license')}`")
                        st.markdown(f"**Expira:** {data_resp.get('expires')}")
                    else:
                        error_detail = resp.json().get("detail", "Error desconocido en el servidor")
                        st.error(f"Fallo al emitir: {error_detail}")
                except Exception as e:
                    st.error(f"Error de conexión con el backend: {e}")
            else:
                st.warning("Completa todos los campos, incluyendo la API Key de administrador.")

    st.markdown("---")
    st.markdown("### 🔄 Verificación de Licencia")
    check_email = st.text_input("Correo registrado:", key="check_email_input")
    
    if st.button("Comprobar Estado"):
        if check_email:
            try:
                resp = requests.get(f"{API_BASE_URL}/licenses/verify/{check_email}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"✅ Activa. Tier: **{data.get('tier')}** | Expira: **{data.get('expires')}**")
                elif resp.status_code == 404:
                    st.error("❌ No se encontró ninguna licencia activa.")
                else:
                    st.error("Error al consultar el servicio.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
        else:
            st.warning("Introduce un correo electrónico.")

    st.markdown("---")
    st.markdown("### 🐙 Automatización GitHub (Opcional)")
    issue_title = st.text_input("Título del Issue:")
    issue_body = st.text_area("Descripción del Issue:")
    if st.button("Crear Issue en GitHub"):
        if issue_title:
            token = os.getenv("GITHUB_BOT_TOKEN")
            if not token:
                st.info("ℹ️ Entorno sin GITHUB_BOT_TOKEN activo en frontend.")
            else:
                try:
                    from github import Github
                    g = Github(token)
                    repo = g.get_repo("Jramone3/REMI_Enterprise_Suite")
                    issue = repo.create_issue(title=issue_title, body=issue_body or "Generado por REMI Core OS")
                    st.success(f"¡Issue #{issue.number} creado con éxito!")
                except Exception as e:
                    st.error(f"Error con GitHub: {e}")
        else:
            st.warning("Ingresa un título para el issue.")

# ==========================================
# INTERFAZ PRINCIPAL DE CHAT (Llama3 Local)
# ==========================================
st.info("Bienvenido a la vitrina interactiva de REMI. Chatea en tiempo real con el núcleo local.")

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

                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    respuesta_ia = response.json()["message"]["content"]
                else:
                    respuesta_ia = f"**REMI:** Error de modelo local (Código {response.status_code})."
            except Exception:
                respuesta_ia = "**REMI (Núcleo):** Error de comunicación con Ollama."
            
            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
