import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

# Baliza Triple-Red
RPCs = {
    'BASE': 'https://base-mainnet.public.blastapi.io',
    'POLYGON': 'https://rpc.ankr.com/polygon'
}

async def auditar_profundo(nombre, rpc, target):
    w3 = AsyncWeb3(AsyncHTTPProvider(rpc))
    try:
        balance = await w3.eth.get_balance(target)
        # Solo nos importa si hay más de 0.1 ETH / 50 POL
        umbral = 0.1 if nombre == 'BASE' else 50.0
        
        eth_val = w3.from_wei(balance, 'ether')
        if float(eth_val) > umbral:
            # La prueba de fuego: ¿Es un Proxy o un contrato simple?
            code = await w3.eth.get_code(target)
            is_proxy = "masterCopy" in str(code) or "implementation" in str(code)
            
            print(f"\n📡 BALIZA DETECTÓ CALOR EN {nombre}")
            print(f"📍 Wallet: {target}")
            print(f"💰 Saldo: {eth_val} {('ETH' if nombre=='BASE' else 'POL')}")
            print(f"⚠️ ¿Es un contrato blindado (Proxy)?: {'SÍ (Ignorar)' if is_proxy else 'NO (MINA POSIBLE)'}")
    except:
        pass

async def main():
    print("--- 📡 BALIZA REMI v5.0 ACTIVADA ---")
    # Prueba con los objetivos que encontramos hoy
    targets = [
        ('BASE', '0x3d126d6B1581f7566a34bD4e912920bBA41367D5'),
        ('BASE', '0x95dd05950bc8CD5dEF7be0aDC600D0fadd15Bd86')
    ]
    for red, wallet in targets:
        await auditar_profundo(red, RPCs[red], wallet)

if __name__ == "__main__":
    asyncio.run(main())
