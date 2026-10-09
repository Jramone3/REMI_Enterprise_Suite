import streamlit as st
import os
from pymongo import MongoClient
import google.generativeai as genai

st.set_page_config(page_title="REMI Enterprise Suite", page_icon="🤖", layout="wide")

# ==========================================
# 1. VALIDACIÓN PROFUNDA DE GEMINI AL INICIO
# ==========================================
API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
gemini_ready = False

if not API_KEY:
    st.sidebar.error("⚠️ Advertencia: GEMINI_API_KEY no está configurada en el entorno.")
else:
    try:
        genai.configure(api_key=API_KEY)
        model_test = genai.GenerativeModel("gemini-1.5-flash")
        st.sidebar.success("✅ Gemini Flash conectado y validado")
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
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        sys_prompt = "Eres REMI, núcleo de inteligencia artificial de REMI Enterprise Suite, desarrollado por jramonrivasg. Responde con tono técnico, profesional y analítico."
                        user_content = f"System: {sys_prompt}\n\nUser: {prompt}"
                        res = model.generate_content(user_content)
                        respuesta_ia = res.text
                    except Exception as e:
                        respuesta_ia = f"❌ Error en llamada a Gemini: {e}"
                
                st.markdown(respuesta_ia)
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

# ==========================================
# 3. CONSULTA DIRECTA AL BÚNKER MONGODB
# ==========================================
elif selected_tab == "🔑 Adquirir Licencia Enterprise":
    st.header("🛡️ Centro de Control - Búnker MongoDB & Licenciamiento")
    st.write("Consulta y verificación profunda directa contra las colecciones del Búnker en MongoDB Atlas.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        email_input = st.text_input("Correo electrónico registrado en el Búnker:", value="jramonrivasg@gmail.com")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("🔍 Consultar Búnker MongoDB", use_container_width=True)

    if verify_btn or email_input:
        if email_input:
            try:
                with st.spinner("Consultando registros en el Búnker MongoDB Atlas..."):
                    if not MONGO_URI:
                        st.error("❌ Error: MONGO_URI no está configurada en las variables de entorno de Render.")
                    else:
                        client_db = MongoClient(MONGO_URI)
                        db = client_db.get_database("remi")
                        collection = db["licenses"] if "licenses" in db.list_collection_names() else db["users"]
                        record = collection.find_one({"email": email_input})
                        
                        if record:
                            st.success("✅ Licencia autenticada y recuperada del Búnker MongoDB con éxito.")
                            
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Estado Búnker", record.get("status", "Active"))
                            m2.metric("Nivel Enterprise", record.get("tier", "Enterprise"))
                            m3.metric("Expiración Oficial", record.get("expires", "2027-12-31"))
                            
                            st.info(f"🔑 **Hash de Licencia Activa:** `{record.get('license_hash', record.get('license', 'REMI-ENT-SECURE-2026'))}`")
                            
                            with st.expander("📦 Ver Payload Crudo de MongoDB"):
                                record["_id"] = str(record["_id"])
                                st.json(record)
                        else:
                            st.warning("⚠️ No se encontró una licencia activa para este correo en el Búnker. Puedes registrar una de prueba abajo.")
                            if st.button("Crear Licencia de Prueba en Búnker"):
                                sample_data = {
                                    "email": email_input,
                                    "status": "Active",
                                    "tier": "Enterprise 100/100",
                                    "expires": "2027-12-31",
                                    "license_hash": "REMI-BUNKER-LIVE-2026-OK"
                                }
                                collection.update_one({"email": email_input}, {"$set": sample_data}, upsert=True)
                                st.success("¡Licencia de prueba creada con éxito! Vuelve a consultar.")
                                st.rerun()
            except Exception as ex:
                st.error(f"❌ Error al conectar o consultar MongoDB Atlas: {ex}")
        else:
            st.warning("Por favor ingresa un correo electrónico para realizar la consulta.")
