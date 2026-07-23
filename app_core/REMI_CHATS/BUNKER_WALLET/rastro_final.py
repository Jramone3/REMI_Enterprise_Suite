from web3 import Web3

# Conexión a la red Base
w3 = Web3(Web3.HTTPProvider('https://base.drpc.org'))

# La dirección donde el log dice que aterrizó el "polvo"
destino = '0x610178dA211FEF7D417bC0e6FeD39F05609AD788'

try:
    balance_wei = w3.eth.get_balance(destino)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    
    print("\n" + "="*40)
    print("🛰️  INFORME DE CAUDALES - BÚNKER")
    print("="*40)
    print(f"📍 DIRECCIÓN: {destino}")
    print(f"💰 SALDO ACTUAL: {balance_eth} ETH")
    print("="*40)
    
    if balance_eth > 0:
        print("🔥 ¡OBJETIVO LOCALIZADO! El dinero está en esa dirección.")
        print("💡 Si es tu cuenta de Binance, revisa tu historial de depósitos.")
    else:
        print("⚠️  SALDO CERO: El dinero pasó por aquí pero ya se movió o la red es otra.")
except Exception as e:
    print(f"❌ ERROR: {e}")
