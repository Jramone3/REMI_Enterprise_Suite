from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
PROXY_ADDR = "0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf"
IMP_ADDR = "0xcCB20AA0413ea73C50142F1CFf461b07f5ae5e48"

def buscar_inicializador():
    print(f"\n{'*'*50}")
    print(" 🕵️‍♂️ BUSCANDO PUERTA DE ENTRADA AL LOCKER")
    print(f"{'*'*50}")

    code = w3.eth.get_code(IMP_ADDR).hex()

    # Selectores de funciones de "Toma de Poder"
    puertas = {
        "0x8129fc1c": "initialize()",
        "0x485cc3a1": "initialize(address)",
        "0xc4d66de8": "initialize(address,bytes)",
        "0xf2fde38b": "transferOwnership(address)",
        "0x09051830": "reclaim()"
    }

    exito = False
    for selector, nombre in puertas.items():
        if selector[2:] in code:
            print(f"🚩 ¡PUERTA DETECTADA!: {nombre} ({selector})")
            exito = True

    if not exito:
        print("🔒 No detecto inicializadores estándar. Usan nombres personalizados.")
    
    print(f"\n💰 Balance en riesgo: {w3.from_wei(w3.eth.get_balance(PROXY_ADDR), 'ether')} ETH")
    print(f"{'*'*50}\n")

if __name__ == "__main__":
    buscar_inicializador()
