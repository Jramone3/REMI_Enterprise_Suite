import requests

wallet = '0x96De980a766CCb10A19B6962587e2b61B650b372'
redes = {
    "Base": "https://base.blockscout.com/api",
    "Polygon": "https://polygon.blockscout.com/api",
    "Optimism": "https://optimism.blockscout.com/api"
}

print(f"🕵️‍♂️ REMI: Escaneando almacenes de munición para {wallet}...")

for nombre, url in redes.items():
    try:
        r = requests.get(f"{url}?module=account&action=balance&address={wallet}").json()
        bal = int(r['result']) / 10**18
        print(f"📡 Red {nombre}: {bal:.6f} ETH/Tokens")
    except:
        print(f"❌ Red {nombre}: Error de conexión.")
