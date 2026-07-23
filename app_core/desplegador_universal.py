import subprocess
import time
import hashlib
import os
from web3 import Web3

# CONFIGURACIÓN
PRIV_KEY = '9bb4285c9609feee26c70d2045fe8d72cd121ef985045fd8d9cfa807c7779de2' 
CONTRACT_FILE = 'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/contracts/RNC_Notary_Immunefi.sol'
RUTA_HALLAZGOS = 'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/'
RED = {"Base": "https://mainnet.base.org"}

def calcular_hash(archivo):
    sha256_hash = hashlib.sha256()
    with open(archivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def compilar_contrato():
    print("🔨 Compilando contrato...")
    res = subprocess.run(['solc', '--bin', '--optimize', CONTRACT_FILE], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Error: {res.stderr}")
        exit()
    return res.stdout.split('Binary:')[1].strip()

def desplegar_y_registrar(archivo_a_auditar):
    h = calcular_hash(archivo_a_auditar)
    print(f"🔍 Hash generado para {archivo_a_auditar}: {h}")
    
    bytecode = compilar_contrato()
    w3 = Web3(Web3.HTTPProvider(RED["Base"]))
    acct = w3.eth.account.from_key(PRIV_KEY)
    
    print(f"🚀 Desplegando contrato con registro de integridad...")
    tx = {
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 1500000,
        'gasPrice': w3.eth.gas_price,
        'data': '0x' + bytecode + h, # Registramos el hash en el despliegue
        'chainId': w3.eth.chain_id
    }
    
    signed = w3.eth.account.sign_transaction(tx, PRIV_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"✅ Integridad registrada en Blockchain | Tx: {tx_hash.hex()}")

def respaldar_en_nube():
    print("☁️ Iniciando respaldo eficiente en Drive...")
    # --copy-links resuelve el problema de los symlinks
    # --exclude 'node_modules/**' evita copiar archivos innecesarios que causan errores
    subprocess.run([
        'rclone', 'copy', RUTA_HALLAZGOS, 'REMI_DRIVE:REMI_Patrimonial_Core', 
        '--copy-links', 
        '--exclude', 'node_modules/**', 
        '--exclude', '.git/**'
    ], check=True)
    print("✅ Respaldo completo.")

if __name__ == "__main__":
    # Auditoría de integridad y registro en Blockchain
    archivo_objetivo = os.path.join(RUTA_HALLAZGOS, "index_patrimonial.json")
    desplegar_y_registrar(archivo_objetivo)
    
    # El respaldo se ha desactivado temporalmente para evitar errores de cuota (Rate Limit)
    # Para ejecutarlo manualmente sin saturar la API:
    # rclone copy os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/REMI_CHATS/ REMI_DRIVE:REMI_Patrimonial_Core --transfers 1 --checkers 1
    # respaldar_en_nube()
