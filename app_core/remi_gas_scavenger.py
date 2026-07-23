import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

# Redes donde el gas residual es común
RPCs = {
    'BASE': 'https://mainnet.base.org',
    'POLYGON': 'https://polygon-rpc.com'
}

async def scan_gas_scraps(name, url):
    w3 = AsyncWeb3(AsyncHTTPProvider(url))
    print(f"\n--- ⛽ ESCANEANDO RESIDUOS EN {name} ---")
    
    # Bloque actual
    try:
        latest_block = await w3.eth.get_block('latest')
        # Escaneamos las últimas 10 transacciones del bloque buscando fallos
        for tx_hash in latest_block['transactions'][-10:]:
            tx = await w3.eth.get_transaction(tx_hash)
            # Si el valor es 0 pero el gas usado fue alto, es un bot de arbitraje
            # Si el receptor es un contrato nuevo, podría haber gas residual
            target = tx['to']
            if target:
                balance = await w3.eth.get_balance(target)
                eth_val = w3.from_wei(balance, 'ether')
                
                # Buscamos "Gas Dust": entre 0.001 y 0.01 ETH
                if 0.001 < float(eth_val) < 0.05:
                    print(f"✨ [POLVO DETECTADO]: {target} | 💰 {eth_val} {('ETH' if name=='BASE' else 'POL')}")
    except Exception as e:
        print(f"Error en {name}: {e}")

async def main():
    await asyncio.gather(
        scan_gas_scraps('BASE', RPCs['BASE']),
        scan_gas_scraps('POLYGON', RPCs['POLYGON'])
    )

if __name__ == "__main__":
    asyncio.run(main())
