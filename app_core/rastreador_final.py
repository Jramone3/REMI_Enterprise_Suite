from web3 import Web3

# Conexión a Ethereum Mainnet (La red de llegada)
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
wallet = '0x96De980a766CCb10A19B6962587e2b61B650b372'

def rastrear():
    print(f"\n🕵️‍♂️ REMI: Iniciando rastreo forense en Mainnet...")
    try:
        # 1. Ver saldo actual
        balance = w3.eth.get_balance(wallet)
        eth_balance = w3.from_wei(balance, 'ether')
        
        print(f"💰 Saldo confirmado: {eth_balance} ETH")
        
        # 2. Ver si hay transacciones internas (como las de Orbiter)
        if balance == 0:
            print("⏳ Estado: El dinero aún no ha tocado tierra en Ethereum.")
            print("💡 Acción: Si han pasado más de 2 horas, el 'Maker' de Orbiter está atascado.")
            print("🔗 Tu comprobante es el Hash de Base que ya tenemos.")
        else:
            print("✨ ¡OBJETIVO DETECTADO! El combustible ha llegado.")
            
    except Exception as e:
        print(f"❌ Error de conexión al nodo: {e}")

rastrear()
