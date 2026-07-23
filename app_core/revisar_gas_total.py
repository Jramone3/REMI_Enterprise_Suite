from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://1rpc.io/matic'))

cuentas = {
    "Wallet Personal (Destino Final)": "0x96De980a766CCb10A19B6962587e2b61B650b372",
    "Gatillo / Nodo A (El Ejecutor)": "0xB9073c07648a414B875874d7B8599dD2fAa171E8"
}

print(f"\n📡 MONITOR DE RED POLYGON - ESPERANDO ORBITER")
print("-" * 50)

for nombre, addr in cuentas.items():
    balance = w3.eth.get_balance(addr)
    pol = w3.from_wei(balance, 'ether')
    print(f"📍 {nombre}:")
    print(f"   Dirección: {addr}")
    print(f"   Saldo: {pol} POL")
    print("-" * 50)

if w3.eth.get_balance(cuentas["Gatillo / Nodo A (El Ejecutor)"]) > 10**17:
    print("✅ ¡LISTO! El Gatillo tiene combustible.")
else:
    print("⏳ Pendiente: El Gatillo aún no tiene suficiente POL para operar.")
