import os
import time
from web3 import Web3

# Probamos con LlamaNodes o Base.org directamente
RPC_URL = 'https://base.llamarpc.com'
w3 = Web3(Web3.HTTPProvider(RPC_URL))

fantasma_priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
fantasma_pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
nodo_a = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def barrido_final():
    print(f"🕵️‍♂️ REMI: Conectando a {RPC_URL}...")
    
    for intento in range(5):
        try:
            if not w3.is_connected():
                print("❌ No se pudo conectar al nodo. Reintentando...")
                time.sleep(5)
                continue

            balance = w3.eth.get_balance(fantasma_pub)
            eth_bal = w3.from_wei(balance, 'ether')
            
            print(f"📊 Intento {intento+1} - Saldo detectado: {eth_bal} ETH")
            
            if balance == 0:
                print("⏳ El nodo reporta 0. Esperando propagación de red...")
                time.sleep(15)
                continue

            # Cálculo de gas dinámico
            gas_price = int(w3.eth.gas_price * 1.5)
            gas_limit = 21000
            costo_gas = gas_price * gas_limit
            
            # TODO AL NODO A
            valor_envio = balance - costo_gas
            
            if valor_envio <= 0:
                print("❌ Saldo insuficiente para el gas de envío.")
                return

            tx = {
                'nonce': w3.eth.get_transaction_count(fantasma_pub),
                'to': nodo_a,
                'value': valor_envio,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': 8453
            }

            signed = w3.eth.account.sign_transaction(tx, fantasma_priv)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            
            print(f"🚀 ¡EXTRACCIÓN EXITOSA!")
            print(f"🔗 Hash: {tx_hash.hex()}")
            os.remove(__file__)
            return

        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    barrido_final()
