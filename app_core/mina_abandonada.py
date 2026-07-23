import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
from collections import deque

# --- CONFIGURACIÓN DE REDES ---
REDES = {
    'BASE': 'https://base-mainnet.public.blastapi.io',
    'POLYGON': 'https://rpc.ankr.com/polygon'
}

# --- BLACKLIST REFORZADA ---
BLACK_LIST = {
    '0x0cb0354E9C51960a7875724343dfC37B93d32609', 
    '0x5e6bB47D89Fea09cf5a75ea7E3Fa2e804798Eb55', 
    '0x01Aa002D4419Dd7d8b469DA8134A21CdC7cB093D', 
    '0x4200000000000000000000000000000000000016', 
    '0x4200000000000000000000000000000000000006', 
    '0x1CE3712395ee4798ac9548B3E0220Ea6A2B61e79', 
    '0x000037bB05B2CeF17c6469f4BcDb198826Ce0000',
    '0x587A18dfcf4484Ce135F9C2A7cB066626037F637',
    '0x0000000000000000000000000000000000000000'
}

SELECTORES = ['0x3fb674f1', '0x3ccfd60b', '0x8fdab360']
SCANNED_CACHE = deque(maxlen=2000)
SEMAPHORE = asyncio.Semaphore(10)
W3_CLIENTS = {n: AsyncWeb3(AsyncHTTPProvider(r)) for n, r in REDES.items()}
LAST_BLOCK = {n: 0 for n in REDES}

async def analyze_target(w3, target, nombre, min_botin):
    if target in BLACK_LIST or target in SCANNED_CACHE:
        return
    SCANNED_CACHE.append(target)
    async with SEMAPHORE:
        try:
            balance = await w3.eth.get_balance(target)
            if balance < w3.to_wei(min_botin, 'ether'):
                return
            code = await w3.eth.get_code(target)
            if 100 < len(code) < 8000:
                for sel in SELECTORES:
                    try:
                        await w3.eth.call({'to': target, 'data': sel})
                        token = 'ETH' if nombre != 'POLYGON' else 'POL'
                        print(f'\n💎 [ORO DETECTADO]: {nombre} | {target} | 💰 {w3.from_wei(balance, "ether")} {token}')
                        BLACK_LIST.add(target)
                        break
                    except: continue
        except: pass

async def scan_network(nombre, w3):
    global LAST_BLOCK
    try:
        curr_bn = await w3.eth.block_number
        if curr_bn <= LAST_BLOCK[nombre]: return
        block = await w3.eth.get_block(curr_bn, full_transactions=True)
        LAST_BLOCK[nombre] = curr_bn
        targets = {tx['to'] for tx in block.transactions if tx['to']}
        min_botin = 0.5 if nombre != 'POLYGON' else 100.0
        await asyncio.gather(*(analyze_target(w3, t, nombre, min_botin) for t in targets))
    except: pass

async def main():
    print(f"\n🛡️ REMI SHIELD v3.0 - LISTO")
    print(f"Escaneando Base y Polygon...\n")
    while True:
        await asyncio.gather(*(scan_network(n, w3) for n, w3 in W3_CLIENTS.items()))
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
