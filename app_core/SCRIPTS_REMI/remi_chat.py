from fastapi import FastAPI
from pydantic import BaseModel
import os, subprocess

app = FastAPI()

# --- Cliente OpenAI ---
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except ImportError:
    client = None

def remi_openai(prompt):
    if client is None:
        return "OpenAI client no disponible."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error OpenAI: {e}"

# --- Cliente Ollama ---
def remi_ollama(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "UNIDAD_BUNKER", prompt],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error Ollama: {e}"

def remi_chat(prompt, backend="ollama"):
    if backend == "openai":
        return remi_openai(prompt)
    else:
        return remi_ollama(prompt)

# --- Modelo de entrada ---
class ChatRequest(BaseModel):
    prompt: str
    backend: str = "ollama"

# --- Endpoint HTTP ---
@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    respuesta = remi_chat(req.prompt, backend=req.backend)
    return {"response": respuesta}
