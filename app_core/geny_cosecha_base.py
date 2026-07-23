import time
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

# Direcciones de "Gas Refuel" y "Rewards" en Base
REWARD_CONTRACTS = {
    'Base Paint Rewards': '0xBa5e000000000000000000000000000000000000', # Placeholder
    'Bungee Refuel': '0x6e885d958564da8a670354b341f530e704179373',
    'Merkly Gas': '0x2213d289417904a9b6278623f2984d63b49d4535'
}

print(f"🚜 GENY: Iniciando cosecha de 'Dust' y Recompensas en Base...")

def buscar_reclamables():
    # 1. Verificar balance actual exacto
    bal = w3.eth.get_balance(wallet)
    print(f"💰 Balance actual: {w3.from_wei(bal, 'ether')} ETH")

    # 2. Simular llamadas a funciones 'claim' o 'withdraw' comunes
    # Nota: Esto es una sonda de reconocimiento
    for nombre, addr in REWARD_CONTRACTS.items():
        try:
            target = w3.to_checksum_address(addr)
            # Probamos si hay un balance interno en esos contratos para ti
            # Usamos el selector genérico de saldo: 0x70a08231
            data = "0x70a08231" + wallet[2:].lower().zfill(64)
            res = w3.eth.call({'to': target, 'data': data})
            print(f"🔎 {nombre}: Respuesta {res.hex()[:10]}...")
        except:
            print(f"❌ {nombre}: Sin respuesta.")

if __name__ == "__main__":
    buscar_reclamables()
