from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# Aplicando Checksum para evitar el error de Web3.py
logic_addr = w3.to_checksum_address('0x22e7170c305298fe6a0132cbad6e3c0691b016de')
target_owner = w3.to_checksum_address('0x0125aeb5fF473De23ab72454B2bbC45613Ff3bd7')

print(f"🕵️‍♂️ REMI: Verificando permisos de la Lógica sobre el Dueño...")

# Selector dd62ed3e: allowance(owner, spender)
# Preparamos los parámetros: 32 bytes para el dueño, 32 bytes para la lógica
params = target_owner[2:].zfill(64) + logic_addr[2:].zfill(64)
data = "0xdd62ed3e" + params

try:
    res = w3.eth.call({'to': logic_addr, 'data': data})
    permiso = int(res.hex(), 16)
    print(f"📊 Permiso detectado: {permiso} Wei")
    
    if permiso > 0:
        print(f"🔥 ¡VULNERABILIDAD! El contrato tiene poder sobre {w3.from_wei(permiso, 'ether')} ETH.")
    else:
        print("🔒 El permiso directo está en 0. Buscando acceso vía fallback...")
        
except Exception as e:
    print(f"❌ Error en la sonda: {e}")
