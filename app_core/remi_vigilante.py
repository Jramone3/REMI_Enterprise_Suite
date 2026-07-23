import time
import datetime
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
target = '0x96De980a766CCb10A19B6962587e2b61B650b372'
log_path = "os.path.expanduser("~/") + Escritorio/REMI_BLACKBOX/BITACORA_ROOT_SDA5.log"

print(f"🛡️ REMI: Sistema de Vigilancia Activo en i5 650")
print(f"📡 Escaneando IBAN Cripto: {target}")

def check():
    # Obtener saldo en Wei y convertir a Ether
    bal_wei = w3.eth.get_balance(target)
    saldo_actual = w3.from_wei(bal_wei, 'ether')
    
    # Preparar registro
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Escribir en consola
    print(f"💎 Saldo actual: {saldo_actual} ETH")
    
    # Guardar en la bitácora
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] SALDO: {saldo_actual} ETH\n")

while True:
    try:
        check()
        time.sleep(30)
    except Exception as e:
        print(f"Error en escaneo: {e}")
        time.sleep(10)
