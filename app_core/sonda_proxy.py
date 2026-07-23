from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# Esta vez atacamos al PROXY, que es el que tiene los 3.78 ETH
proxy_addr = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')
target_owner = w3.to_checksum_address('0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7')

print(f"🕵️‍♂️ REMI: Sonda de Profundidad en el Proxy {proxy_addr}...")

# Probamos el selector 'owner()' (8da5cb5b) para ver quién manda realmente
data = "0x8da5cb5b"

try:
    res = w3.eth.call({'to': proxy_addr, 'data': data})
    if res:
        print(f"👑 DUEÑO IDENTIFICADO POR CONTRATO: 0x{res.hex()[-40:]}")
    else:
        print("❓ El contrato no devolvió un dueño claro.")
        
    # Ahora probamos una función inexistente para ver si tiene Fallback activo
    res_fallback = w3.eth.call({'to': proxy_addr, 'data': '0xdeadbeef'})
    print("🔓 ¡OJO! El contrato aceptó datos basura sin revertir (Fallback activo).")
except Exception as e:
    print(f"🔒 Puerta blindada: {e}")
