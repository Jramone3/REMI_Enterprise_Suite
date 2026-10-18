import getpass
from web3 import Web3
import json
import sys

# Nodo de contingencia (Gateway público alternativo)
w3 = Web3(Web3.HTTPProvider("https://ethereum-rpc.publicnode.com"))
ORIGEN = "0xe4EdB277e4122137966EFC68615b3C5890d2979E"
# Dirección verificada de tu Wallet PC
DESTINO = "0x96De980a766CCb10A19B6962587e2b61B650b372"

try:
    pk_raw = getpass.getpass(f"\n[REMI] Introduce la llave para {ORIGEN}: ")
    pk = pk_raw.strip()
    if not pk.startswith('0x'): pk = '0x' + pk
    
    account = w3.eth.account.from_key(pk)
    balance = w3.eth.get_balance(account.address)
    
    # Cálculo manual de gas para evitar peticiones extra al nodo
    gas_price = w3.eth.gas_price
    gas_limit = 21000
    costo_gas = gas_price * gas_limit
    valor_enviar = balance - costo_gas

    if valor_enviar <= 0:
        print(f"❌ Error: Balance insuficiente para cubrir el gas.")
        sys.exit(1)

    tx = {
        'nonce': w3.eth.get_transaction_count(account.address),
        'to': DESTINO,
        'value': valor_enviar,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': 1
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"\n✅ MIGRACIÓN EXITOSA A WALLET PC: https://etherscan.io/tx/{tx_hash.hex()}")
    
    # Registro de éxito en la bitácora de SDA5
    with open('/home/ramon/REMI_CORE/patrimonio/log_exito.json', 'w') as f:
        json.dump({"hash": tx_hash.hex(), "status": "COMPLETADO"}, f)

except Exception as e:
    print(f"❌ Fallo en la matriz: {e}")
    sys.exit(1)
