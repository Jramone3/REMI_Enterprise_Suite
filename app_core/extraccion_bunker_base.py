import time
from web3 import Web3

# 1. CONEXIÓN A BASE (Donde están tus 11 USD)
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# 2. CREDENCIALES RECUPERADAS
fantasma_priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
fantasma_pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'

# EL DESTINO (Tu Nodo A)
nodo_a = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def mover_fondos():
    balance = w3.eth.get_balance(fantasma_pub)
    eth_val = w3.from_wei(balance, 'ether')
    print(f"📡 Detectados {eth_val} ETH en Búnker Base.")

    if balance > 0:
        gas_price = w3.eth.gas_price
        # Dejamos un poco de margen para el gas
        value_to_send = balance - (gas_price * 21000)
        
        tx = {
            'nonce': w3.eth.get_transaction_count(fantasma_pub),
            'to': nodo_a,
            'value': value_to_send,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 8453 # Red Base
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, fantasma_priv)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"✅ Fondos en movimiento hacia Nodo A (Base). Hash: {tx_hash.hex()}")
    else:
        print("❌ La cuenta está vacía o el gas aún no llega.")

if __name__ == "__main__":
    mover_fondos()
