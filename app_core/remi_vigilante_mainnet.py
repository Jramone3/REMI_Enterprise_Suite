import time
from web3 import Web3

# Esta vez conectamos a la red CARA (Mainnet)
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

print(f"🕵️‍♂️ REMI: Vigilando la Mainnet de Ethereum... (Ctrl+C para salir)")

def vigilar():
    while True:
        bal = w3.eth.get_balance(wallet)
        eth = w3.from_wei(bal, 'ether')
        print(f"📡 Saldo actual en Mainnet: {eth} ETH", end='\r')
        
        if bal >= w3.to_wei(0.015, 'ether'):
            print(f"\n🔥 ¡GAS DETECTADO! Saldo suficiente: {eth} ETH")
            print("🚀 Ramón, ejecuta ahora: python3 os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/operacion_sombra.py")
            break
        time.sleep(15)

if __name__ == "__main__":
    vigilar()
