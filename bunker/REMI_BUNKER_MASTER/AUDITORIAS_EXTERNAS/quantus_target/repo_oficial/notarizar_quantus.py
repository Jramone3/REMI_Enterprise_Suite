from web3 import Web3

PRIV_KEY = '9bb4285c9609feee26c70d2045fe8d72cd121ef985045fd8d9cfa807c7779de2'
CONTRACT_ADDRESS = '0x6043370c0e2a5209e8193aba850145d89cda9ea0'
RPC_URL = 'https://mainnet.base.org'
HASH_TARGET = '176b010ee448b2d9e8b92a1af0be5181c8fd4a8995a41de485e00c13cab19d97'

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("❌ Error: No se pudo conectar a la red Base.")
    exit()

acct = w3.eth.account.from_key(PRIV_KEY)
nonce = w3.eth.get_transaction_count(acct.address)

# Preparamos los datos de la transacción incluyendo el hash como payload de datos (data)
# Esto asegura que el hash quede inmutablemente registrado en la traza de la llamada al contrato.
payload_data = w3.to_hex(text=HASH_TARGET)

tx = {
    'from': acct.address,
    'to': Web3.to_checksum_address(CONTRACT_ADDRESS),
    'value': 0,
    'nonce': nonce,
    'gas': 100000,
    'gasPrice': w3.eth.gas_price,
    'data': payload_data,
    'chainId': w3.eth.chain_id
}

signed_tx = w3.eth.account.sign_transaction(tx, PRIV_KEY)
print("🚀 Enviando transacción de notaría a la red Base...")
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"✅ ¡Notaría completada con éxito!")
print(f"🔗 Hash de la Transacción (TxHash): {tx_hash.hex()}")
