import json
from cdp.cdp_client import CdpClient

def escanear_nervios_evm():
    creds_path = 'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/cdp_api_key.json'
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    name = creds.get('name')
    p_key = creds.get('private_key') or creds.get('privateKey')

    try:
        client = CdpClient(name, p_key.replace('\\n', '\n'))
        print("\n🔎 --- ESCANEO DE MÓDULO EVM (REMI_SENSING) ---")
        
        # Analizamos el objeto evm que detectamos antes
        metodos_evm = [m for m in dir(client.evm) if not m.startswith('_')]
        print(f"Capacidades en 'client.evm': {metodos_evm}")

        # Buscamos si existe un import global para Wallet que no hayamos visto
        try:
            from cdp.wallet import Wallet
            print("✅ Clase 'cdp.wallet.Wallet' detectada mediante importación directa.")
            print(f"Métodos en Wallet: {[m for m in dir(Wallet) if not m.startswith('_')]}")
        except ImportError:
            print("❌ No se encontró 'cdp.wallet' como módulo independiente.")

    except Exception as e:
        print(f"❌ Error en el escaneo: {e}")

if __name__ == "__main__":
    escanear_nervios_evm()
