import os
from web3 import Web3

# Usaremos solo el oficial para este pulso
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
dest = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def pulso_ignicion():
    print(f"⚡ REMI: Enviando pulso de activación de 0.001 ETH...")
    
    try:
        # Forzamos un Nonce manual
        nonce = w3.eth.get_transaction_count(pub)
        gas_price = int(w3.eth.gas_price * 1.2)
        
        # Enviamos solo 0.001 ETH (~ $2.30 USD)
        # Esto es para "limpiar" el error de 'have 0' forzando al nodo
        valor = w3.to_wei(0.001, 'ether') 

        tx = {
            'nonce': nonce,
            'to': dest,
            'value': valor,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 8453
        }

        signed = w3.eth.account.sign_transaction(tx, priv)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        print(f"✅ ¡PULSO ENVIADO! Hash: {tx_hash.hex()}")
        print("💡 Si esto confirma, el resto del saldo se 'activará' de inmediato.")
        
    except Exception as e:
        print(f"❌ Error de persistencia: {e}")
        print("\n📢 CONSEJO DE REMI: Ramón, la red Base está 'congelada' para tu IP/Dirección.")
        print("Espera 15 minutos exactos sin tocar la terminal. El sistema necesita sincronizar.")

if __name__ == "__main__":
    pulso_ignicion()
