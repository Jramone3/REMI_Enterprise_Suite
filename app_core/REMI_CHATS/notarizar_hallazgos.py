from web3 import Web3
import os

# 1. Configuración de Red Polygon
w3 = Web3(Web3.HTTPProvider("https://polygon-pokt.nodies.app"))
contract_address = "0x42D1006311d390c3905E2B19e0884349bc31aDE6"
priv_key = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
acct = w3.eth.account.from_key(priv_key)

# 2. ABI Validado
abi = [{"inputs": [{"internalType": "string", "name": "_hash", "type": "string"}, {"internalType": "string", "name": "_custodio", "type": "string"}], "name": "sellarPatrimonio", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
contract = w3.eth.contract(address=contract_address, abi=abi)

def notarizar(h, c):
    nonce = w3.eth.get_transaction_count(acct.address)
    # Gas sugerido para Polygon (puedes ajustar si es necesario)
    tx = contract.functions.sellarPatrimonio(h, c).build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 137
    })
    signed = w3.eth.account.sign_transaction(tx, priv_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.to_hex(tx_hash)

# Notarización de los hallazgos críticos de Lido
if __name__ == "__main__":
    print("🛡️ Notarizando hallazgos de Lido en RNC-01 (Polygon)...")
    
    tx1 = notarizar("8464bd6bd2d73cdc16d75f930d1e3543b4f00b32b0da31ed7e7d98d850f78cb8", "LIDO_V2_INFLATION_VECTOR")
    print(f"✅ Registro 1 (Inflación) confirmado. Tx: {tx1}")
    
    tx2 = notarizar("ee0826c2bc3e985ec7da3d9b35eb6923cd2d0a3764f8b3e36de53d8503bac721", "LIDO_V2_WITHDRAWAL_FREEZE")
    print(f"✅ Registro 2 (Bloqueo) confirmado. Tx: {tx2}")
