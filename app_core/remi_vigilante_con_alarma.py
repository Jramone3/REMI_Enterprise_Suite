import time
from web3 import Web3
import os

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
wallet = '0x96De980a766CCb10A19B6962587e2b61B650b372'

print("📡 [REMI]: Vigilante con Alarma activado. Si el saldo sube, sonará un aviso.")

while True:
    try:
        balance = w3.eth.get_balance(wallet)
        eth_balance = w3.from_wei(balance, 'ether')
        
        print(f"🕵️‍♂️ REMI: Vigilando... Saldo: {eth_balance} ETH (Hora: {time.strftime('%H:%M:%S')})")
        
        if balance > 0:
            print("🚀 ¡CHISPA DETECTADA! El gas ha llegado.")
            for i in range(5):
                os.system('spd-say "Gas detectado, Ramón. Despierta."') # Si tienes instalado speech-dispatcher
                print('\a') # Pitido del sistema
                time.sleep(1)
            break
            
    except Exception as e:
        print(f"❌ Error de red: {e}")
    
    time.sleep(30)
