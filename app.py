# app.py - Frontend unificado de Streamlit para REMI Enterprise Suite
import os
import requests
import streamlit as st

# Validación segura de assets para evitar errores de renderizado
logo_path = "assets/remi_logo.png"
favicon_arg = logo_path if os.path.exists(logo_path) else None

st.set_page_config(
    page_title="REMI Enterprise Suite - Portal y Clúster",
    page_icon=favicon_arg,
    layout="centered",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Imagen oficial de REMI condicional y título principal
img_path = "assets/remi_imagen_oficial.jpeg"
if os.path.exists(img_path):
    st.image(img_path, width=200)
else:
    st.markdown("### 🛡️ REMI Enterprise Core")

st.title("💎 REMI Enterprise Suite")
st.markdown("### Framework Multi-Agente y Núcleo de Inteligencia Artificial")
st.markdown("---")

# ==========================================
# BARRA LATERAL: PASARELA Y LICENCIAMIENTO
# ==========================================
with st.sidebar:
    if os.path.exists(img_path):
        st.image(img_path, width=100)

    st.subheader("Portal Enterprise")
    st.caption("Infraestructura conectada al microservicio de licencias seguro.")

    # Verificación de Estado del Backend en tiempo real
    try:
        health_resp = requests.get(f"{API_BASE_URL}/docs", timeout=2)
        if health_resp.status_code == 200:
            st.success("🟢 Backend API: Conectado")
        else:
            st.warning("🟡 Backend API: Respuesta inusual")
    except Exception:
        st.error("🔴 Backend API: Desconectado (Ejecuta FastAPI)")

    st.markdown("---")
    st.markdown("### 🐙 Automatización GitHub")
    issue_title = st.text_input("Título del Issue:")
    issue_body = st.text_area("Descripción del Issue:")
    if st.button("Crear Issue en GitHub"):
        if issue_title:
            token = os.getenv("GITHUB_BOT_TOKEN")
            if not token:
                st.warning("⚠️ GITHUB_BOT_TOKEN no detectado en el entorno local del servidor frontend.")
            else:
                try:
                    from github import Github
                    g = Github(token)
                    repo = g.get_repo("Jramone3/REMI_Enterprise_Suite")
                    issue = repo.create_issue(title=issue_title, body=issue_body or "Generado por REMI Core OS")
                    st.success(f"¡Issue #{issue.number} creado con éxito en GitHub!")
                except Exception as e:
                    st.error(f"Error al conectar con GitHub: {e}")
        else:
            st.warning("Por favor ingresa un título para el issue.")

    st.markdown("---")
    st.markdown("### 🔄 Verificación de Licencia")
    check_email = st.text_input("Correo registrado:", key="check_email_input")
    
    if st.button("Comprobar Estado"):
        if check_email:
            try:
                resp = requests.get(f"{API_BASE_URL}/licenses/verify/{check_email}", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"✅ Licencia activa. Estado: **{data.get('status')}** | Tier: **{data.get('tier')}**")
                elif resp.status_code == 404:
                    st.error("❌ No se encontró ninguna licencia activa para este correo.")
                else:
                    st.error(f"Error del servidor: {resp.json().get('detail', 'Desconocido')}")
            except Exception as e:
                st.error(f"Error de conexión con el servicio: {e}")
        else:
            st.warning("Introduce un correo electrónico registrado.")

    st.markdown("---")
    st.markdown("### 🐙 Automatización GitHub")
    issue_title = st.text_input("Título del Issue:")
    issue_body = st.text_area("Descripción del Issue:")
    if st.button("Crear Issue en GitHub"):
        if issue_title:
            token = os.getenv("GITHUB_BOT_TOKEN")
            if not token:
                st.error("Token del bot no configurado (GITHUB_BOT_TOKEN)")
            else:
                try:
                    from github import Github
                    g = Github(token)
                    repo = g.get_repo("Jramone3/REMI_Enterprise_Suite")
                    issue = repo.create_issue(title=issue_title, body=issue_body or "Generado por REMI Core OS")
                    st.success(f"¡Issue #{issue.number} creado con éxito en GitHub!")
                except Exception as e:
                    st.error(f"Error al conectar con GitHub: {e}")
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

                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    respuesta_ia = response.json()["message"]["content"]
                else:
                    respuesta_ia = f"**REMI:** Error de modelo local (Código {response.status_code})."

            except Exception:
                respuesta_ia = "**REMI (Núcleo):** Error de comunicación con el clúster local (Ollama)."
            
            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
