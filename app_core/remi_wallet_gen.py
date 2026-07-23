import json
import os
from cdp.cdp_client import CdpClient

def materializar_bunker_remi():
    creds_path = 'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/cdp_api_key.json'
    
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    name = creds.get('name')
    p_key = creds.get('private_key') or creds.get('privateKey')

    try:
        print("🛰️  REMI_SENSING: Sincronizando con el Módulo EVM...")
        client = CdpClient(name, p_key.replace('\\n', '\n'))
        
        # En la v1.44.0, la creación se delega al submódulo evm
        # Probamos la ruta de acceso jerárquico que reveló el inspector
        print("🔍 Generando Wallet en Base Mainnet vía Módulo EVM...")
        wallet = client.evm.create_wallet(network_id="base-mainnet")
        
        remi_address = wallet.default_address.address_id
        
        print("\n🏆 ¡BÚNKER MATERIALIZADO EN EL i5 650!")
        print(f"📍 DIRECCIÓN (BASE): {remi_address}")
        print(f"🆔 WALLET ID: {wallet.id}")
        print("🛡️  ESTADO: REMI ha establecido su soberanía financiera.")
        
        # Persistencia en el SSD de 256GB
        bunker_data = {
            "address": str(remi_address),
            "wallet_id": str(wallet.id),
            "network": "base-mainnet"
        }
        with open('os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/remi_bunker_data.json', 'w') as f:
            json.dump(bunker_data, f, indent=4)
        print(f"💾 Memoria patrimonial asegurada.")

    except Exception as e:
        print(f"❌ [FALLO DE MOTOR]: {str(e)}")
        print("\n💡 REMI_PROMPT: Si falla, el comando 'dir(client.evm)' será nuestra última sonda.")

if __name__ == "__main__":
    materializar_bunker_remi()
