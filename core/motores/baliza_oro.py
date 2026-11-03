import json
import time
from web3 import Web3

# Configuración de Red Base (RPC Público)
BASE_RPC = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(BASE_RPC))

WALLET_PATH = "/home/ramon/REMI_CORE/oro_finance/remi_wallet.json"

def latido_oro():
    try:
        with open(WALLET_PATH, 'r') as f:
            wallet_data = json.load(f)
        
        address = wallet_data['address']
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        print(f"🛰️ [BALIZA_ORO] Pulso: OK | Billetera: {address[:6]}...{address[-4:]}")
        print(f"💰 [RECURSOS] Saldo en Base: {balance_eth} ETH")
        
        if balance_eth == 0:
            print("⚠️ [ALERTA] Sin combustible (Gas) para operaciones autónomas.")
            
    except Exception as e:
        print(f"❌ [ERROR_BALIZA] Fallo en el pulso de red: {e}")

if __name__ == "__main__":
    while True:
        latido_oro()
        time.sleep(15) # Ciclo de 15 segundos alineado con el Compendio
