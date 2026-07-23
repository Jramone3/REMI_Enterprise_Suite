import asyncio
import aiohttp
from web3 import AsyncWeb3, AsyncHTTPProvider

NODOS = {
    'BASE': 'https://mainnet.base.org',
    'ARBITRUM': 'https://arbitrum.llamarpc.com',
    'POLYGON': 'https://polygon-bor-rpc.publicnode.com'
}

async def scan_loop(name, url):
    w3 = AsyncWeb3(AsyncHTTPProvider(url))
    print(f"✅ Centinela activo en {name}")
    
    last_block = 0
    while True:
        try:
            current_block = await w3.eth.block_number
            if current_block > last_block:
                last_block = current_block
                block = await w3.eth.get_block(current_block, full_transactions=True)
                
                for tx in block['transactions'][:50]:
                    target = tx.get('to')
                    if target:
                        # Filtro rápido de saldo antes de pedir el código (ahorra tiempo)
                        balance = await w3.eth.get_balance(target)
                        eth_val = float(w3.from_wei(balance, 'ether'))
                        
                        if 0.002 <= eth_val <= 0.5:
                            code = await w3.eth.get_code(target)
                            # Si es un contrato pequeño y no es USDC/WETH
                            if 0 < len(code) < 2500:
                                print(f"\n🎯 [HALLAZGO] {name} Bloque {current_block}")
                                print(f"📍 Dirección: {target}")
                                print(f"💰 Saldo: {eth_val:.5f}")
                                print(f"📏 ADN: {len(code)} bytes")
                                print("-" * 30)
            
            await asyncio.sleep(2) # Espera para el siguiente bloque
        except Exception:
            await asyncio.sleep(5) # Si hay error, espera y reintenta

async def main():
    print("--- 🛰️ SISTEMA CENTINELA REMI IA ---")
    print("Escaneando en tiempo real. Presiona Ctrl+C para detener.")
    await asyncio.gather(
        scan_loop('BASE', NODOS['BASE']),
        scan_loop('ARBITRUM', NODOS['ARBITRUM']),
        scan_loop('POLYGON', NODOS['POLYGON'])
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPatrulla finalizada.")
