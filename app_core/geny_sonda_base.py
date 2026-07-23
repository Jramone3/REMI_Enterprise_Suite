from web3 import Web3

# Conectamos a Base
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
mi_bunker = w3.to_checksum_address('0x6a8a0ec01dfe9e8bc385c743204e674ed705dafc')
mi_wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

print(f"🚀 GENY: Iniciando escaneo de activos en red Base...")

def escanear():
    # 1. Ver ETH
    eth = w3.eth.get_balance(mi_wallet)
    print(f"🔹 Wallet Personal: {w3.from_wei(eth, 'ether')} ETH")
    
    # 2. Ver si el contrato tiene funciones de reclamo activas
    # (Simulamos una llamada de mantenimiento)
    print(f"🔎 Analizando integridad del Búnker...")
    code = w3.eth.get_code(mi_bunker)
    if len(code) > 0:
        print(f"✅ Búnker Online ({len(code)} bytes de blindaje)")
    else:
        print(f"⚠️ El Búnker no responde. Revisar RPC.")

if __name__ == "__main__":
    escanear()
