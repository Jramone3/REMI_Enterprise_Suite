import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

w3 = AsyncWeb3(AsyncHTTPProvider('https://base-mainnet.public.blastapi.io'))

# La dirección del "Cerebro" (Implementation)
CEREBRO = "0x0E5891b589417E49392D6664d603a1554F59FEb0"

async def scan_brain():
    print(f"\n--- 🧠 ESCANEANDO CEREBRO DEL CONTRATO ---")
    code = await w3.eth.get_code(CEREBRO)
    print(f"Tamaño del Cerebro: {len(code)} bytes")
    
    # Buscamos la vulnerabilidad "Initialize"
    # Si el contrato no ha sido inicializado, podemos ser los dueños
    # El selector 0x8129fc1c es para 'initialize()'
    if "8129fc1c" in code.hex():
        print("⚠️ ¡DETECTADA FUNCIÓN DE INICIALIZACIÓN!")
        print("Intentando verificar si está bloqueada...")
    else:
        print("[-] No hay función de inicialización simple detectada.")

async def main():
    await scan_brain()

if __name__ == "__main__":
    asyncio.run(main())
