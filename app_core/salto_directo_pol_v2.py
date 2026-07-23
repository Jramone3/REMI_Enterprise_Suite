import os
from web3 import Web3

# Probamos con un nodo alternativo más rápido
w3 = Web3(Web3.HTTPProvider('https://base.meowrpc.com'))

fantasma_priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
fantasma_pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
nodo_a_dest = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def ejecucion_final():
    if not w3.is_connected():
        print("❌ Error de conexión al nodo.")
        return

    bal = w3.eth.get_balance(fantasma_pub)
    print(f"📡 Saldo detectado: {w3.from_wei(bal, 'ether')} ETH")
    
    if bal <= 0:
        print("❌ El nodo sigue reportando 0. Esperando sincronización...")
        return

    # Dejamos un margen mayor para asegurar la aceptación
    gas_price = w3.eth.gas_price
    gas_limit = 21000
    total_gas = gas_price * gas_limit
    
    # Enviamos un poco menos para que no haya error de cálculo
    envio = int(bal * 0.90) 

    tx = {
        'nonce': w3.eth.get_transaction_count(fantasma_pub),
        'to': nodo_a_dest,
        'value': envio,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': 8453
    }

    try:
        signed = w3.eth.account.sign_transaction(tx, fantasma_priv)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ MUNICIÓN ENVIADA. Hash: {tx_hash.hex()}")
        os.remove(__file__)
        print("💀 Limpieza ejecutada.")
    except Exception as e:
        print(f"⚠️ Fallo: {e}")

if __name__ == "__main__":
    ejecucion_final()
