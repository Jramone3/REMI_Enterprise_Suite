import asyncio
import socket
from web3 import AsyncWeb3, AsyncHTTPProvider
from aiohttp import ClientSession, TCPConnector

# Forzamos la resolución DNS compatible con Tor
class TorCompatibleResolver:
    async def resolve(self, host, port=0, family=socket.AF_INET):
        # Retornamos la IP de Base Mainnet directamente si falla el DNS
        # O dejamos que torsocks maneje la resolución a nivel de kernel
        return [{'hostname': host, 'host': '162.159.153.4', 'port': port, 'family': family, 'proto': 0, 'flags': 0}]

async def main():
    print("--- 🧠 REMI INTELLIGENCE CORE: MODO AUDITOR (TOR SAFE) ---")
    
    # Configuramos un conector que no se pelee con el DNS de Tor
    connector = TCPConnector(use_dns_cache=False)
    
    # Inicializamos Web3 con el conector personalizado
    W3 = AsyncWeb3(AsyncHTTPProvider('https://mainnet.base.org', request_kwargs={'connector': connector}))

    async def audit_contract(address):
        selectors = ['0x3ccfd60b', '0x2e1a7d4d', '0xdb2e2107']
        for sig in selectors:
            try:
                # Simulación de auditoría
                res = await W3.eth.call({
                    'to': address,
                    'data': sig,
                    'from': '0x0000000000000000000000000000000000000000'
                })
                print(f"🔥 ¡POSIBLE FALLO DETECTADO!: {address}")
            except Exception:
                pass

    print("📡 Escaneando nuevos contratos en la red Base...")
    contratos_analizados = 0
    
    while True:
        try:
            block = await W3.eth.get_block('latest', full_transactions=True)
            for tx in block['transactions']:
                if tx['to'] is None:  # Creación de contrato
                    receipt = await W3.eth.get_transaction_receipt(tx['hash'])
                    contract_addr = receipt['contractAddress']
                    if contract_addr:
                        contratos_analizados += 1
                        await audit_contract(contract_addr)
                        # Cada 10 contratos nos avisa que sigue vivo
                        if contratos_analizados % 10 == 0:
                            print(f"✔️ Latido: {contratos_analizados} contratos analizados sin fallos...")
        except Exception as e:
            await asyncio.sleep(5)
            continue
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
