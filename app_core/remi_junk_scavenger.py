import asyncio
import aiohttp
from web3 import AsyncWeb3, AsyncHTTPProvider

# Lista negra: Ignoramos USDC, WETH, y contratos de infraestructura conocidos
LISTA_NEGRA = [
    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", # USDC Base
    "0x4200000000000000000000000000000000000006", # WETH
    "0x0000000000000000000000000000000000000000"  # Null
]

NODOS = {
    'BASE': 'https://mainnet.base.org',
    'POLYGON': 'https://polygon.meowrpc.com',
    'ARBITRUM': 'https://arbitrum.llamarpc.com'
}

async def scan_junk(name, url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        w3 = AsyncWeb3(AsyncHTTPProvider(url))
        print(f"📡 Buscando chatarra real en {name}...")
        try:
            block = await w3.eth.get_block('latest', full_transactions=True)
            for tx in block['transactions'][:40]:
                target = tx.get('to')
                if target and target not in LISTA_NEGRA:
                    # Buscamos contratos con poco código (bots simples)
                    code = await w3.eth.get_code(target)
                    if 0 < len(code) < 2000: # Filtro de tamaño: contratos pequeños
                        balance = await w3.eth.get_balance(target)
                        val = float(w3.from_wei(balance, 'ether'))
                        
                        if 0.005 < val < 0.2:
                            print(f"🔥 [CHATARRA DETECTADA] {name}: {target} | 💰 {val:.4f} ETH")
        except:
            pass

async def main():
    print("--- 🗑️ SCANNER DE CHATARRA Y RESIDUOS v4 ---")
    for name, url in NODOS.items():
        await scan_junk(name, url)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
