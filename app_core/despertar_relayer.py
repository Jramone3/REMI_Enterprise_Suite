import requests
import json

# Datos de tu transaccion atrapada
tx_hash_base = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
wallet = '0x96De980a766CCb10A19B6962587e2b61B650b372'

print(f"📡 REMI: Enviando señal de despertar al servidor de Orbiter...")

# Intentamos comunicarnos con el indexador de Orbiter
url = "https://openapi.orbiter.finance/explore/v1/mainnet/tx-speed-up"
payload = {
    "sourceHash": tx_hash_base,
    "userAddress": wallet
}

try:
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code == 200:
        print("✅ ¡SEÑAL ENVIADA! El servidor respondió. Revisa el radar en unos minutos.")
        print(f"Respuesta: {response.text}")
    else:
        print(f"⚠️ El servidor respondió con código {response.status_code}. Quizás la API cambió.")
        # Intento alternativo (Consulta de estado para forzar indexación)
        print("📡 Intentando forzar re-indexación vía consulta de historial...")
        hist_url = f"https://openapi.orbiter.finance/view/v2/history?user={wallet}"
        r_hist = requests.get(hist_url)
        print(f"🔎 Estado en historial: {r_hist.status_code}")
except Exception as e:
    print(f"❌ No se pudo conectar con el servidor: {e}")
