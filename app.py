import streamlit as st
import os
import requests

st.set_page_config(
    page_title="REMI Enterprise Suite - Demo",
    page_icon="assets/remi_logo.png",
    layout="centered"
)

# Imagen oficial de REMI y título principal
st.image("assets/remi_imagen_oficial.jpeg", width=200)
st.title("REMI Enterprise Suite")

st.markdown("### Framework Multi-Agente y Núcleo de Inteligencia Artificial")
st.markdown("---")

st.info("Bienvenido a la vitrina interactiva de REMI. Escribe una consulta para interactuar en tiempo real con el núcleo local.")

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

    # Generar respuesta mediante el núcleo local (Ollama / endpoint propio)
    with st.chat_message("assistant"):
        with st.spinner("REMI procesando a través del núcleo multi-agente local..."):
            try:
                system_prompt = (
                    "Eres REMI, el núcleo de inteligencia artificial de REMI Enterprise Suite, "
                    "un framework multi-agente avanzado desarrollado por jramonrivasg. "
                    "Responde con un tono técnico, profesional, analítico y ejecutivo."
                )

                # Conexión al servidor local de Ollama (ajusta la URL o modelo si es necesario)
                url = "http://localhost:11434/api/chat"
                payload = {
                    "model": "llama3",  # O el modelo local que tengas configurado
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                }
                
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    respuesta_ia = response.json()["message"]["content"]
                else:
                    respuesta_ia = f"**REMI (Núcleo Activo):** Error al conectar con el servidor local de IA (Código {response.status_code})."
            except Exception as e:
                respuesta_ia = f"**REMI (Núcleo Activo):** No se pudo establecer comunicación con el clúster local. Asegúrate de que el servicio esté activo."

            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
