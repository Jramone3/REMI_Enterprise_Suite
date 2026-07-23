import time
from web3 import Web3

# Conexión a Base
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# TUS DATOS
mi_wallet = w3.to_checksum_address("0x96De980a766CCb10A19B6962587e2b61B650b372")
# Pega aquí tu llave privada (la que termina en 9de2)
private_key = "os.getenv("PRIVATE_KEY")" 

# Dirección de Orbiter
orbiter_maker = w3.to_checksum_address("0xe4EdB277e4122137966efc68615b3c5890d2979E")

# Mensaje de rescate
mensaje_hex = "0x6f726269746572900128c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172"

print(f"🚀 [REMI]: Iniciando secuencia de disparo final desde el búnker...")

try:
    nonce = w3.eth.get_transaction_count(mi_wallet)
    
    tx = {
        'nonce': nonce,
        'to': orbiter_maker,
        'value': 0,
        'gas': 40000, 
        'gasPrice': w3.eth.gas_price,
        'data': mensaje_hex,
        'chainId': 8453
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    
    # Intentamos enviar usando el atributo moderno, si falla usamos el antiguo
    raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
    
    tx_hash = w3.eth.send_raw_transaction(raw_tx)

    print(f"✅ ¡DISPARO EXITOSO!")
    print(f"📦 Hash del rescate: {tx_hash.hex()}")
    print("📡 Señal enviada. Si Orbiter tiene indexador activo, el gas llegará pronto.")

except Exception as e:
    print(f"❌ Error en el búnker: {e}")
