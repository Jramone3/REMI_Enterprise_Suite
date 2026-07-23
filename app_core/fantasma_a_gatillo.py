import time
from web3 import Web3

# Conexión
w3 = Web3(Web3.HTTPProvider('https://1rpc.io/matic'))

# DATOS CRÍTICOS
fantasma_priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
fantasma_pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
gatillo_a = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def enviar_gas():
    # Este script lo usaremos para mandar el POL al Gatillo A una vez lo tengas
    balance = w3.eth.get_balance(fantasma_pub)
    print(f"Saldo en Fantasma: {w3.from_wei(balance, 'ether')} POL")
    
    if balance > 0:
        gas_price = w3.eth.gas_price
        tx = {
            'nonce': w3.eth.get_transaction_count(fantasma_pub),
            'to': gatillo_a,
            'value': balance - (gas_price * 21000), # Todo menos la comisión
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 137
        }
        signed_tx = w3.eth.account.sign_transaction(tx, fantasma_priv)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Munición enviada al Gatillo A: {tx_hash.hex()}")

if __name__ == "__main__":
    enviar_gas()
