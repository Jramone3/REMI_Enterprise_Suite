from web3 import Web3

# Configuración de Redes
w3_base = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
wallet_address = '0x96De980a766CCb10A19B6962587e2b61B650b372'
private_key = 'TU_LLAVE_PRIVADA_AQUI' # REMI: Ramón, pon tu llave aquí

# Dirección del Puente (Usaremos un Bridge directo para gas)
# Este es el contrato oficial de salida de Base
bridge_address = '0x4904803356221d621FBE3037494448c08276E36a' 

print(f"🚀 REMI: Iniciando transferencia de GAS desde Base a Mainnet...")

# 1. Preparar la transacción
nonce = w3_base.eth.get_transaction_count(wallet_address)
gas_price = w3_base.eth.gas_price

# Vamos a enviar 0.004 ETH para dejar un poquito para el gas en Base
amount_to_send = w3_base.to_wei(0.004, 'ether')

tx = {
    'nonce': nonce,
    'to': bridge_address, # Enviamos al contrato del puente
    'value': amount_to_send,
    'gas': 100000,
    'gasPrice': gas_price,
    'chainId': 8453 # ID de la red Base
}

# 2. Firmar y Enviar
signed_tx = w3_base.eth.account.sign_transaction(tx, private_key)
tx_hash = w3_base.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"✅ ¡Transmisión lograda! Hash en Base: {tx_hash.hex()}")
print(f"⏳ Ahora solo espera 5-10 minutos a que el radar detecte el saldo en Mainnet.")
