import asyncio
import aiohttp
from web3 import AsyncWeb3, AsyncHTTPProvider

# Usamos RPCs más estables para evitar el "Error de conexión"
NODOS = {
    'BASE': 'https://mainnet.base.org',
    'POLYGON': 'https://polygon-rpc.com',
    'ETHEREUM': 'https://cloudflare-eth.com'
}

CEREBRO = "0x0E5891b589417E49392D6664d603A1554F59feB0"

async def verificar_redes():
    print(f"\n--- 🌐 ESCANEO MULTIVIA CORREGIDO ---")
    
    for red, url in NODOS.items():
        # Creamos una sesión nueva para cada intento para evitar cierres sucios
        async with aiohttp.ClientSession() as session:
            w3 = AsyncWeb3(AsyncHTTPProvider(url, request_kwargs={'timeout': 20}))
            try:
                addr = w3.to_checksum_address(CEREBRO)
                code = await w3.eth.get_code(addr)
                
                status = "✅ CÓDIGO ENCONTRADO" if len(code) > 0 else "❌ VACÍO"
                print(f"[{red:10}]: {status} ({len(code)} bytes)")
            except Exception as e:
                print(f"[{red:10}]: ⚠️ Error: {str(e)[:50]}")
        
        await asyncio.sleep(1) # Un respiro para el nodo

if __name__ == "__main__":
    asyncio.run(verificar_redes())
