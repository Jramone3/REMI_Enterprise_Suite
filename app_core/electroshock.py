from web3 import Web3
import os

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'

def enviar_pulso():
    print("⚡ Iniciando pulso de limpieza de caché...")
    try:
        nonce = w3.eth.get_transaction_count(pub)
        gas_price = int(w3.eth.gas_price * 1.1)
        
        # Transacción de 0 ETH a ti mismo
        tx = {
            'nonce': nonce,
            'to': pub, 
            'value': 0,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 8453
        }
        
        signed = w3.eth.account.sign_transaction(tx, priv)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Pulso enviado con éxito. Hash: {tx_hash.hex()}")
        print("💡 Ahora el nodo DEBE reconocer tu saldo real.")
    except Exception as e:
        print(f"❌ El nodo sigue en coma: {e}")

if __name__ == "__main__":
    enviar_pulso()
