from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# Aplicamos el parche de seguridad de direcciones
bunker = w3.to_checksum_address('0x6a8a0ec01dfe9e8bc385c743204e674ed705dafc')

def check():
    try:
        bal = w3.eth.get_balance(bunker)
        print(f"\n🏰 ESTADO DEL BÚNKER RAMÓN (Red: Base)")
        print(f"💰 Saldo Actual: {w3.from_wei(bal, 'ether')} ETH")
        print(f"🔗 Explorador: https://basescan.org/address/{bunker}")
    except Exception as e:
        print(f"❌ Error en la red: {e}")

if __name__ == "__main__":
    check()
