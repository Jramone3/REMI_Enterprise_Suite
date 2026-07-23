from web3 import Web3

# Usamos el RPC oficial de Base directamente
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# COORDENADAS
LLAVE_ORIGEN = '0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172'
DIR_ORIGEN = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
NODO_B = '0x79D79B1cE83e32f35798ad1A3C8DBB101B6F3291'

def mandar_gas():
    print(f"🚀 REMI: Forzando extracción segura...")
    
    # Verificamos saldo real antes de intentar nada
    balance = w3.eth.get_balance(DIR_ORIGEN)
    print(f"💰 Saldo real en Base: {w3.from_wei(balance, 'ether')} ETH")
    
    if balance == 0:
        print("❌ Error: La red dice que esta cuenta está vacía. Revisa la red.")
        return

    # Vamos a enviar un monto FIJO pequeño para que no falle por cálculo de comisiones
    # 0.003 ETH es suficiente y seguro
    monto_fijo = w3.to_wei(0.003, 'ether') 
    
    nonce = w3.eth.get_transaction_count(DIR_ORIGEN)
    gas_price = w3.eth.gas_price

    tx = {
        'nonce': nonce,
        'to': NODO_B,
        'value': monto_fijo,
        'gas': 21000,
        'gasPrice': gas_price,
        'chainId': 8453
    }

    try:
        signed = w3.eth.account.sign_transaction(tx, LLAVE_ORIGEN)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction) 
        print(f"✅ ¡MISIÓN CUMPLIDA!")
        print(f"🔗 Hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    mandar_gas()
