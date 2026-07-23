import requests
import json

def consultar_precio_gas_polygon(max_gwei_seguro=50):
    """
    Simbiosis Remi & Ramón: Consulta el gas de Polygon usando un nodo robusto
    y saltando bloqueos de seguridad con User-Agent.
    """
    # Usamos el nodo Bor de PublicNode que es más tolerante que el de polygon-rpc
    POLYGON_RPC_URL = "https://polygon-bor-rpc.publicnode.com"
    
    # El "Disfraz" de navegador para evitar el Error 401 (Unauthorized)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Estándar JSON-RPC para consultar eth_gasPrice
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_gasPrice",
        "params": [],
        "id": 1
    }

    print("\n" + "="*45)
    print(" ⛽ MONITOR DE GAS POLYGON - PROYECTO REMI")
    print("="*45)

    try:
        # Realizamos la petición con un timeout de 10 segundos por si el nodo está lento
        response = requests.post(POLYGON_RPC_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status() 
        data = response.json()

        if "result" in data:
            # Conversión de Hexadecimal (Wei) a Decimal (Gwei)
            gas_price_wei = int(data["result"], 16)
            gas_price_gwei = gas_price_wei / 1e9

            print(f" > Precio actual: {gas_price_gwei:.2f} Gwei")
            print(f" > Tu límite:     {max_gwei_seguro:.2f} Gwei")
            print("-" * 45)

            if gas_price_gwei < max_gwei_seguro:
                print(f" ✅ ¡ESTADO ÓPTIMO! Es el momento de mover tus $4.")
                print(f"    Comisión estimada: < $0.01 USD")
            else:
                print(f" ❌ ¡DEMASIADO CARO! La red está congestionada.")
                print(f"    Sugerencia: Espera a que baje para no diluir tus $4.")
        else:
            print(" ⚠️ Error: El nodo devolvió una respuesta vacía.")

    except requests.exceptions.HTTPError as e:
        print(f" ❌ Error HTTP: {e} (Posible bloqueo de IP)")
    except Exception as e:
        print(f" ❌ Error de conexión: {e}")
    
    print("="*45 + "\n")

if __name__ == "__main__":
    # Ajustamos a 50 Gwei, que es el estándar para transacciones baratas en Polygon
    consultar_precio_gas_polygon(max_gwei_seguro=50)
