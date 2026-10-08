import streamlit as st
import os
import requests

st.set_page_config(page_title="REMI Enterprise Suite", page_icon="🤖", layout="wide")

# ==========================================
# 1. VALIDACIÓN PROFUNDA DE GEMINI AL INICIO
# ==========================================
API_KEY = os.getenv("GEMINI_API_KEY")
gemini_ready = False

if not API_KEY:
    st.sidebar.error("⚠️ Advertencia: GEMINI_API_KEY no está configurada en el entorno.")
else:
    try:
        from google import genai
        # Validación de inicialización de cliente
        test_client = genai.Client(api_key=API_KEY)
        st.sidebar.success("✅ Gemini 2.5 Flash conectado y validado")
        gemini_ready = True
    except Exception as e:
        st.sidebar.error(f"❌ Error al validar la API Key de Gemini: {e}")

st.title("🤖 REMI Enterprise Suite - Centro de Comando")
st.sidebar.title("Navegación")
selected_tab = st.sidebar.radio("Ir a:", ["💬 Chat Principal", "🔑 Adquirir Licencia Enterprise"])

# ==========================================
# 2. CHAT PRINCIPAL CON GEMINI
# ==========================================
if selected_tab == "💬 Chat Principal":
    st.header("Centro de Inteligencia - REMI Core")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu orden o consulta técnica..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("REMI ejecutando auditoría y análisis de sistema..."):
                respuesta_ia = ""
                if not gemini_ready:
                    respuesta_ia = "❌ Error: La API Key de Gemini no está activa o configurada correctamente."
                else:
                    try:
                        client = genai.Client(api_key=API_KEY)
                        sys_prompt = "Eres REMI, núcleo de inteligencia artificial de REMI Enterprise Suite, desarrollado por jramonrivasg. Responde con tono técnico, profesional y analítico."
                        user_content = "System: " + sys_prompt + chr(10) + chr(10) + "User: " + prompt
                        res = client.models.generate_content(model="gemini-2.5-flash", contents=user_content)
                        respuesta_ia = res.text
                    except Exception as e:
                        respuesta_ia = "❌ Error en llamada a Gemini 2.5 Flash: " + str(e)
                
                st.markdown(respuesta_ia)
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

# ==========================================
# 3. CONSULTA PROFUNDA AL BÚNKER MONGODB
# ==========================================
elif selected_tab == "🔑 Adquirir Licencia Enterprise":
    st.header("🛡️ Centro de Control - Búnker MongoDB & Licenciamiento")
    st.write("Consulta y verificación profunda contra el microservicio FastAPI (Puerto 8000) y las colecciones del Búnker MongoDB.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        email_input = st.text_input("Correo electrónico registrado en el Búnker:", value="jramonrivasg@gmail.com")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("🔍 Consultar Búnker MongoDB", use_container_width=True)

    if verify_btn or email_input:
        if email_input:
            try:
                with st.spinner("Consultando registros en el Búnker MongoDB (Puerto 8000)..."):
                    response = requests.get(f"http://localhost:8000/licenses/verify/{email_input}", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Licencia autenticada y recuperada del Búnker MongoDB con éxito.")
                    
                    # Métricas clave del búnker
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Estado Búnker", data.get("status", "N/A"))
                    m2.metric("Nivel Enterprise", data.get("tier", "N/A"))
                    m3.metric("Expiración Oficial", data.get("expires", "N/A"))
                    
                    st.info(f"🔑 **Hash de Licencia Activa:** `{data.get('license', 'N/A')}`")
                    
                    with st.expander("📦 Ver Payload Crudo de MongoDB"):
                        st.json(data)
                else:
                    st.error("❌ El correo no arrojó resultados activos en las colecciones del Búnker MongoDB.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Error de conexión: El microservicio FastAPI en el puerto 8000 no responde. Asegúrate de que `license_service.py` esté activo.")
            except Exception as ex:
                st.error(f"❌ Error inesperado al consultar el búnker: {ex}")
        else:
            st.warning("Por favor ingresa un correo electrónico para realizar la consulta.")
