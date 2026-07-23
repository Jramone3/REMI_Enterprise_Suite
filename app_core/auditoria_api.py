import requests
import time

nodos = {
    "Wallet_PC": "0x96De980a766CCb10A19B6962587e2b61B650b372",
    "Nodo_A_Gatillo": "0xB9073c07648a414B875874d7B8599dD2fAa171E8",
    "Nodo_B_Puente": "0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291",
    "Nodo_Fantasma": "0xe4EdB277328A32976F5E4aC18A494f1890d2979E",
    "Contrato_Request": "0x5E0f8E73884b3E124884b3E124884b3E124884b3"
}

print("\n🛰️ REMI: CONSULTA DIRECTA VIA API POLYGONSCAN")
print("-" * 50)

for nombre, addr in nodos.items():
    # Usamos el endpoint público de balance
    url = f"https://api.polygonscan.com/api?module=account&action=balance&address={addr}&tag=latest"
    try:
        response = requests.get(url).json()
        if response["status"] == "1":
            balance_wei = int(response["result"])
            balance_pol = balance_wei / 10**18
            print(f"📍 {nombre:18} | {balance_pol:.6f} POL")
        else:
            print(f"❌ {nombre:18} | Error en API")
        time.sleep(0.2) # Respetamos el límite de la API gratuita
    except Exception as e:
        print(f"❌ {nombre:18} | Fallo de conexión")

print("-" * 50)
