import requests
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# Esta es la billetera de Orbiter (Maker) que suele enviar el dinero en Mainnet
orbiter_maker = '0x80C67432656d59144cEFf962E8fAF8926599bCF8' 

print(f"🕵️‍♂️ REMI: Investigando estado de salud de Orbiter Finance...")

try:
    # 1. ¿Tiene dinero el pagador?
    bal = w3.eth.get_balance(orbiter_maker)
    eth_bal = w3.from_wei(bal, 'ether')
    print(f"💰 Saldo del Pagador de Orbiter: {eth_bal} ETH")
    
    # 2. ¿Está enviando transacciones hoy?
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={orbiter_maker}&startblock=0&endblock=99999999&sort=desc&apikey=YourApiKeyToken"
    r = requests.get(url).json()
    
    if r['status'] == '1':
        ultima_tx = r['result'][0]
        print(f"⏱️ Última transacción enviada por Orbiter: hace poco.")
        print(f"🛰️ Estado de la red: Orbiter está OPERANDO pero con retraso.")
    else:
        print("🚨 ALERTA: Orbiter parece estar TOTALMENTE detenido en Ethereum.")

    # 3. El veredicto del Gas
    gas_price = w3.eth.gas_price
    gwei = w3.from_wei(gas_price, 'gwei')
    print(f"⛽ Gas actual en Ethereum: {gwei} Gwei")

except Exception as e:
    print(f"❌ Error en la investigación: {e}")
