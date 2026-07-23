from web3 import Web3

# Probamos en Base (donde el gas es regalado)
w3_base = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
target = w3_base.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')

print(f"🛰️ GENY: Buscando el objetivo 0x3AC0... en la red BASE")

try:
    balance = w3_base.eth.get_balance(target)
    code = w3_base.eth.get_code(target)
    
    if len(code) > 0:
        print(f"🔥 ¡OBJETIVO LOCALIZADO EN BASE!")
        print(f"💰 Saldo en Base: {w3_base.from_wei(balance, 'ether')} ETH")
    else:
        print("📭 El contrato no existe en Base. El botín es exclusivo de Ethereum Mainnet.")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
