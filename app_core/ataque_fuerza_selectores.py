from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
proxy = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
# Probamos selectores sospechosos de tu lista
selectores = ['ac18de43', 'adc82ce6', 'd14faf2c', 'f3ae2415']

print("🚀 Probando bypass de Admin en funciones críticas...")
for s in selectores:
    try:
        # Intentamos llamar a la función con tu wallet como parámetro
        data = "0x" + s + "96De980a766CCb10A19B6962587e2b61B650b372".lower().zfill(64)
        w3.eth.call({'to': proxy, 'data': data})
        print(f"🔥 ¡SELECTOR {s} RESPONDIÓ! Posible punto de entrada.")
    except Exception as e:
        print(f"🔹 {s}: Acceso denegado.")
