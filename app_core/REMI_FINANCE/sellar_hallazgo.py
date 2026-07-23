import sys
from web3 import Web3
import os
from dotenv import load_dotenv

# Cargar entorno
load_dotenv(os.path.expanduser('~/.bunker_env'))
w3 = Web3(Web3.HTTPProvider('https://1.rpc.thirdweb.com'))
# Configuración del contrato RNC-01
contract_address = "0x38e8645325E6D26301a3F7556627Cffe1D68b875"
abi = '[{"inputs":[{"internalType":"string","name":"_hash","type":"string"},{"internalType":"string","name":"_protocolo","type":"string"}],"name":"sellarPatrimonio","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
contract = w3.eth.contract(address=contract_address, abi=abi)

def sellar(hash_auditoria, protocolo):
    acct = w3.eth.account.from_key(os.getenv('BUNKER_KEY'))
    nonce = w3.eth.get_transaction_count(acct.address)
    
    tx = contract.functions.sellarPatrimonio(hash_auditoria, protocolo).build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 137
    })
    
    signed = w3.eth.account.sign_transaction(tx, os.getenv('BUNKER_KEY'))
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()

# Ejecución
if __name__ == "__main__":
    protocolo = sys.argv[1]
    hash_audit = sys.argv[2]
    print(f"🚀 Sellando auditoría para {protocolo}...")
    print(f"🔗 Hash en Blockchain: {sellar(hash_audit, protocolo)}")
