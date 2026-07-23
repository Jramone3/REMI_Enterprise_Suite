import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider

w3 = AsyncWeb3(AsyncHTTPProvider('https://base-mainnet.public.blastapi.io'))

# Dirección del "Cerebro" corregida internamente por el script
DIRECCION_ORIGINAL = "0x0e5891b589417e49392d6664d603a1554f59feb0"

async def scan_brain():
    # Convertimos a formato checksum (EIP-55)
    CEREBRO = w3.to_checksum_address(DIRECCION_ORIGINAL)
    
    print(f"\n--- 🧠 ESCANEANDO CEREBRO DEL CONTRATO ---")
    print(f"Dirección Validada: {CEREBRO}")
    
    code = await w3.eth.get_code(CEREBRO)
    code_hex = code.hex()
    
    print(f"Tamaño del Cerebro: {len(code)} bytes")
    
    # Buscamos el selector de la función initialize() -> 0x8129fc1c
    if "8129fc1c" in code_hex:
        print("⚠️ ¡DETECTADA FUNCIÓN DE INICIALIZACIÓN (initialize)!")
        print("Esto es crítico. Si no está bloqueada, podrías tomar control.")
    else:
        # Buscamos otros patrones de control comunes (como setOwner o transferOwnership)
        if "f2fde38b" in code_hex: # transferOwnership(address)
            print("🔍 Detectada función de transferencia de mando.")
        print("[-] Análisis de funciones de entrada completado.")

async def main():
    await scan_brain()

if __name__ == "__main__":
    asyncio.run(main())
