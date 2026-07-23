from web3 import Web3

# Conexión a la red Base
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# CONFIGURACIÓN DE SEGURIDAD
priv_key = 'os.getenv("PRIVATE_KEY")'
acct = w3.eth.account.from_key(priv_key)

# DIRECCIÓN REAL GENERADA EN BASESCAN (Tu Cuenta Fantasma)
contrato_fantasma = '0x7dab20b8e9113f873c3b715536e657ff93897b6b'

# Tu wallet personal donde llegará el dinero
mi_wallet_pc = '0x96De980a766CCb10A19B6962587e2b61B650b372'

# Función de activación: "Liquidar y Autodestruir"
data_activacion = "0x3fb674f1" 

print(f"🔥 REMI: ACTIVANDO PROTOCOLO DE LIQUIDACIÓN...")
print(f"📡 CONTRATO ORIGEN: {contrato_fantasma}")
print(f"💰 DESTINO FINAL: {mi_wallet_pc}")

# Verificar si hay saldo antes de proceder
balance = w3.eth.get_balance(contrato_fantasma)
if balance == 0:
    print(f"⚠️ ADVERTENCIA: El contrato fantasma no tiene fondos todavía (Saldo: 0 ETH).")
    print(f"Asegúrate de enviar los fondos a {contrato_fantasma} antes de ejecutar este gatillo.")
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
    print(f"🚀 MISIÓN EJECUTADA. Los fondos están siendo transferidos.")
    print(f"🧹 El contrato se está autodestruyendo para borrar la huella.")
    print(f"🔗 Hash de salida: {tx_hash.hex()}")
except Exception as e:
    print(f"❌ ERROR EN LA OPERACIÓN: {e}")
