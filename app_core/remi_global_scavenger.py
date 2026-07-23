import asyncio
import aiohttp
from web3 import AsyncWeb3, AsyncHTTPProvider

# Redes con RPCs públicos de alta disponibilidad
NODOS = {
    'ETHEREUM': 'https://cloudflare-eth.com',
    'BASE': 'https://mainnet.base.org',
    'ARBITRUM': 'https://arb1.chroniclelabs.io',
    'OPTIMISM': 'https://mainnet.optimism.io',
    'POLYGON': 'https://polygon.llamarpc.com'
}

async def scavenge(name, url):
    async with aiohttp.ClientSession() as session:
        w3 = AsyncWeb3(AsyncHTTPProvider(url))
        print(f"📡 Escaneando {name}...")
        try:
            # Miramos el último bloque
            block = await w3.eth.get_block('latest', full_transactions=True)
            count = 0
            
            for tx in block['transactions'][:20]: # Analizamos las primeras 20
                target = tx.get('to')
                if target:
                    balance = await w3.eth.get_balance(target)
                    eth_val = float(w3.from_wei(balance, 'ether'))
                    
                    # Rango de "Polvo de Gas": 0.005 a 0.05 unidades
                    if 0.005 < eth_val < 0.1:
                        print(f"✨ [{name}] Hallazgo: {target} | 💰 {eth_val:.4f}")
                        count += 1
            if count == 0:
                print(f"[-] {name}: Sin residuos claros en este bloque.")
        except Exception as e:
            print(f"❌ {name}: Nodo saturado o error: {str(e)[:40]}")

async def main():
    print("--- ⛽ INICIANDO RECOLECCIÓN GLOBAL DE GAS ---")
    tasks = [scavenge(name, url) for name, url in NODOS.items()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
