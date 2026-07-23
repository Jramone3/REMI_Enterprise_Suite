import os
from web3 import Web3

# 1. CONFIGURACIÓN
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
fantasma_priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
fantasma_pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
nodo_a_dest = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def ejecucion_y_quema():
    balance = w3.eth.get_balance(fantasma_pub)
    if balance <= 0:
        print("❌ Búnker vacío o saldo insuficiente.")
        return

    print(f"🚀 Iniciando salto: {w3.from_wei(balance, 'ether')} ETH -> Nodo A")
    
    gas_price = int(w3.eth.gas_price * 1.2)
    tx = {
        'nonce': w3.eth.get_transaction_count(fantasma_pub),
        'to': nodo_a_dest,
        'value': balance - (gas_price * 21000),
        'gas': 21000,
        'gasPrice': gas_price,
        'chainId': 8453
    }

    try:
        signed = w3.eth.account.sign_transaction(tx, fantasma_priv)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ MUNICIÓN ENVIADA AL NODO A. Hash: {tx_hash.hex()}")
        
        print("🧹 Ejecutando protocolo de limpieza...")
        os.remove(__file__)
        print("💀 Script auto-destruido. Rastro eliminado.")
    except Exception as e:
        print(f"⚠️ Error en la fase de ignición: {e}")

if __name__ == "__main__":
    ejecucion_y_quema()
