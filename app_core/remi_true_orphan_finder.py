import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

w3 = AsyncWeb3(AsyncHTTPProvider('https://mainnet.base.org'))

async def check_orphan(addr):
    addr = w3.to_checksum_address(addr)
    balance = await w3.eth.get_balance(addr)
    eth_val = w3.from_wei(balance, 'ether')
    
    # Selector de owner()
    try:
        owner_data = await w3.eth.call({'to': addr, 'data': '0x8da5cb5b'})
        owner = "0x" + owner_data.hex()[-40:]
    except:
        owner = "unknown"

    if float(eth_val) > 0.05:
        print(f"\n📍 Analizando: {addr}")
        print(f"💰 Saldo: {eth_val} ETH")
        print(f"👤 Owner: {owner}")
        
        if owner == "0x0000000000000000000000000000000000000000":
            print("🔥 ¡MINA DETECTADA! Contrato con saldo y SIN DUEÑO.")
        else:
            print("[-] Propiedad privada. Saltando...")

async def main():
    print("--- 🔍 BUSCADOR DE HUÉRFANOS REALES ---")
    # Aquí pondríamos la lista de contratos que tu escáner v4 detecte
    objetivos = ["0x3d126d6B1581f7566a34bD4e912920bBA41367D5", "0x95dd05950bc8CD5dEF7be0aDC600D0fadd15Bd86"]
    for obj in objetivos:
        await check_orphan(obj)

if __name__ == "__main__":
    asyncio.run(main())
