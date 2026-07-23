import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

w3 = AsyncWeb3(AsyncHTTPProvider('https://mainnet.base.org'))
PROXY = w3.to_checksum_address("0x95dd05950bc8CD5dEF7be0aDC600D0fadd15Bd86")

async def simulate():
    print(f"\n--- 🚀 SIMULACIÓN DE RECLAMO TÁCTICO ---")
    
    # Intentamos leer quién es el 'owner()' oficial por si no usa el ADMIN_SLOT estándar
    # El selector 0x8da5cb5b es para 'owner()'
    try:
        result = await w3.eth.call({'to': PROXY, 'data': '0x8da5cb5b'})
        owner = "0x" + result.hex()[-40:]
        print(f"👤 Owner reportado por código: {owner}")
    except:
        print("[-] El contrato no responde a la función owner().")

    # Intentamos ver si acepta depósitos (si es un "Vault")
    code = await w3.eth.get_code(PROXY)
    if "f3" in code.hex(): # 'f3' es el opcode para RETURN
        print("✅ El Proxy tiene código operativo.")
    
    print(f"\n💡 CONCLUSIÓN: Si el owner es 0x000... y el Admin Slot es 0x000...,")
    print(f"   estamos ante un contrato que NADIE controla ahora mismo.")

if __name__ == "__main__":
    asyncio.run(simulate())
