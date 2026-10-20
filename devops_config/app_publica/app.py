import streamlit as st
import os

st.set_page_config(
    page_title="REMI Enterprise Suite - Demo",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 REMI Enterprise Suite")
st.markdown("### Framework Multi-Agente y Núcleo de Inteligencia Artificial")
st.markdown("---")

st.info("Bienvenido a la vitrina de demostración interactiva. Esta versión muestra las capacidades lógicas del núcleo de REMI.")

# Campo de interacción de ejemplo para la demo
user_input = st.text_input("Escribe una consulta o instrucción para REMI:")

if st.button("Enviar a REMI"):
    if user_input:
        # Respuesta simulada o conexión al motor de agentes del app_core
        st.success(f"**REMI (Núcleo Activo):** Procesando solicitud comercial para: *'{user_input}'*")
        st.write("Para acceder a la versión completa, pasarelas de despliegue en servidor propio y módulos avanzados, adquiere tu licencia Enterprise.")
    else:
        st.warning("Por favor, ingresa una consulta.")

st.markdown("---")
st.markdown("*REMI Enterprise Suite © 2026 - Desarrollado por jramonrivasg*")
