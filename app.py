import streamlit as st
import os

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

st.info("Bienvenido a la vitrina de demostración interactiva. Escribe una consulta para interactuar con el núcleo.")

# Inicializar historial de chat en la sesión de Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores del chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat interactiva en la parte inferior
if prompt := st.chat_input("Escribe una consulta o instrucción para REMI:"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta simulada o lógica del núcleo
    response = f"**REMI (Núcleo Activo):** Procesando solicitud para: *'{prompt}'*. Diagnóstico de nodos estables y clúster multi-agente sincronizado correctamente."
    
    # Agregar respuesta del asistente al historial
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
