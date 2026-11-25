import os
from datetime import datetime

def _registrar_pregunta(pregunta: str) -> None:
    ruta = os.path.join(os.getcwd(), "docs", "patrimonial")
    os.makedirs(ruta, exist_ok=True)
    # Registro seguro de auditoría de consultas
    log_path = os.path.join(ruta, "consultas_audit.log")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()] {pregunta}\n")
    except Exception:
        pass

def responder(pregunta: str) -> str:
    if not pregunta:
        return "Por favor, escribe una pregunta válida."
        
    pregunta_lower = pregunta.lower().strip()
    _registrar_pregunta(pregunta_lower)

    # Mapa limpio de patrones y respuestas para evitar bucles de recursión en linter
    respuestas_map = {
        ("que eres", "quien eres"): "Soy REMI, un asistente de inteligencia artificial soberano y multi-pilar integrado en tu entorno enterprise.",
        ("donde estas", "ubicacion"): "Estoy presente operando de forma local y soberana dentro de tu infraestructura Linux.",
        ("estado", "sistema"): "Los sistemas de la suite operan bajo control de estabilidad y flujos seguros de CI/CD.",
    }

    for claves, respuesta in respuestas_map.items():
        if any(clave in pregunta_lower for clave in claves):
            return respuesta

    return f"Consulta procesada por REMI para: '{pregunta}'."
