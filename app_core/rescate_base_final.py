from web3 import Web3

# Usamos el nodo oficial
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

priv_key = 'os.getenv("PRIVATE_KEY")'
addr_origen = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
addr_destino = '0x96De980a766CCb10A19B6962587e2b61B650b372'

def envio_final():
    try:
        # El saldo exacto que nos dio tu comando anterior
        balance_wei = 4739897094150513 
        
        gas_limit = 21000
        # Gas barato pero suficiente para Base
        gas_price = w3.to_wei(0.05, 'gwei') 
        
        costo_gas = gas_price * gas_limit
        monto_enviar = balance_wei - costo_gas

        # Usamos el Nonce 35 (el siguiente después de la limpieza)
        tx = {
            'nonce': 35, 
            'to': addr_destino,
            'value': monto_enviar,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': 8453
        }

        signed_tx = w3.eth.account.sign_transaction(tx, priv_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"🚀 ¡RESQUICIO ENVIADO! Hash: {tx_hash.hex()}")
        print("Revisa tu wallet en 1 minuto.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    envio_final()
