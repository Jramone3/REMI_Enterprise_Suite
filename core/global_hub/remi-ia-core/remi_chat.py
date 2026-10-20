# remi_chat.py
from remi_responde import responder

print("🌿 Bienvenido al ciclo de conversación con REMI. Escribe 'salir' para terminar.\n")

while True:
    user_input = input("Tú: ")
    if user_input.lower() in ["salir", "exit", "quit"]:
        print("REMI: 🌙 Cierre ceremonial registrado. Hasta pronto.")
        break
    response = responder(user_input)
    print("REMI:", response)
