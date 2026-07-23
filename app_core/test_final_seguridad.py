from web3 import Web3

# Usamos el nodo más estable para la verificación
w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))

llaves = {
    "FANTASMA REAL (Gasolinera)": "0x28c6c1a33a6eafbd55e70d565f6f2599432ce6419265ffeb106f6e3fe7807172",
    "GATILLO A (Percutor)": "0x589f10559f34606f99abd479688d8be9501d08a2e51f7c6895024839c49f656a",
    "NODO B (Sifón)": "0xf0d4f993d117ee86b9a6c8d0e5232d795a08db1bc4c14044ed54feba94ab2485"
}

print(f"\n🛡️  AUDITORÍA DE PRE-LANZAMIENTO REMI")
print("=" * 60)

for nombre, key in llaves.items():
    try:
        acct = w3.eth.account.from_key(key)
        balance = w3.eth.get_balance(acct.address)
        balance_pol = w3.from_wei(balance, 'ether')
        
        print(f"📡 {nombre}:")
        print(f"   🔓 Dirección: {acct.address}")
        print(f"   💰 Saldo Actual: {balance_pol:.6f} POL")
        print(f"   ✅ ESTADO: LLAVE MAESTRA OPERATIVA")
        print("-" * 60)
    except Exception as e:
        print(f"❌ ERROR EN {nombre}: {e}")

print("💡 NOTA: Si el saldo es 0.00, es normal. Solo esperamos el gas.")
print("=" * 60)
