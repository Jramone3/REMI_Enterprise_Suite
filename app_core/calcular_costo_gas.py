from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

proxy = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
tu_wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')
dueño = w3.to_checksum_address('0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7')
saldo_wei = w3.eth.get_balance(dueño)

data_full = "0xf3ae2415" + tu_wallet[2:].lower().zfill(64) + hex(saldo_wei)[2:].zfill(64)

try:
    gas_estimate = w3.eth.estimate_gas({
        'to': proxy,
        'from': tu_wallet,
        'data': data_full
    })
    gas_price = w3.eth.gas_price
    costo_total_eth = w3.from_wei(gas_estimate * gas_price, 'ether')
    print(f"\n⛽ ESTIMACIÓN DE GAS:")
    print(f"🔹 Unidades de Gas: {gas_estimate}")
    print(f"🔹 Costo Total Estimado: {costo_total_eth} ETH")
    print(f"🔹 En USD (aprox): ${float(costo_total_eth) * 2090:.2f}")
except Exception as e:
    print(f"❌ No se pudo estimar: {e}")
