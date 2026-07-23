from web3 import Web3

# Conexión a la red Base
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# CONFIGURACIÓN DE SEGURIDAD
priv_key = 'os.getenv("PRIVATE_KEY")'
acct = w3.eth.account.from_key(priv_key)

# DIRECCIÓN FANTASMA (Convertida a Checksum para evitar el error)
contrato_fantasma = w3.to_checksum_address('0x7dab20b8e9113f873c3b715536e657ff93897b6b')

# Tu wallet personal (También en Checksum)
mi_wallet_pc = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

# Función de activación: "Liquidar y Autodestruir"
data_activacion = "0x3fb674f1" 

print(f"🔥 REMI: ACTIVANDO PROTOCOLO DE LIQUIDACIÓN FINAL...")

# Verificar saldo real en la cuenta fantasma
balance = w3.eth.get_balance(contrato_fantasma)
if balance == 0:
    print(f"⚠️  Saldo aún en 0. Esperando un momento a la red...")
else:
    print(f"💎 FONDOS DETECTADOS: {w3.from_wei(balance, 'ether')} ETH")

tx = {
    'from': acct.address,
    'to': contrato_fantasma,
    'nonce': w3.eth.get_transaction_count(acct.address),
    'gas': 150000,
    'gasPrice': w3.eth.gas_price,
    'data': data_activacion,
    'chainId': 8453
}

try:
    signed = w3.eth.account.sign_transaction(tx, priv_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"🚀 EXTRACCIÓN COMPLETADA HACIA: {mi_wallet_pc}")
    print(f"🧹 CUENTA FANTASMA AUTODESTRUIDA. No queda huella.")
    print(f"🔗 Hash final: {tx_hash.hex()}")
except Exception as e:
    print(f"❌ ERROR: {e}")
