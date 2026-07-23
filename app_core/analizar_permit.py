from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
target = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')

print(f"🔬 REMI: Buscando soporte 'Gasless' (Permit) en el objetivo...")

# Buscamos selectores de EIP-2612 o EIP-712
# permit(address,address,uint256,uint256,uint8,bytes32,bytes32) -> 0xd505accf
# DOMAIN_SEPARATOR() -> 0x3644e511
selectores = {
    'PERMIT_SELECTOR': '0xd505accf',
    'DOMAIN_SEPARATOR': '0x3644e511',
    'NONCES_SELECTOR': '0x7ecebe00'
}

code = w3.eth.get_code(target).hex()

found = False
for nombre, sig in selectores.items():
    if sig in code:
        print(f"✅ ¡GOLPE DE SUERTE! Detectado soporte para: {nombre}")
        found = True

if not found:
    print("❌ El contrato no soporta firmas 'Sin Gas'. Requiere gas tradicional.")
