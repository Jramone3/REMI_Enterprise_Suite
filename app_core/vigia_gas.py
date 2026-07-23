import time
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://1rpc.io/matic'))
# Vigilamos el Gatillo, que es quien necesita el POL
gatillo = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

print(f"📡 REMI: Vigía de gas activo. Esperando a Orbiter para la cuenta {gatillo}...")

while True:
    try:
        balance = w3.eth.get_balance(gatillo)
        pol = w3.from_wei(balance, 'ether')
        
        if pol > 0.1:
            print(f"\n⛽ ¡GAS DETECTADO! Saldo actual: {pol} POL")
            print("🚀 Ramón, el Gatillo está cargado. ¡Es hora de ejecutar!")
            break
        else:
            print(f"⏳ Saldo actual: {pol} POL... esperando.", end="\r")
            
    except Exception:
        pass
    time.sleep(30)
