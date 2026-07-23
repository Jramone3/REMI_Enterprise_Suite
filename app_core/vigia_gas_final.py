from web3 import Web3
import time
import sys

# Conexiones con timeout para que no se cuelgue si falla internet
w3_eth = Web3(Web3.HTTPProvider('https://eth.llamarpc.com', request_kwargs={'timeout': 10}))
w3_poly = Web3(Web3.HTTPProvider('https://1rpc.io/matic', request_kwargs={'timeout': 10}))
w3_base = Web3(Web3.HTTPProvider('https://mainnet.base.org', request_kwargs={'timeout': 10}))

wallets = {
    "Personal": "0x96De980a766CCb10A19B6962587e2b61B650b372",
    "Gatillo A": "0xB9073c07648a414B875874d7B8599dD2fAa171E8",
    "Fantasma Real": "0x42D1006311d390c3905E2B19e0884349bc31aDE6"
}

print(f"\n📡 MONITOR INTEGRAL ACTIVO")
print("-" * 65)

while True:
    try:
        reporte = []
        for nombre, addr in wallets.items():
            eth = w3_eth.from_wei(w3_eth.eth.get_balance(addr), 'ether')
            pol = w3_poly.from_wei(w3_poly.eth.get_balance(addr), 'ether')
            base = w3_base.from_wei(w3_base.eth.get_balance(addr), 'ether')
            
            # Si hay balance significativo en cualquier red
            if eth > 0.0001 or pol > 0.05 or base > 0.0001:
                print(f"\n\n⛽ ¡GAS DETECTADO EN {nombre.upper()}!")
                print(f"   ADDR: {addr}")
                print(f"   ETH: {eth:.6f} | POL: {pol:.6f} | BASE-ETH: {base:.6f}")
                print("-" * 65)
                # Sonido de alerta (si la terminal lo soporta)
                sys.stdout.write('\a')
                sys.stdout.flush()
            
            reporte.append(f"{nombre[:4]}: E:{float(eth):.4f} P:{float(pol):.1f} B:{float(base):.4f}")
        
        # Imprimir progreso en una sola línea que se actualiza
        print(f"⏳ {' | '.join(reporte)}", end="\r")
        
    except Exception as e:
        # En caso de error de conexión, esperamos y seguimos
        pass
    
    time.sleep(10)
