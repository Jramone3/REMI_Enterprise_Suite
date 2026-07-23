from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
wallet = w3.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

# Lista de contratos de tokens populares en Base
tokens = {
    'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    'USDT': '0xfde4C962512795Fe91e75f573602148b59623838',
    'DAI':  '0x50c5725949A6F0c72E6C45641f24029a21cFE8cf',
    'WETH': '0x4200000000000000000000000000000000000006'
}

print(f"🔎 GENY: Escaneando Bóvedas ERC-20 en Base para {wallet}...")

for nombre, contrato in tokens.items():
    # Selector balanceOf(address) = 70a08231
    data = "0x70a08231" + wallet[2:].lower().zfill(64)
    try:
        res = w3.eth.call({'to': w3.to_checksum_address(contrato), 'data': data})
        balance = int(res.hex(), 16)
        if balance > 0:
            # Ajuste de decimales (6 para USDC/USDT, 18 para el resto)
            dec = 6 if nombre in ['USDC', 'USDT'] else 18
            print(f"💰 ¡HALLAZGO! {nombre}: {balance / (10**dec)}")
        else:
            print(f"🔹 {nombre}: 0.0")
    except:
        print(f"❌ Error al consultar {nombre}")

