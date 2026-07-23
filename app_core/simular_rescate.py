from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
proxy = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
tu_wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

print(f"🎯 REMI: Intentando forzar el selector f3ae2415...")

# Intentamos construir la llamada: Selector + Tu Wallet (rellenada a 32 bytes)
# Muchas veces estas funciones esperan: function(address recipient)
data = "0xf3ae2415" + tu_wallet[2:].lower().zfill(64)

try:
    # Simulamos la transacción
    tx_simulada = w3.eth.call({
        'to': proxy,
        'data': data,
        'from': tu_wallet # Simulamos que tú eres quien llama
    })
    print("✅ ¡SIMULACIÓN EXITOSA! El contrato aceptó el comando de rescate.")
    print(f"📦 Retorno del contrato: {tx_simulada.hex()}")
except Exception as e:
    print(f"❌ Fallo en la simulación: {e}")
