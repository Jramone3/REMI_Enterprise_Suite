from web3 import Web3

# Usamos un RPC robusto para evitar fallos de red
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
target = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
admin_slot = '0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103'

print(f"🕵️‍♂️ REMI: Investigando Jerarquía en Ethereum para {target}...")

try:
    # Leer el administrador del contrato
    admin_data = w3.eth.get_storage_at(target, admin_slot)
    admin_address = f"0x{admin_data.hex()[-40:]}"
    print(f"👑 ADMIN DETECTADO: {admin_address}")
    
    # Consultar el botín de 3.78 ETH
    owner_addr = '0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7'
    owner_balance = w3.eth.get_balance(owner_addr)
    print(f"💰 Saldo del Dueño Corporativo: {w3.from_wei(owner_balance, 'ether')} ETH")
except Exception as e:
    print(f"❌ Error en el escaneo: {e}")
