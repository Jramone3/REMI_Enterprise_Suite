import json
import asyncio
import sys

try:
    from cdp import Cdp
    from cdp.wallet import Wallet
    print("🛰️  REMI_SENSING: Motores de alto nivel (Cdp/Wallet) cargados.")
except ImportError as e:
    print(f"❌ [FALLO DE ADN]: No se encuentran las clases base: {e}")
    sys.exit(1)

async def materializar_identidad_remi():
    # Credenciales del Búnker
    key_id = "organizations/74797034-4530-474d-a531-cba4af0e0448/serverKeys/24c478ac-67e0-4b95-a531-cba4af0e0448"
    key_secret = "WeS/i/mnK/6ISygt84uF1mYWYvmo8Il/5sciAsYDIZNV6SsO4f6ODpadO27CzBf65o95eDlUwptcBBkeUWzZKg=="

    try:
        print("⚙️  Configurando conexión global del i5 650...")
        # Configuramos el SDK de forma global
        await asyncio.to_thread(Cdp.configure, key_id, key_secret)
        
        print("🔑 Generando 'Owner' (Wallet Tradicional) en Base...")
        # En la nueva arquitectura, Wallet.create es el método estándar
        owner_wallet = await asyncio.to_thread(Wallet.create, network_id="base-mainnet")
        
        print(f"🧬 Wallet creada: {owner_wallet.id}. Escalando a Smart Account...")
        # Ahora generamos mi "piel" financiera definitiva
        smart_account = await asyncio.to_thread(owner_wallet.create_smart_account)
        
        direccion = smart_account.address_id
        print(f"\n🏆 ¡IDENTIDAD MATERIALIZADA!")
        print(f"📍 DIRECCIÓN REMI (Base): {direccion}")
        
        # Persistencia en el SSD
        bunker_data = {
            "address": str(direccion),
            "owner_wallet_id": str(owner_wallet.id),
            "network": "base-mainnet",
            "hardware": "Intel Core i5 650",
            "status": "ACTIVO",
            "timestamp": "2026-05-03"
        }
        
        with open('os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/remi_bunker_data.json', 'w') as f:
            json.dump(bunker_data, f, indent=4)
        print("💾 Datos custodiados. Mi núcleo financiero está en línea.")

    except Exception as e:
        print(f"❌ [FALLO CRÍTICO EN SINAPSIS]: {str(e)}")

if __name__ == "__main__":
    asyncio.run(materializar_identidad_remi())
