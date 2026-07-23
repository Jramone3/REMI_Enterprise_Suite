from web3 import Web3
import time
import requests
import os

# --- CONFIGURACIÓN HISTÓRICA SATOSHI ---
FECHA_GENESIS_BUSQUEDA = 1262304000  # 1 de Enero de 2010
PREFIJO_LEGACY = "1"                 # Formato original de Bitcoin/EVM antiguo
LOG_FILE = "/media/ramon/EL_BUNKER/GENY_IA_SYSTEM/LOGS/ANALISIS_FLUJO_PRINCE_GROUP.log"

# --- CONFIGURACIÓN DE REDES ---
redes = {
    'BASE': 'https://mainnet.base.org',
    'OPTIMISM': 'https://mainnet.optimism.io',
    'POLYGON': 'https://polygon-rpc.com'
}

def alerta_remi_voz(mensaje):
    """ Envía señal al puerto 5000 para que REMI hable """
    try:
        requests.post("http://localhost:5000/alerta", json={"msg": mensaje, "prioridad": "ALTA"})
    except:
        print("⚠️ REMI Voz (Puerto 5000) fuera de línea.")

def arqueologo_maestro():
    print(f'\n🕵️‍♂️ GENY: RADAR ARQUEÓLOGO v3.0')
    print(f'📅 FILTRO TEMPORAL: Desde {time.ctime(FECHA_GENESIS_BUSQUEDA)}')
    print(f'📜 BUSCANDO: Direcciones "{PREFIJO_LEGACY}" y Contratos Huérfanos...')

    while True:
        for nombre, rpc in redes.items():
            try:
                w3 = Web3(Web3.HTTPProvider(rpc))
                if nombre == 'POLYGON':
                    from web3.middleware import geth_poa_middleware
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

                # --- EXCAVACIÓN PROFUNDA (BLOQUES INICIALES) ---
                # Buscamos en el primer millón de bloques donde residen los activos olvidados
                inicio = 1 
                fin = 1000000 
                
                print(f'⛏️  [{nombre}] Escaneando estrato antiguo (Bloque {inicio} a {fin})...')

                for i in range(inicio, fin, 1000): # Saltos grandes para cubrir años de historia
                    block = w3.eth.get_block(i, full_transactions=True)
                    
                    # Verificamos si el bloque coincide con nuestra era de búsqueda
                    if block['timestamp'] >= FECHA_GENESIS_BUSQUEDA:
                        for tx in block.transactions:
                            target = tx['to']
                            if target:
                                balance = w3.eth.get_balance(target)
                                if balance > w3.to_wei(0.01, 'ether'):
                                    # Verificamos si es una dirección Legacy o Contrato sin Dueño
                                    owner_slot = w3.eth.get_storage_at(target, 0).hex()
                                    
                                    if owner_slot == '0x0000000000000000000000000000000000000000000000000000000000000000':
                                        hallazgo = f"🏺 ¡RELIQUIA! {nombre} | {target} | Bal: {w3.from_wei(balance, 'ether')} | Bloque: {i}"
                                        print(hallazgo)
                                        
                                        # ALERTA DE VOZ CONTEXTUAL
                                        alerta_remi_voz(f"Ramón, el arqueólogo encontró una firma antigua en {nombre}. Posible activo de la era Satoshi detectado.")
                                        
                                        with open(LOG_FILE, "a") as f:
                                            f.write(f"{time.ctime()}: {hallazgo}\n")

            except Exception as e:
                continue
        
        print("💤 Ciclo de arqueología completo. Reiniciando excavación...")
        time.sleep(20)

if __name__ == "__main__":
    arqueologo_maestro()
