from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# CONFIGURACIÓN
priv_key = 'os.getenv("PRIVATE_KEY")'
acct = w3.eth.account.from_key(priv_key)
contrato_fantasma = w3.to_checksum_address('0x7dab20b8e9113f873c3b715536e657ff93897b6b')

# El selector de autodestrucción que vimos en el Bytecode
data_activacion = "0x3fb674f1" 

print(f"🧨 REMI: FORZANDO LIQUIDACIÓN TOTAL EN {contrato_fantasma}...")

# Subimos el GAS para que no haya excusas de la red
tx = {
    'from': acct.address,
    'to': contrato_fantasma,
    'nonce': w3.eth.get_transaction_count(acct.address),
    'gas': 250000, 
    'gasPrice': int(w3.eth.gas_price * 1.5), # Pagamos un poco más para prioridad
    'data': data_activacion,
    'chainId': 8453
}

try:
    signed = w3.eth.account.sign_transaction(tx, priv_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"🚀 GATILLO DE EMERGENCIA LANZADO")
    print(f"🔗 Hash: {tx_hash.hex()}")
    print("⏳ Esperando 10 segundos para confirmar destrucción...")
except Exception as e:
    print(f"❌ ERROR: {e}")
