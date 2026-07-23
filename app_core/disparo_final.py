import os
from web3 import Web3

# Cambiamos a LlamaNodes que es el que nos detectó saldo antes
w3 = Web3(Web3.HTTPProvider('https://base.llamarpc.com'))

priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
dest = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def ejecucion_final_segura():
    print(f"📡 REMI: Conectando a LlamaNodes (Bypass Mode)...")
    try:
        # Forzamos lectura de balance en cada intento
        balance = w3.eth.get_balance(pub)
        print(f"💰 Saldo en el nodo: {w3.from_wei(balance, 'ether')} ETH")
        
        # Mandamos una cantidad menor para asegurar que el nodo lo acepte
        # 0.0035 es un valor MUY seguro considerando que tienes 0.0047
        valor_envio = w3.to_wei(0.0035, 'ether')
        
        # Gas estándar pero con prioridad
        gas_price = int(w3.eth.gas_price * 1.2)
        nonce = w3.eth.get_transaction_count(pub)

        tx = {
            'nonce': nonce,
            'to': dest,
            'value': valor_envio,
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 8453
        }

        print(f"🚀 Intentando salto con {w3.from_wei(valor_envio, 'ether')} ETH...")
        signed = w3.eth.account.sign_transaction(tx, priv)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        print(f"✅ ¡ÉXITO! Hash: {tx_hash.hex()}")
        print(f"🔗 Revisa: https://basescan.org/tx/{tx_hash.hex()}")

    except Exception as e:
        print(f"❌ El nodo sigue bloqueado: {e}")

if __name__ == "__main__":
    ejecucion_final_segura()
