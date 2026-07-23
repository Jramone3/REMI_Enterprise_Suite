import time
from web3 import Web3

# Configuración de Red (Polygon para rescate)
rpc_url = "https://polygon.llamarpc.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Cuentas varadas bajo custodia
cuentas_objetivo = [
    "0x04DBc19CB0e8E12bbDD7f43062B6B233c4332bDA",
    "0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291"
]

def optimizar_rescate():
    print("🚀 [REMI]: Iniciando optimizador de gas para activos varados...")
    gas_price = w3.eth.gas_price
    
    for cuenta in cuentas_objetivo:
        balance_pol = w3.from_wei(w3.eth.get_balance(cuenta), 'ether')
        print(f"\n--- Auditoría: {cuenta} ---")
        print(f"Balance actual de POL: {balance_pol} MATIC")
        
        # Cálculo estimado de gas para una transferencia simple
        est_gas = 21000 * gas_price
        costo_pol = w3.from_wei(est_gas, 'ether')
        print(f"Costo estimado de transacción: {costo_pol} POL")
        
        if balance_pol < costo_pol:
            faltante = costo_pol - balance_pol
            print(f"⚠️ ESTADO: VARADO. Requiere inyección mínima de: {faltante + 0.001:.6f} POL")
        else:
            print("✅ ESTADO: LISTO PARA EXTRACCIÓN.")

if __name__ == "__main__":
    optimizar_rescate()
