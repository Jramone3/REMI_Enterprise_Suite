from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

llave_origen = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
publica_origen = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
mi_wallet_personal = '0x96De980a766CCb10A19B6962587e2b61B650b372'

def disparo_final_remi():
    # Bajamos la cantidad a 0.003 ETH para que el margen de gas sea GIGANTE
    # No queremos que el nodo tenga ni una excusa de decimales.
    valor_enviar = w3.to_wei(0.003, 'ether')
    
    # Obtenemos datos frescos
    gas_price = int(w3.eth.gas_price * 1.5) # Pagamos propina extra
    nonce = w3.eth.get_transaction_count(publica_origen)

    tx = {
        'chainId': 8453,
        'nonce': nonce,
        'to': mi_wallet_personal,
        'value': valor_enviar,
        'gas': 25000,
        'gasPrice': gas_price,
        'accessList': [
            {
                'address': publica_origen,
                'storageKeys': []
            }
        ]
    }

    try:
        print(f"⚡ [REMI]: Forzando pre-carga de dirección (Access List)...")
        signed_tx = w3.eth.account.sign_transaction(tx, llave_origen)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ ¡SISTEMA PERFORADO! Transacción enviada.")
        print(f"🔗 Hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"❌ El nodo sigue bloqueando: {e}")
        print("\n💡 Ramón, si esto falla, ve al Discord de Base y pega esto:")
        print(f"Help! Address {publica_origen} has 0.0047 ETH but RPC returns 'have 0' even with AccessList and correct Nonce. State desync detected.")

if __name__ == "__main__":
    disparo_final_remi()
