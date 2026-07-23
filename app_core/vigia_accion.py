import time
from web3 import Web3

# Conexión a Polygon
w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))

# Coordenadas
nodo_b = '0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291'
wallet_pc = '0x96De980a766CCb10A19B6962587e2b61B650b372'
usdc_contract = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'

# ABI para balance
abi_balance = '[{"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]'
contract = w3.eth.contract(address=w3.to_checksum_address(usdc_contract), abi=abi_balance)

print(f"\n📡 RASTREADOR DE FLUJO ACTIVO")
print(f"1. Esperando entrada al Nodo B: {nodo_b[:8]}...")
print(f"2. Esperando salida hacia PC:   {wallet_pc[:8]}...")
print("-" * 55)

fase_entrada = False

while True:
    try:
        # 1. Monitorear Nodo B
        saldo_b = contract.functions.balanceOf(nodo_b).call() / 1e6
        
        # 2. Monitorear tu Wallet PC (solo para confirmar recepción)
        saldo_pc = contract.functions.balanceOf(wallet_pc).call() / 1e6

        if saldo_b > 0 and not fase_entrada:
            print(f"\n📥 [FASE 1]: ¡Botín detectado en Nodo B! (${saldo_b:.2f} USDC)")
            print("⏳ Esperando que el script 'Sifón' ejecute el reenvío...")
            fase_entrada = True

        if fase_entrada and saldo_b == 0:
            print(f"\n📤 [FASE 2]: El Nodo B se ha vaciado.")
            print(f"✅ [ÉXITO TOTAL]: Los fondos deberían estar en tu Wallet PC.")
            print(f"💰 Saldo actual en tu PC: ${saldo_pc:.2f} USDC")
            print("-" * 55)
            break
            
        if not fase_entrada:
            print(f"⏳ Escaneando... B: {saldo_b} | PC: {saldo_pc}", end="\r")
        else:
            print(f"🚀 Procesando traslado... B: {saldo_b} | PC: {saldo_pc}", end="\r")
            
    except Exception:
        pass
    time.sleep(3)
