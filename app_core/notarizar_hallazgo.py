from web3 import Web3

# Configuración de tu nueva Notaría
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
PRIV_KEY = '9bb4285c9609feee26c70d2045fe8d72cd121ef985045fd8d9cfa807c7779de2' # Usa la misma llave del búnker
CONTRACT_ADDRESS = w3.to_checksum_address('0x6043370c0e2a5209e8193aba850145d89cda9ea0')
# ABI necesario para llamar a la función registrarHallazgo
abi = [
    {"inputs": [{"internalType": "string", "name": "_protocolo", "type": "string"}, {"internalType": "string", "name": "_hash", "type": "string"}],
     "name": "registrarHallazgo", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def registrar_hallazgo(protocolo, hash_hallazgo):
    acct = w3.eth.account.from_key(PRIV_KEY)
    tx = contract.functions.registrarHallazgo(protocolo, hash_hallazgo).build_transaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 8453
    })
    
    signed = w3.eth.account.sign_transaction(tx, PRIV_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Hallazgo sellado en RNC-01 | Tx: {tx_hash.hex()}")

# Ejemplo de uso:
# registrar_hallazgo("NombreDelProtocolo", "TU_HASH_SHA256_DEL_BUG")
registrar_hallazgo("Threshold Network", "ee0826c2bc3e985ec7da3d9b35eb6923cd2d0a3764f8b3e36de53d8503bac721")
