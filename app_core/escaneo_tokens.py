from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
PROXY_ADDR = "0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf"

# Lista de tokens comunes donde los bots suelen dejar "polvo"
TOKENS = {
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "WETH": "0x4200000000000000000000000000000000000006",
    "DAI": "0x50c5725949A6F0c72E6C4564183900781479Af21"
}

def escanear_bolsillos():
    print(f"\n--- 💎 BUSCANDO TOKENS EN EL LOCKER ---")
    
    for nombre, addr in TOKENS.items():
        # Llamada mínima para balance de tokens (0x70a08231)
        data = "0x70a08231" + PROXY_ADDR[2:].zfill(64)
        try:
            res = w3.eth.call({'to': addr, 'data': data})
            balance = int(res.hex(), 16)
            if balance > 0:
                print(f"🚩 ¡ORO ENCONTRADO!: {balance / 10**6 if 'USD' in nombre else balance / 10**18:.4f} {nombre}")
            else:
                print(f"⚪ {nombre}: 0")
        except:
            print(f"❌ No pude leer {nombre}")

if __name__ == "__main__":
    escanear_bolsillos()
