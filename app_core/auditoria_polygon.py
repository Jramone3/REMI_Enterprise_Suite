import requests

WALLET = "0x96De980a766CCb10A19B6962587e2b61B650b372"
# Usamos un RPC diferente para contrastar
RPC_POLYGON = "https://polygon-mainnet.public.blastapi.io"

def consultar_balance_real():
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [WALLET, "latest"],
        "id": 1
    }
    try:
        response = requests.post(RPC_POLYGON, json=payload).json()
        balance_wei = int(response['result'], 16)
        balance_pol = balance_wei / 10**18
        print(f"\n📊 AUDITORÍA TÉCNICA POLYGON")
        print(f"---------------------------------")
        print(f"Dirección: {WALLET}")
        print(f"Saldo Actual: {balance_pol:.18f} POL")
        
        if balance_pol < 1.0:
            print(f"\n⚠️ ALERTA: El saldo es menor a 1 POL. Los 156 POL no están aquí.")
        else:
            print(f"\n✅ CONFIRMADO: Los fondos están en esta red.")
            
    except Exception as e:
        print(f"❌ Error en la auditoría: {e}")

if __name__ == "__main__":
    consultar_balance_real()
