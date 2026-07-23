import os
from web3 import Web3

# Usamos el nodo que nos dio la victoria
w3 = Web3(Web3.HTTPProvider('https://base.llamarpc.com'))

nodo_a = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'
bunker = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'

def auditoria():
    print("🔎 REMI: Realizando auditoría de post-extracción...")
    
    bal_bunker = w3.eth.get_balance(bunker)
    bal_nodo_a = w3.eth.get_balance(nodo_a)
    
    print(f"🏦 Saldo en Búnker: {w3.from_wei(bal_bunker, 'ether')} ETH")
    print(f"🚀 Saldo en Nodo A: {w3.from_wei(bal_nodo_a, 'ether')} ETH")
    
    if bal_bunker == 0 and bal_nodo_a > 0:
        print("✅ ÉXITO TOTAL: El búnker está vacío y el Nodo A está cargado.")
        # Borrar rastros de los scripts anteriores
        archivos_a_borrar = [
            'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/reparto_bunker.py',
            'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/salto_directo_pol_v2.py'
        ]
        for f in archivos_a_borrar:
            if os.path.exists(f):
                os.remove(f)
                print(f"🧹 Archivo {f} eliminado.")
    else:
        print("⏳ La transacción aún se está procesando en el bloque. Espera 1 minuto.")

if __name__ == "__main__":
    auditoria()
