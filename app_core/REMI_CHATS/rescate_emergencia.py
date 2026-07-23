from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# La llave de Hardhat que encontramos en tu grep
pk_hardhat = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
acct = w3.eth.account.from_key(pk_hardhat)

# Tu billetera real donde quieres el dinero
mi_wallet = "0x96De980a766CCb10A19B6962587e2b61B650b372"

print(f"🕵️ Recuperando desde: {acct.address}")

balance = w3.eth.get_balance(acct.address)
gas_price = w3.eth.gas_price
gas_limit = 21000
valor_a_enviar = balance - (gas_price * gas_limit)

if valor_a_enviar > 0:
    tx = {
        'nonce': w3.eth.get_transaction_count(acct.address),
        'to': mi_wallet,
        'value': valor_a_enviar,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': 8453 # Red Base
    }
    signed_tx = w3.eth.account.sign_transaction(tx, pk_hardhat)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"🚀 ¡DINERO ENVIADO! Hash: {tx_hash.hex()}")
else:
    print("❌ El saldo es insuficiente para pagar el gas o está en 0.")
