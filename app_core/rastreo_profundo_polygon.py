import asyncio
import aiohttp
from web3 import AsyncWeb3, AsyncHTTPProvider

# Usaremos nodos más estables para evitar el error 401
NODOS = [
    'https://polygon-bor-rpc.publicnode.com',
    'https://polygon.drpc.org',
    'https://1rpc.io/matic'
]

async def scan_range_with_memory(w3, start, end):
    SALTO = 1000 
    print(f"🔎 Modo Tuneladora: Saltando de {SALTO} en {SALTO}...")
    
    for block_num in range(start, 0, -SALTO):
        try:
            with open("last_block.txt", "w") as f:
                f.write(str(block_num))
        except: pass
            
        try:
            # Quitamos 'full_transactions=True' para que el nodo no pese tanto y no nos de error 400
            block = await asyncio.wait_for(w3.eth.get_block(block_num), timeout=5.0)
            if not block: continue
            
            # Buscamos las transacciones de forma más ligera
            txs = block.get('transactions', [])
            for tx_hash in txs:
                try:
                    # Obtenemos la tx individualmente
                    tx = await w3.eth.get_transaction(tx_hash)
                    addr = tx['to']
                    if addr:
                        bal_wei = await w3.eth.get_balance(addr)
                        if bal_wei > w3.to_wei(20, 'ether'):
                            code = await w3.eth.get_code(addr)
                            if len(code) > 100:
                                print(f"\n💎 ¡ORO!: {addr} | 💰 {w3.from_wei(bal_wei, 'ether')} POL")
                except: continue
            
            print(f"⏳ Bloque actual: {block_num} | i5-650 Buscando...", end="\r")
            await asyncio.sleep(0.1) 
        except Exception:
            continue

async def main():
    print("🚀 REMI DEEP-SCAN v4.1 - COMPATIBILITY FIX")
    # Limpiamos los headers para evitar el error "Can not decode content-encoding: br"
    headers = {'Accept-Encoding': 'identity'} 
    
    start_block = None
    try:
        with open("last_block.txt", "r") as f:
            line = f.read().strip()
            if line: start_block = int(line)
    except: pass

    for url in NODOS:
        print(f"📡 Intentando con: {url}")
        # Desactivamos la compresión automática que causa el error 'br'
        w3 = AsyncWeb3(AsyncHTTPProvider(url, request_kwargs={'headers': headers}))
        
        try:
            if await w3.is_connected():
                latest = await w3.eth.block_number
                actual_start = start_block if start_block else latest
                print(f"✅ ¡DENTRO! | Iniciando en: {actual_start}")
                await scan_range_with_memory(w3, actual_start, 0)
                return
        except Exception as e:
            print(f"❌ Fallo: {e}")
            continue

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Detenido.")
