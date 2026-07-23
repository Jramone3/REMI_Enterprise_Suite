from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
target = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')

print(f"📡 REMI: Buscando 'Paymasters' activos para el contrato...")

# Verificamos si el contrato tiene saldo propio para pagar su propio gas (Meta-tx)
balance_contrato = w3.eth.get_balance(target)
print(f"💰 Saldo del contrato: {w3.from_wei(balance_contrato, 'ether')} ETH")

if balance_contrato > 0:
    print("💡 El contrato TIENE fondos. Podríamos intentar una 'Meta-transacción' si el guardia lo permite.")
else:
    print("❌ El contrato está seco. Requiere gas externo obligatoriamente.")
