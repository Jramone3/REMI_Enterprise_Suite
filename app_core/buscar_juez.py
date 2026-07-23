from web3 import Web3

# Orbiter usa contratos MDC para arbitraje. Vamos a buscar el de Ethereum/Base.
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# Dirección del MDC (según registros de Orbiter)
mdc_address = '0x10f3F7f26dEcC4ae7A1E1f04313f8373322E73B9' 

print(f"🕵️‍♂️ REMI: Investigando al 'Juez' (Contrato MDC) de Orbiter...")

try:
    balance = w3.eth.get_balance(w3.to_checksum_address(mdc_address))
    print(f"💰 Fondos de Reserva en el Juez: {w3.from_wei(balance, 'ether')} ETH")
    if balance > 0:
        print("⚖️ Hay fondos para compensación. Si el gas no llega en 24h, podemos iniciar arbitraje.")
    else:
        print("❌ El Juez no tiene fondos. Esto confirmaría un abandono total.")
except:
    print("❌ No se pudo conectar con el contrato de arbitraje.")
