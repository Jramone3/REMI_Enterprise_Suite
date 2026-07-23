import requests
from bs4 import BeautifulSoup

def scout_info(url):
    print(f"👁️ [REMI-SCOUT]: Observando objetivo: {url}")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer texto principal
        texto = soup.get_text(separator=' ', strip=True)[:5000] # Limite para no saturar memoria
        return texto
    except Exception as e:
        return f"Error en la visión: {e}"
