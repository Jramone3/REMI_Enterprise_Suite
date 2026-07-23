from web3 import Web3

# Conexión al nodo de Ethereum
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
wallet = '0x96De980a766CCb10A19B6962587e2b61B650b372'

try:
    bal = w3.eth.get_balance(wallet)
    eth = w3.from_wei(bal, 'ether')
    print(f"\n💰 SALDO EN MAINNET: {eth} ETH")
    
    if bal > 0:
        print("✅ ¡EL GAS YA ESTÁ AQUÍ!")
    else:
        print("⏳ Sigue en 0. Orbiter está procesando el cruce...")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
