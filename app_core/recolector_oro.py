import json
from web3 import Web3

# 1. CONEXIÓN A BASE (Donde está el contrato)
RPC_URL = "https://mainnet.base.org" 
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# 2. DATOS DE LA CORPORACIÓN (El contrato que me pasaste)
CONTRACT_ADDRESS = "0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf"
# ABI simplificada basada en lo que me enviaste
ABI = [
    {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"stateMutability":"payable","type":"receive"}
]

def escanear_locker():
    if not w3.is_connected():
        print("❌ No puedo conectar con la red Base.")
        return

    print(f"--- 🤖 REMI SCANNER: CONTRATO {CONTRACT_ADDRESS} ---")
    
    # Revisar balance del locker
    balance = w3.eth.get_balance(CONTRACT_ADDRESS)
    eth_balance = w3.from_wei(balance, 'ether')
    
    print(f"💰 Oro detectado en el locker: {eth_balance} ETH")
    
    # Intentar ver quién es el dueño actual en vivo
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    try:
        dueno = contract.functions.owner().call()
        print(f"👤 Dueño de la corporación: {dueno}")
    except:
        print("⚠️ No pude leer el dueño, el contrato está protegido.")

    if balance > 0:
        print("\n✨ ¡HAY POLVO DE ORO! El contrato tiene fondos liquidos.")
        print("Próximo paso: Buscar funciones de 'withdraw' o 'claim' en la implementación.")
    else:
        print("Empty locker. Los bots ya limpiaron aquí.")

if __name__ == "__main__":
    escanear_locker()
