import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

w3 = AsyncWeb3(AsyncHTTPProvider('https://mainnet.base.org'))

# Dirección del Proxy con los 1.28 ETH
PROXY = w3.to_checksum_address("0x95dd05950bc8CD5dEF7be0aDC600D0fadd15Bd86")

# El "Slot" de administración según el estándar EIP-1967
ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"

async def check_admin():
    print(f"\n--- 🕵️ BUSCANDO AL DUEÑO DEL ZOMBI ---")
    # Leemos directamente el espacio de memoria donde se guarda el Admin
    admin_data = await w3.eth.get_storage_at(PROXY, ADMIN_SLOT)
    admin_address = "0x" + admin_data.hex()[-40:]
    
    print(f"📍 Admin actual en memoria: {admin_address}")
    
    if admin_address == "0x0000000000000000000000000000000000000000":
        print("🔥 ¡ALERTA! El contrato no tiene Admin definido. ¡PODRÍA ESTAR LIBRE!")
    else:
        print(f"[-] El contrato está bajo el control de: {admin_address}")

if __name__ == "__main__":
    asyncio.run(check_admin())
