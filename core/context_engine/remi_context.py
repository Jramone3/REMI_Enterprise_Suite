import datetime
import pytz

def get_remi_environmental_context():
    """
    Genera el contexto ambiental en tiempo real (Tiempo, Zona, Ubicación y Modo) 
    para inyectarlo soberanamente en los prompts del sistema de REMI.
    """
    try:
        tz = pytz.timezone('America/Caracas')
        now = datetime.datetime.now(tz)
    except Exception:
        now = datetime.datetime.now()
        
    context_block = (
        f"[REMI_CORE Environmental & Spatial Matrix]\n"
        f"- Current Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"- Local Time: {now.strftime('%H:%M:%S %z')}\n"
        f"- Geographic Location: Aragua, Venezuela (Desktop Bunker / Local Node)\n"
        f"- Operational Status: Active Defense, Audit & Autonomous Execution Mode\n"
        f"- Core Directive: Provide precise, context-aware, real-time responses.\n"
    )
    return context_block

if __name__ == "__main__":
    print(get_remi_environmental_context())
