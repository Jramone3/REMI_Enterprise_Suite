from web3 import Web3
import os
import json
from solcx import compile_standard, install_solc

# 1. Cargar llave privada de forma segura
with open(os.path.expanduser("~/.remi_env"), "r") as f:
    priv_key = f.read().strip().replace("PRIVATE_KEY=", "")

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
acct = w3.eth.account.from_key(priv_key)

# 2. Cargar el contrato Patrimonio.sol
with open("contracts/Patrimonio.sol", "r") as f:
    source = f.read()

# 3. Compilar (Asegúrate de tener py-solc-x instalado)
install_solc('0.8.0')
compiled = compile_standard({
    "language": "Solidity",
    "sources": {"Patrimonio.sol": {"content": source}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "metadata", "evm.bytecode"]}}}
})

bytecode = compiled['contracts']['Patrimonio.sol']['PatrimonioREMI']['evm']['bytecode']['object']
abi = compiled['contracts']['Patrimonio.sol']['PatrimonioREMI']['abi']

# 4. Desplegar
Patrimonio = w3.eth.contract(abi=abi, bytecode=bytecode)
tx = Patrimonio.constructor().build_transaction({
    'from': acct.address,
    'nonce': w3.eth.get_transaction_count(acct.address),
    'gasPrice': w3.eth.gas_price
})

signed_tx = w3.eth.account.sign_transaction(tx, priv_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"🚀 Búnker V2 desplegado en: {tx_receipt.contractAddress}")
