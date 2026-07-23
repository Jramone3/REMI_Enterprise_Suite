import time
from web3 import Web3

# Conexión a Ethereum Mainnet
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

print(f"🛰️ RADAR: Vigilando llegada de ETH desde Orbiter... (Ctrl+C para salir)")

def monitorear():
    saldo_inicial = w3.eth.get_balance(wallet)
    while True:
        try:
            actual = w3.eth.get_balance(wallet)
            eth = w3.from_wei(actual, 'ether')
            
            if actual > saldo_inicial:
                print(f"\n✨ ¡RECARGA DETECTADA! ✨")
                print(f"💰 Saldo nuevo en Mainnet: {eth} ETH")
                print(f"🚀 Ramón, ya puedes ejecutar: python3 os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/flash_sombra_final.py")
                break
            else:
                print(f"⏳ Esperando... Saldo actual: {eth} ETH", end='\r')
        except:
            print("📡 Error de conexión, reintentando...")
        
        time.sleep(10)

if __name__ == "__main__":
    monitorear()
