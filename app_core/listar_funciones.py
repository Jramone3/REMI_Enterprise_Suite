import re
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
code = w3.eth.get_code(w3.to_checksum_address('0x22e7170c305298fe6a0132cbad6e3c0691b016de')).hex()

# Buscamos el patrón PUSH4 (63) seguido de 4 bytes, que son los selectores de funciones
selectors = re.findall(r'63([0-9a-f]{8})', code)
unique_selectors = sorted(list(set(selectors)))

print(f"\n🕵️‍♂️ CATÁLOGO DE FUNCIONES DETECTADO ({len(unique_selectors)} funciones):")
for s in unique_selectors:
    # Marcar selectores conocidos de transferencia o retiro
    note = ""
    if s == "a9059cbb": note = " <- TRANSFER (ERC20)"
    if s == "23b872dd": note = " <- TRANSFERFROM"
    if s == "8da5cb5b": note = " <- OWNER()"
    print(f"🔹 Selector: {s} {note}")
