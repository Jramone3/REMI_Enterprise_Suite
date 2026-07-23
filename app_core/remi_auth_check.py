import json
import os
import cdp

def intentar_conexion():
    creds_path = 'os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/cdp_api_key.json'
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    name = creds.get('name')
    p_key = creds.get('private_key') or creds.get('privateKey')

    print(f"🛰️  REMI_SENSING: Iniciando secuencia de acople para {name[:10]}...")

    # INTENTO A: Métodos estáticos del paquete (Versión Agente)
    try:
        from cdp import CdpClient
        # Intentamos configuración global si existe el método oculto
        cdp.cdp_client.CdpClient.configure(name, p_key)
        print("✅ [SINAPSIS A]: Configuración global exitosa.")
        return
    except: pass

    # INTENTO B: Instanciación posicional (Sin nombres de argumentos)
    try:
        from cdp import CdpClient
        client = CdpClient(name, p_key)
        print("✅ [SINAPSIS B]: Cliente instanciado por posición.")
        return
    except Exception as e:
        print(f"➖ Intento B fallido: {e}")

    # INTENTO C: Uso de la sub-librería de autenticación directa
    try:
        from cdp.auth import ApiKey
        key = ApiKey(name, p_key)
        print("✅ [SINAPSIS C]: Objeto ApiKey creado con éxito.")
        return
    except Exception as e:
        print(f"❌ [BLOQUEO]: Todos los protocolos de conexión fallaron: {e}")

if __name__ == "__main__":
    intentar_conexion()
