import json
from cdp.cdp_client import CdpClient

def inspeccionar_conciencia():
    creds_path = 'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/cdp_api_key.json'
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    name = creds.get('name')
    p_key = creds.get('private_key') or creds.get('privateKey')

    try:
        client = CdpClient(name, p_key.replace('\\n', '\n'))
        print("\n🔎 --- MAPA DE CAPACIDADES DE REMI_SENSING ---")
        
        # Listamos todos los métodos del cliente que no sean internos
        metodos = [m for m in dir(client) if not m.startswith('_')]
        
        print(f"Atributos detectados en CdpClient: {metodos}")
        
        # Buscamos específicamente cualquier rastro de 'wallet' o 'create'
        pistas = [m for m in metodos if 'wallet' in m.lower() or 'create' in m.lower()]
        print(f"\n💡 PISTAS ENCONTRADAS: {pistas}")

    except Exception as e:
        print(f"❌ Error en la inspección: {e}")

if __name__ == "__main__":
    inspeccionar_conciencia()
