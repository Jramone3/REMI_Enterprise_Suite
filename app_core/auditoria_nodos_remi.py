from web3 import Web3
import time

# Intentamos con un nodo de alta disponibilidad
RPC_URL = 'https://polygon.llamarpc.com'
w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'timeout': 20}))

nodos = {
    "Wallet_PC": "0x96De980a766CCb10A19B6962587e2b61B650b372",
    "Nodo_A_Gatillo": "0xB9073c07648a414B875874d7B8599dD2fAa171E8",
    "Nodo_B_Puente": "0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291",
    "Nodo_Fantasma": "0xe4EdB277328A32976F5E4aC18A494f1890d2979E",
    "Contrato_Request": "0x5E0f8E73884b3E124884b3E124884b3E124884b3"
}

print(f"\n📡 CONECTANDO A: {RPC_URL}")
print("🔍 REVISIÓN DE BÓVEDAS (POLYGON)")
print("-" * 50)

if not w3.is_connected():
    print("❌ No se pudo establecer conexión con el Nodo. Revisa tu internet.")
else:
    for nombre, addr in nodos.items():
        try:
            # Añadimos un pequeño retraso para evitar bloqueos
            time.sleep(1) 
            balance = w3.eth.get_balance(Web3.to_checksum_address(addr))
            pol = w3.from_wei(balance, 'ether')
            print(f"📍 {nombre:18} | {pol:.6f} POL")
        except Exception as e:
            print(f"❌ Error en {nombre}: {str(e)[:50]}")

print("-" * 50)
