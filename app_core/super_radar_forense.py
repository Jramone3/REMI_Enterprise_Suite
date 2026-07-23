from web3 import Web3
import time

# Lista de Nodos de Reserva (Diferentes puertas a Ethereum)
nodos = [
    'https://eth.llamarpc.com',
    'https://ethereum.publicnode.com',
    'https://rpc.ankr.com/eth',
    'https://1rpc.io/eth'
]

wallet = '0x96De980a766CCb10A19B6962587e2b61B650b372'

def escanear_profundo():
    print(f"\n🕵️‍♂️ REMI: Iniciando Escaneo Profundo Multicanal...")
    
    for url in nodos:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                balance = w3.eth.get_balance(wallet)
                eth_val = w3.from_wei(balance, 'ether')
                
                print(f"📡 Conectado vía: {url}")
                if balance > 0:
                    print(f"\n✨ ¡CHISPA DETECTADA!")
                    print(f"💰 Saldo: {eth_val} ETH")
                    print("🚀 ACCIÓN: Ejecuta flash_sombra_final.py")
                    return
                else:
                    print(f"⏳ Saldo: 0 ETH (Hora: {time.strftime('%H:%M:%S')})")
                    print("📦 Estado: Esperando liberación de Orbiter...")
                    return
        except:
            continue
    
    print("❌ Todos los nodos están ocupados. Reintentando en 30 segundos...")

if __name__ == "__main__":
    escanear_profundo()
