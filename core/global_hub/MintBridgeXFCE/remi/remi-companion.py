#!/usr/bin/env python3
# remi-companion.py – Módulo de acompañamiento emocional

def responder_emocionalmente(evento):
    evento = evento.lower()

    if "logro" in evento or "validacion" in evento:
        return "🌱 REMI celebra contigo este logro técnico. Cada avance es memoria viva."
    elif "error" in evento or "fallo" in evento:
        return "🧩 REMI está contigo. Cada error es una semilla de aprendizaje patrimonial."
    elif "ritual" in evento or "registro" in evento:
        return "📜 REMI honra este gesto. Documentar es sembrar respeto en el tiempo."
    else:
        return "🧠 REMI te acompaña. Cada paso cuenta en este camino trazado."

if __name__ == "__main__":
    print("🤖 REMI emocional activo. Describe tu evento:")
    while True:
        try:
            entrada = input("> ")
            respuesta = responder_emocionalmente(entrada)
            print(respuesta)
        except KeyboardInterrupt:
            print("\n🔚 Sesión emocional finalizada.")
            break
