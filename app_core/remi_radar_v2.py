import time
from web3 import Web3

# Redes de alta intensidad
REDES = {
    'Ethereum': 'https://ethereum.publicnode.com',
    'Polygon': 'https://polygon-rpc.com',
    'Base': 'https://mainnet.base.org',
    'Arbitrum': 'https://arb1.arbitrum.io/rpc',
    'Optimism': 'https://mainnet.optimism.io'
}

# Firmas de funciones de "Puerta Abierta"
SELECTORES_CRITICOS = {
    '3659cfe6': 'upgradeTo()',
    '8129fc1c': 'initialize()',
    '5fd89cfa': 'migrate()',
    '1308de7c': 'transferOwnership()'
}

def scan_target(nombre_red, rpc, address):
    try:
        # Timeout extendido para que Tor no corte la conexión
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 30}))
        addr = w3.to_checksum_address(address)
        
        # 1. Verificación de "Sangre" (Saldo)
        balance = w3.eth.get_balance(addr)
        eth = w3.from_wei(balance, 'ether')
        
        if balance > 0:
            # 2. Verificación de "ADN" (Código del Contrato)
            codigo = w3.eth.get_code(addr).hex()
            
            print(f"\n🎯 [DETECTADO] Red: {nombre_red} | Addr: {address}")
            print(f"💰 Saldo: {eth:.6f} ETH/Native")
            
            # 3. Búsqueda de Vulnerabilidades
            encontradas = []
            for sel, func in SELECTORES_CRITICOS.items():
                if sel in codigo:
                    encontradas.append(func)
            
            if encontradas:
                print(f"🚨 ALERTA: Funciones críticas halladas: {', '.join(encontradas)}")
                print(f"📝 Nota: Este contrato es un Proxy activo y vulnerable.")
            else:
                print("🔒 Código sólido o funciones ocultas.")
                
    except Exception:
        pass

if __name__ == "__main__":
    print("🕵️‍♂️ REMI: Radar de Búsqueda y Detección V2 activado.")
    print("🌐 Operando tras el túnel de Tor (Lelystad)...")
    
    # Aquí pondremos la lista de nuevas direcciones que vayamos encontrando
    # Por ahora, puedes probar con una lista de prueba o dejarlo listo para entrada manual
    # --- LISTA DE CAZA ACTUALIZADA ---
    targets = [
        '0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf', # El Proxy (vigilancia permanente)
        '0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7', # El Dueño anterior (por si reincide)
        '0xe4EdB277e4122137966EFC68615b3C5890d2979E', # Nodo de paso detectado
        '0x7b5ae5e48ff99239775f0a38f328f4160408544a'  # Ejemplo de contrato activo en Base
    ]
    # --------------------------------
    
    if not targets:
        print("⚠️ No hay objetivos en la lista. Agrega direcciones en el script para iniciar.")
    else:
        for t in targets:
            for nombre, rpc in REDES.items():
                scan_target(nombre, rpc, t)
