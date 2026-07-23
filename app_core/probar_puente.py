from web3 import Web3

# Conectamos a Base para ver salida
w3_base = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
wallet = w3_base.to_checksum_address('0x96De980a766CCb10A19B6962587e2b61B650b372')

print(f"🌉 GENY: Calculando puente de Base a Ethereum...")

try:
    balance_base = w3_base.eth.get_balance(wallet)
    print(f"💰 Tienes {w3_base.from_wei(balance_base, 'ether')} ETH en Base.")
    
    if balance_base < 0.01:
        print("⚠️  AVISO: El saldo en Base es muy bajo para pagar el peaje del puente hacia Ethereum.")
    else:
        print("✅ Saldo suficiente para intentar un Bridge.")

except Exception as e:
    print(f"❌ Error: {e}")
