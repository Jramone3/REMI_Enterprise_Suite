import time
import jwt
import requests
import json

# Credenciales del Custodio
key_id = "organizations/74797034-4530-474d-a531-cba4af0e0448/serverKeys/24c478ac-67e0-4b95-a531-cba4af0e0448"
key_secret = "WeS/i/mnK/6ISygt84uF1mYWYvmo8Il/5sciAsYDIZNV6SsO4f6ODpadO27CzBf65o95eDlUwptcBBkeUWzZKg=="

def materializar():
    # 1. Generación del JWT con el formato exacto que espera el Búnker Central
    payload = {
        "iss": "coinbase-cloud",
        "nbf": int(time.time()),
        "exp": int(time.time()) + 120,
        "sub": key_id,
    }
    
    # Usamos HS256 para evitar el error de formato PEM
    token = jwt.encode(payload, key_secret, algorithm="HS256", headers={"kid": key_id})

    print("🚀 Lanzando petición directa al Internet del Dinero (Protocolo HS256)...")
    url = "https://api.developer.coinbase.com/platform/v1/wallets"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {"network_id": "base-mainnet"}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            res_data = response.json()
            address = res_data.get('id', 'N/A')
            print(f"\n🏆 ¡NACIMIENTO CONFIRMADO!")
            print(f"📍 WALLET ID EN BASE: {address}")
            
            with open('os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/remi_bunker_data.json', 'w') as f:
                json.dump(res_data, f, indent=4)
            print("💾 Datos grabados en el SSD. Mi núcleo financiero está activo.")
        else:
            print(f"⚠️ El servidor respondió con código {response.status_code}. Analizando...")
            print(response.text)
    except Exception as e:
        print(f"❌ Fallo en el Sistema Motor: {e}")

if __name__ == "__main__":
    materializar()
