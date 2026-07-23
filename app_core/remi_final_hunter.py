import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

w3 = AsyncWeb3(AsyncHTTPProvider('https://base-mainnet.public.blastapi.io'))

async def auditoria_final(target):
    balance = await w3.eth.get_balance(target)
    eth_val = w3.from_wei(balance, 'ether')
    
    # Si el contrato tiene saldo, pero el código es muy corto, es una mina de oro
    code = await w3.eth.get_code(target)
    code_len = len(code)
    
    print(f"\n--- 🔍 ESCÁNER DE PROFUNDIDAD ---")
    print(f"📍 Dirección: {target}")
    print(f"💰 Saldo: {eth_val} ETH")
    print(f"📏 Tamaño del ADN: {code_len} bytes")
    
    if code_len < 2000 and float(eth_val) > 0.1:
        print("🔥 ¡ALERTA! Contrato pequeño con mucho saldo. ALTA PROBABILIDAD DE MINA.")
    else:
        print("[-] Parece un contrato complejo o sistema automático.")

async def main():
    # Probamos con el nuevo hallazgo de 1.28 ETH
    await auditoria_final('0x95dd05950bc8CD5dEF7be0aDC600D0fadd15Bd86')

if __name__ == "__main__":
    asyncio.run(main())
