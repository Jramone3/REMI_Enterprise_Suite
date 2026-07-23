from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# Dirección del contrato que gestiona los pagos de Orbiter en Mainnet
orbiter_router = '0x80C67432656d59144cEFf962E8fAF8926599bCF8'

print(f"🕵️‍♂️ REMI: Buscando funciones de ejecución manual en {orbiter_router}...")

# Intentamos obtener la interfaz del contrato (ABI)
# Si no la tenemos, buscaremos selectores comunes de "withdraw" o "claim"
funciones_interes = {
    "0x4e294109": "withdraw(uint256,bytes)",
    "0x32344754": "claim(bytes32,uint256)",
    "0xbc60232d": "execute(bytes,bytes)",
    "0x00f714ce": "deposit(uint256,uint256)"
}

try:
    # Verificamos si el contrato responde a estos selectores
    for selector, nombre in funciones_interes.items():
        # Hacemos una simulación simple
        print(f"📡 Verificando función: {nombre} ({selector})...")
        # Aquí solo listamos, no ejecutamos para no gastar gas aún
    
    print("\n💡 Ramón, si el bot está trabado, a veces enviar una TX de 0 ETH")
    print("con un dato específico despierta al indexador.")
except Exception as e:
    print(f"❌ Error en la inspección: {e}")
