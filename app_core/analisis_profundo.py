from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

proxy = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
tu_wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')
dueño = w3.to_checksum_address('0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7')
saldo_objetivo = w3.eth.get_balance(dueño)

# Selector + Wallet + Cantidad
data = "0xf3ae2415" + tu_wallet[2:].lower().zfill(64) + hex(saldo_objetivo)[2:].zfill(64)

print(f"🔬 Analizando comportamiento interno de f3ae2415...")

try:
    # Hacemos un call y vemos si el estado de los balances cambiaría
    # (Esto es una simulación avanzada)
    resultado = w3.eth.call({
        'to': proxy,
        'from': tu_wallet,
        'data': data
    })
    
    print(f"📡 Respuesta del contrato (Hex): {resultado.hex()}")
    if resultado.hex() == "" or resultado.hex() == "0x":
        print("⚠️  ALERTA: El contrato no devolvió confirmación. Podría ser una función vacía.")
    else:
        print("✅ El contrato devolvió datos. Hay lógica real detrás.")

except Exception as e:
    print(f"❌ Error técnico: {e}")
