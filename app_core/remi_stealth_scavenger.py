import asyncio
import aiohttp
from web3 import AsyncWeb3, AsyncHTTPProvider

# Lista de nodos ultra-estables
NODOS = {
    'ETHEREUM': 'https://eth.llamarpc.com',
    'BASE': 'https://mainnet.base.org',
    'ARBITRUM': 'https://arbitrum.llamarpc.com',
    'POLYGON': 'https://polygon.meowrpc.com',
    'OPTIMISM': 'https://optimism.llamarpc.com'
}

async def scan_red(name, url):
    # Simulamos ser un navegador para evitar bloqueos 401/400
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0'}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        w3 = AsyncWeb3(AsyncHTTPProvider(url, request_kwargs={'timeout': 30}))
        print(f"📡 Sincronizando con {name}...")
        try:
            # Obtenemos las transacciones del bloque más reciente
            block = await w3.eth.get_block('latest', full_transactions=True)
            hallazgos = 0
            
            # Analizamos 30 transacciones para aumentar probabilidad
            for tx in block['transactions'][:30]:
                target = tx.get('to')
                if target:
                    balance = await w3.eth.get_balance(target)
                    val = float(w3.from_wei(balance, 'ether'))
                    
                    # Filtro de "Gas Dust" (0.005 a 0.1)
                    if 0.005 < val < 0.1:
                        print(f"✨ [{name}] Hallazgo: {target} | 💰 {val:.4f}")
                        hallazgos += 1
            
            if hallazgos == 0:
                print(f"[-] {name}: Escaneado sin residuos.")
        except Exception as e:
            print(f"⚠️ {name}: Saltado (Nodo ocupado)")

async def main():
    print("--- 🕵️ MODO SIGILO: RECOLECTOR DE GAS v3 ---")
    # Ejecutamos uno tras otro para no alertar a los Firewalls
    for name, url in NODOS.items():
        await scan_red(name, url)
        await asyncio.sleep(2) # Pausa estratégica

if __name__ == "__main__":
    asyncio.run(main())
