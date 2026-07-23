from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://1rpc.io/matic'))

target = w3.to_checksum_address('0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf')

# Direcciones de los diferentes establos en Polygon
TOKENS = {
    'USDC (Nativo)': '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
    'USDC (Bridged/Viejo)': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
    'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
    'DAI': '0x8f3Cf7ad23Cd3BaDDb9135994124182104F63143'
}

abi = '[{"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

print(f"\n📡 --- CAZADOR DE TOKENS: OBJETIVO POLYGON ---")

try:
    # 1. Saldo POL
    print(f"💰 Saldo Nativo: {w3.from_wei(w3.eth.get_balance(target), 'ether')} POL")

    # 2. Barrido de Tokens
    for nombre, direccion in TOKENS.items():
        contrato = w3.eth.contract(address=w3.to_checksum_address(direccion), abi=abi)
        # Algunos tokens tienen 6 decimales (USDC/USDT) y otros 18 (DAI)
        raw_balance = contrato.functions.balanceOf(target).call()
        
        # Ajuste de decimales rápido
        decimales = 6 if 'USD' in nombre else 18
        balance_final = raw_balance / (10**decimales)
        
        if balance_final > 0:
            print(f"💵 {nombre}: {balance_final} 🔥")
        else:
            print(f"⚪ {nombre}: 0.0")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"--- FIN DEL REPORTE ---\n")
