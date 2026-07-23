import requests

def revisar(nombre, direccion):
    url = f"https://api.polygonscan.com/api?module=account&action=txlist&address={direccion}&startblock=0&endblock=99999999&sort=desc&apikey=YourApiKeyToken"
    try:
        r = requests.get(url).json()
        print(f"\n--- {nombre} ({direccion[:10]}...) ---")
        if r['result'] and len(r['result']) > 0:
            for tx in r['result'][:3]: # Miramos las últimas 3
                valor = float(tx['value']) / 10**18
                tipo = "ENTRADA" if tx['to'].lower() == direccion.lower() else "SALIDA"
                print(f"Monto: {valor:.4f} POL | Tipo: {tipo} | Fecha: {tx['timeStamp']}")
        else:
            print("Sin movimientos recientes en Polygon.")
    except:
        print(f"Error conectando con el explorador para {nombre}")

revisar("BILLETERA PC", "0x96De980a766CCb10A19B6962587e2b61B650b372")
revisar("NODO B", "0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291")
