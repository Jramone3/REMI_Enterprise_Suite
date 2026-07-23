import requests

# Tu wallet principal
WALLET = "0x96De980a766CCb10A19B6962587e2b61B650b372"
# Cambiamos a un RPC más potente (Ankr)
RPC_POLYGON = "https://rpc.ankr.com/polygon"

def auditar():
    print(f"🛰️ REMI: Iniciando escaneo profundo en Polygon...")
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [WALLET, "latest"],
        "id": 1
    }
    
    try:
        r = requests.post(RPC_POLYGON, json=payload, timeout=15)
        data = r.json()
        
        if "result" in data:
            balance_wei = int(data['result'], 16)
            balance_pol = balance_wei / 10**18
            print(f"\n💎 RESULTADO PARA {WALLET}")
            print(f"💰 SALDO REAL: {balance_pol:.6f} POL")
            
            if balance_pol > 150:
                print("\n🔥 ¡LOS 156 POL SIGUEN AHÍ! El explorador web está desfasado.")
            else:
                print("\n📉 Saldo bajo. El reporte de ayer de 156 POL fue un error de lectura del nodo anterior.")
        else:
            print(f"⚠️ El nodo respondió pero sin saldo: {data}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    auditar()
