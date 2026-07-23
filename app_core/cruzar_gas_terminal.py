import time
from web3 import Web3

# Conexiones
w3_base = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
w3_eth = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# Datos del Búnker
priv_key = 'os.getenv("PRIVATE_KEY")'
acct = w3_base.eth.account.from_key(priv_key)

# Dirección del "Maker" de Orbiter (El puente)
# Esta dirección recibe en Base y te envía en Mainnet automáticamente
ORBITER_MAKER_BASE = w3_base.to_checksum_address('0xe4edb277e4122137966efc68615b3c5890d2979e')

def ejecutar_puente():
    print(f"🚀 REMI: Iniciando cruce de gas desde el Búnker...")
    
    saldo_base = w3_base.eth.get_balance(acct.address)
    # Dejamos un margen pequeño para el gas de Base
    monto_a_enviar = saldo_base - w3_base.to_wei(0.0001, 'ether')
    
    if monto_a_enviar <= 0:
        print("❌ Error: No hay saldo suficiente en Base.")
        return

    tx = {
        'from': acct.address,
        'to': ORBITER_MAKER_BASE,
        'value': monto_a_enviar,
        'gas': 21000,
        'gasPrice': w3_base.eth.gas_price,
        'nonce': w3_base.eth.get_transaction_count(acct.address),
        'chainId': 8453 # Base
    }

    print(f"📦 Enviando {w3_base.from_wei(monto_a_enviar, 'ether')} ETH al puente...")
    signed = w3_base.eth.account.sign_transaction(tx, priv_key)
    tx_hash = w3_base.eth.send_raw_transaction(signed.raw_transaction)
    
    print(f"✅ ¡GAS EN CAMINO! Hash: {tx_hash.hex()}")
    print("⏳ Ahora el Radar de Mainnet detectará la llegada en unos minutos.")

if __name__ == "__main__":
    ejecutar_puente()
