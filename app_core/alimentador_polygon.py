from web3 import Web3
import time

w3 = Web3(Web3.HTTPProvider('https://1rpc.io/matic'))

def obtener_ballenas_recientes():
    print("🎣 Pescando transacciones grandes en Polygon...")
    block = w3.eth.get_block('latest', full_transactions=True)
    ballenas = []
    
    for tx in block.transactions:
        # Filtro: Transacciones de más de 15,000 POL (aprox $10k)
        if tx.value > w3.to_wei(15000, 'ether'):
            if tx.to and tx.to not in ballenas:
                ballenas.append(tx.to)
    
    return ballenas

if __name__ == "__main__":
    lista = obtener_ballenas_recientes()
    if lista:
        print(f"✅ Se encontraron {len(lista)} objetivos potenciales.")
        with open("os.path.expanduser("~/") + Escritorio/Proyecto_Remi_IA_App/targets.txt", "a") as f:
            for addr in lista:
                f.write(addr + "\n")
