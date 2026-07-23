from web3 import Web3
import time

# Conexión a Optimism
w3 = Web3(Web3.HTTPProvider('https://mainnet.optimism.io'))

print('\n🕵️‍♂️ GENY: MODO CENTINELA ACTIVADO EN OPTIMISM...')
print('🔭 Vigilando nacimientos en tiempo real. Presiona Ctrl+C para detener.')

last_block = w3.eth.block_number

while True:
    try:
        current_block = w3.eth.block_number
        if current_block > last_block:
            for i in range(last_block + 1, current_block + 1):
                block = w3.eth.get_block(i, full_transactions=True)
                print(f'📦 Escaneando bloque {i}... ({len(block.transactions)} txs)')
                for tx in block.transactions:
                    if tx['to'] is None: # Es una creación de contrato
                        receipt = w3.eth.get_transaction_receipt(tx['hash'])
                        addr = receipt.contractAddress
                        bal = w3.eth.get_balance(addr)
                        
                        if bal > 0:
                            print(f'\n🚨 ¡ALERTA DE TESORO! 🚨')
                            print(f'📍 Contrato: {addr}')
                            print(f'💰 Saldo: {w3.from_wei(bal, "ether")} ETH')
                            print(f'🔗 Hash: {tx["hash"].hex()}\n')
            last_block = current_block
        time.sleep(2) # Espera 2 segundos para el siguiente bloque
    except Exception as e:
        print(f'⏳ Reintentando conexión...')
        time.sleep(5)
