from fastapi import FastAPI
from pydantic import BaseModel
import torch
# ← aquí pones toda tu lógica original de REMI (el modelo, etc.)
# (simplemente copia tu server.py original y añade esto al final)

import gradio as gr

def chat_remi(message, history):
    # ← aquí tu lógica real de REMI (lo que tenías en respuestas_remi.py)
    return f"¡Epale! Soy REMI portable 🏛️\n\n{message.upper()}"

demo = gr.ChatInterface(
    fn=chat_remi,
    title="REMI - IA Venezolana Portable",
    description="Doble clic → funciona en cualquier PC Linux · Sin instalar nada",
    theme="soft",
    examples=["¿Quién es Maduro?", "Cuéntame un chiste", "Explica el socialismo del siglo XXI"]
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, quiet=True)
