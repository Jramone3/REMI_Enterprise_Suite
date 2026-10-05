# app.py - Portal de Demostración y Cliente de REMI Enterprise Suite (Edición Comercial Unificada)
import streamlit as st
import requests
import os
import json

# Configuración de la página
logo_path = "assets/remi_logo.png"
favicon_arg = logo_path if os.path.exists(logo_path) else "🛡️"

st.set_page_config(
    page_title="REMI Enterprise Suite | Sovereign AI",
    page_icon=favicon_arg,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para un look corporativo moderno (Modo Búnker / Tech Dark)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stButton>button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2ea043 0%, #3fb950 100%);
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Variables de entorno y URLs de microservicio
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
LICENSE_API_URL = os.getenv("LICENSE_API_URL", API_BASE_URL)
img_path = "assets/remi_imagen_oficial.jpeg"

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists(img_path):
        st.image(img_path, width=120)
    elif os.path.exists("assets/remi_logo.png"):
        st.image("assets/remi_logo.png", width=120)
    else:
        st.title("🛡️ REMI Enterprise")
        
    st.markdown("### **Soberanía y Automatización**")
    st.markdown("Plataforma multi-agente con licenciamiento on-chain y fiduciario.")
    
    # Verificación de Estado del Backend en tiempo real
    try:
        health_resp = requests.get(f"{API_BASE_URL}/", timeout=2)
        if health_resp.status_code == 200:
            st.success("🟢 Backend API: Conectado")
        else:
            st.warning("🟡 Backend API: Respuesta inusual")
    except Exception:
        st.error("🔴 Backend API: Desconectado")
    
    st.divider()
    
    selected_tab = st.radio(
        "Navegación del Portal",
        ["💬 Centro de Comando (Chat)", "🔑 Adquirir Licencia Enterprise", "🔍 Verificar Estado de Licencia", "🐙 Automatización GitHub"]
    )
    
    st.divider()
    st.markdown("**Entorno:** `ramon-desktop` (sda5)")
    st.markdown("**Versión:** 2.2.0 Enterprise")

# --- PESTAÑA 1: CENTRO DE COMANDO (CHAT) ---
if selected_tab == "💬 Centro de Comando (Chat)":
    st.title("💬 REMI AI - Centro de Comando Operativo")
    st.markdown("Interactúa en tiempo real con el núcleo de inteligencia soberano de REMI (Llama3 Local).")

    # Inicializar historial de chat en Streamlit session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Saludos, Custodio. REMI en línea desde el búnker local de sda5. ¿Qué directiva ejecutamos hoy?"}
        ]

    # Mostrar mensajes anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de usuario
    if prompt := st.chat_input("Escribe tu instrucción o comando para REMI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("REMI procesando a través del núcleo local (Ollama)..."):
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
                    response = requests.post(url, json=payload, timeout=30)
                    if response.status_code == 200:
                        respuesta_ia = response.json()["message"]["content"]
                    else:
                        respuesta_ia = f"⚠️ Error de modelo local (Código {response.status_code})."
                except Exception:
                    respuesta_ia = "❌ Error crítico: No se pudo conectar con el servicio Ollama local."
                
                st.markdown(respuesta_ia)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

# --- PESTAÑA 2: ADQUIRIR LICENCIA ENTERPRISE ---
elif selected_tab == "🔑 Adquirir Licencia Enterprise":
    st.title("🔑 Portal de Adquisición de Licencias Enterprise")
    st.markdown("Obtén acceso completo a la suite empresarial mediante criptoactivo verificado on-chain o pasarela fiduciaria segura.")

    tab_crypto, tab_fiat = st.tabs(["💎 Pago Cripto (USDT/USDC en Base)", "💳 Pago Tarjeta / Fiduciario (Stripe)"])

    with tab_crypto:
        st.subheader("Emisión Instantánea por Validación On-Chain")
        st.markdown(f"Envía **499 USDT (ERC-20 / Base)** a la dirección corporativa autorizada:\n`{os.getenv('REMI_PAYMENT_ADDRESS', '0x96De980a766CCb10A19B6962587e2b61B650b372')}`")
        
        with st.form("crypto_license_form"):
            c_email = st.text_input("Correo Electrónico Corporativo")
            c_tx = st.text_input("Hash de la Transacción (TxID en Red Base)")
            c_tier = st.selectbox("Nivel de Licencia", ["standard", "enterprise"])
            admin_key_input = st.text_input("API Key de Activación (Admin)", type="password")
            
            submit_crypto = st.form_submit_button("Validar Pago y Activar Licencia")
            
            if submit_crypto:
                if not c_email or not c_tx or not admin_key_input:
                    st.error("Por favor, completa todos los campos requeridos, incluyendo la API Key de administrador.")
                else:
                    with st.spinner("Validando transacción on-chain en red Base y registrando licencia..."):
                        try:
                            payload = {
                                "email": c_email,
                                "tx_hash": c_tx,
                                "tier": c_tier
                            }
                            headers = {"X-API-Key": admin_key_input, "Content-Type": "application/json"}
                            res = requests.post(f"{LICENSE_API_URL}/licenses/issue", json=payload, headers=headers, timeout=15)
                            
                            if res.status_code == 200:
                                data = res.json()
                                st.success("¡Licencia emitida y registrada con éxito en el búnker!")
                                st.markdown(f"**Clave de Licencia:** `{data.get('license')}`")
                                st.info(f"Válida hasta: {data.get('expires')}")
                            else:
                                st.error(f"Fallo en la emisión: {res.json().get('detail', 'Error desconocido')}")
                        except Exception as ex:
                            st.error(f"Error de conexión con el microservicio de licencias: {str(ex)}")

    with tab_fiat:
        st.subheader("Pago Corporativo Internacional con Tarjeta")
        st.markdown("Procesa tu pago de forma segura a través de nuestra pasarela integrada con Stripe.")
        st.info("💡 Al completar el pago en la pasarela de Stripe, el sistema de webhooks emitirá tu clave corporativa automáticamente.")
        
        stripe_checkout_url = st.text_input("URL de Checkout de Stripe", "https://buy.stripe.com/test_placeholder")
        if st.button("Ir a Pasarela de Pago Segura"):
            st.markdown(f"Haz clic en el siguiente enlace para proceder al pago: [Abrir Pasarela de Stripe]({stripe_checkout_url})")

# --- PESTAÑA 3: VERIFICAR ESTADO DE LICENCIA ---
elif selected_tab == "🔍 Verificar Estado de Licencia":
    st.title("🔍 Verificador de Licencias Activas")
    st.markdown("Consulta el estado y vigencia de cualquier licencia corporativa registrada en el búnker de MongoDB.")

    verify_email = st.text_input("Introduce el correo electrónico corporativo asociado:")
    if st.button("Consultar Estado"):
        if not verify_email:
            st.warning("Introduce un correo válido.")
        else:
            with st.spinner("Consultando base de datos segura..."):
                try:
                    res = requests.get(f"{LICENSE_API_URL}/licenses/verify/{verify_email}", timeout=10)
                    if res.status_code == 200:
                        data = res.json()
                        st.success("¡Licencia encontrada y activa!")
                        st.markdown(f"✅ Tier: **{data.get('tier')}** | Expira: **{data.get('expires')}**")
                        st.json(data)
                    elif res.status_code == 404:
                        st.error("❌ No se encontró ninguna licencia activa para este correo.")
                    else:
                        st.error("Error al consultar el servicio backend.")
                except Exception as e:
                    st.error(f"Error de conexión con el servidor: {str(e)}")

# --- PESTAÑA 4: AUTOMATIZACIÓN GITHUB ---
elif selected_tab == "🐙 Automatización GitHub":
    st.title("🐙 Automatización de Tareas (GitHub Integration)")
    st.markdown("Crea issues técnicos directamente en el repositorio remoto del proyecto.")

    issue_title = st.text_input("Título del Issue:")
    issue_body = st.text_area("Descripción detallada:")
    
    if st.button("Crear Issue en GitHub"):
        if issue_title:
            token = os.getenv("GITHUB_BOT_TOKEN")
            if not token:
                st.warning("⚠️ Entorno sin `GITHUB_BOT_TOKEN` activo en el contenedor o sesión actual.")
            else:
                try:
                    from github import Github
                    g = Github(token)
                    repo = g.get_repo("Jramone3/REMI_Enterprise_Suite")
                    issue = repo.create_issue(title=issue_title, body=issue_body or "Generado por REMI Core OS")
                    st.success(f"¡Issue #{issue.number} creado con éxito en GitHub!")
                except Exception as e:
                    st.error(f"Error al conectar con la API de GitHub: {e}")
        else:
            st.warning("Ingresa un título para el issue.")

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
