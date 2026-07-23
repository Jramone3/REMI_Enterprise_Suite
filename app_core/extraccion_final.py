from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

priv = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
pub = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
nodo_a = '0xB9073c07648a414B875874d7B8599dD2fAa171E8'

def disparar():
    print("🧨 REMI: Intento de extracción corregido...")
    try:
        balance = w3.eth.get_balance(pub)
        print(f"💰 Saldo en el búnker: {w3.from_wei(balance, 'ether')} ETH")
        
        gas_price = int(w3.eth.gas_price * 2) 
        gas_limit = 21000
        costo_gas = gas_price * gas_limit
        
        # Corregido: ahora la variable coincide
        monto_final = balance - costo_gas - w3.to_wei(0.00005, 'ether')

        if monto_final <= 0:
            print("❌ Saldo insuficiente para pagar el gas.")
            return

        tx = {
            'nonce': w3.eth.get_transaction_count(pub),
            'to': nodo_a,
            'value': monto_final,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': 8453
        }

        signed = w3.eth.account.sign_transaction(tx, priv)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"🚀 ¡TRANSACCIÓN ENVIADA! Hash: {tx_hash.hex()}")

    except Exception as e:
        print(f"⚠️ El sistema respondió: {e}")

if __name__ == "__main__":
    disparar()
