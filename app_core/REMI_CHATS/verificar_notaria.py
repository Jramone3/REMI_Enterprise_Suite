from web3 import Web3

# Vamos a probar la conexión a Polygon usando un nodo público alternativo (sin clave)
# Usaremos 'polygon-pokt.nodies.app' que es un endpoint público muy estable
rpc_url = "https://polygon-pokt.nodies.app"
w3 = Web3(Web3.HTTPProvider(rpc_url))

contract_address = "0x42D1006311d390c3905E2B19e0884349bc31aDE6"

# Bytecode para verificar si hay código en la dirección
code = w3.eth.get_code(contract_address)

if code != b'\x00':
    print(f"✅ ¡ÉXITO! El contrato {contract_address} existe en Polygon.")
    # Ahora intentamos leer el owner
    # Usamos un ABI mínimo para llamar a 'owner()'
    abi = [{"constant":True,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"}]
    contract = w3.eth.contract(address=contract_address, abi=abi)
    print(f"👑 Owner detectado: {contract.functions.owner().call()}")
else:
    print(f"❌ Error: El contrato {contract_address} no tiene código en esta red.")
