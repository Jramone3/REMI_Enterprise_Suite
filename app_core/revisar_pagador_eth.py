from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# El "Maker" que debería enviarte el dinero en Mainnet
pagador_orbiter_eth = '0x80C67432656d59144cEFf962E8fAF8926599bCF8'

print(f"🕵️‍♂️ REMI: Investigando la billetera pagadora en Ethereum...")

try:
    bal = w3.eth.get_balance(w3.to_checksum_address(pagador_orbiter_eth))
    eth = w3.from_wei(bal, 'ether')
    print(f"💰 Saldo del Pagador Orbiter en ETH: {eth} ETH")
    
    if bal < w3.to_wei(0.01, 'ether'):
        print("🚨 ¡ESTÁ SECO! El pagador no tiene fondos para enviarte nada.")
    else:
        print("✅ El pagador TIENE fondos. El problema es su software/bot que está trabado.")
except:
    print("❌ Error de conexión al investigar el pagador.")
