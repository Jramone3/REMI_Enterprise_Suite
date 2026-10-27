import requests
import json

def fetch_media(target_url):
    api_url = "http://localhost:9000/"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {"url": target_url}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"\n[Éxito] Estado de la respuesta: {status}")
            
            # Cobalt puede devolver un enlace directo ('url') o un selector ('picker' para múltiples calidades)
            if "url" in data:
                print(f"URL de descarga directa: {data.get('url')}")
            elif "picker" in data:
                print("Opciones disponibles (Picker):")
                for item in data.get("picker"):
                    print(f" - [{item.get('type')}] {item.get('url')}")
            else:
                print(json.dumps(data, indent=2))
        else:
            print(f"\n[Error] Código HTTP {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("\n[Error] No se pudo conectar con el contenedor de Cobalt. Asegúrate de que esté corriendo en http://localhost:9000")

if __name__ == "__main__":
    link = input("Introduce el enlace multimedia: ").strip()
    if link:
        fetch_media(link)
    else:
        print("No se proporcionó ningún enlace.")
