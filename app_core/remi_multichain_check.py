import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

# Direcciones de los "nodos" para cada red
NODOS = {
    'BASE': 'https://base-mainnet.public.blastapi.io',
    'POLYGON': 'https://rpc.ankr.com/polygon',
    'ETHEREUM': 'https://eth.llamarpc.com'
}

CEREBRO = "0x0E5891b589417E49392D6664d603A1554F59feB0"

async def verificar_redes():
    print(f"\n--- 🌐 BUSCANDO EL CEREBRO EN EL MULTIVERSO ---")
    for red, url in NODOS.items():
        try:
            w3 = AsyncWeb3(AsyncHTTPProvider(url))
            # Corregimos checksum para cada red
            addr = w3.to_checksum_address(CEREBRO)
            code = await w3.eth.get_code(addr)
            
            status = "✅ CÓDIGO ENCONTRADO" if len(code) > 0 else "❌ VACÍO"
            print(f"[{red}]: {status} ({len(code)} bytes)")
        except Exception as e:
            print(f"[{red}]: Error de conexión")

if __name__ == "__main__":
    asyncio.run(verificar_redes())
