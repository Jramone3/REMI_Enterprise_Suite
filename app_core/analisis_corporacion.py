import requests
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
IMP_ADDRESS = "0xcCB20AA0413ea73C50142F1CFf461b07f5ae5e48"

def extraer_secretos():
    print(f"--- 🕵️‍♂️ EXTRACCIÓN PROFUNDA: {IMP_ADDRESS} ---")
    code = w3.eth.get_code(IMP_ADDRESS).hex()
    
    # Estos son los "motores" de las funciones (PUSH4)
    # Buscamos la firma 0x3635 (CALLDATALOAD) y comparaciones
    print("Buscando 'puertas de salida' en el laberinto de 17KB...")
    
    # Vamos a buscar funciones que suelen ser para mover pasta
    interesantes = {
        "0x00000000": "❗ POSIBLE FUNCIÓN DE RESCATE",
        "0xf3fde38b": "transferOwnership",
        "0x3ccfd60b": "withdraw",
        "0x5fd8c710": "withdraw(address)",
        "0x23b872dd": "transferFrom (¡ORO DE OTROS!)"
    }

    encontradas = 0
    for selector, nombre in interesantes.items():
        if selector in code:
            print(f"🚩 ¡ENCONTRADA!: {nombre} en el offset {code.find(selector)}")
            encontradas += 1

    if encontradas == 0:
        print("❌ Los pajaritos usan funciones personalizadas. Necesitamos 'picar' el código.")
    
    # Truco: Si el contrato tiene 'selfdestruct' (0xff), podemos romper el locker
    if "ff" in code[-100:]:
        print("⚠️ ¡CUIDADO! El contrato tiene botón de AUTODESTRUCCIÓN.")

if __name__ == "__main__":
    extraer_secretos()
