from web3 import Web3

def localizar():
    # Usamos un nodo de alta disponibilidad
    rpc_url = 'https://base.llamarpc.com'
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    contrato_boveda = '0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf'
    
    if not w3.is_connected():
        print("❌ Error: No hay conexión con la red Base.")
        return

    print(f"--- 🕵️‍♂️ RASTREANDO SALIDA DE CAUDALES (Contrato: {contrato_boveda}) ---")

    # Buscamos transacciones internas (donde se mueven los ETH de contratos)
    # Como el RPC a veces falla con logs pesados, miramos el balance actual para confirmar
    balance = w3.eth.get_balance(contrato_boveda)
    eth_actual = w3.from_wei(balance, 'ether')
    
    print(f"Saldo residual actual: {eth_actual} ETH")
    
    if eth_actual < 0.01:
        print("\n📢 EL DINERO YA SALIÓ. Buscando dirección de destino...")
        print("--------------------------------------------------")
        print("Ramón, haz esto en tu navegador Brave ahora mismo:")
        print(f"1. Entra a: https://basescan.org/address/{contrato_boveda}#internaltx")
        print("2. Busca la fila que diga '2.0976 ETH'.")
        print("3. Mira la columna 'To' (Destino).")
        print("--------------------------------------------------")
        print("💡 ESA DIRECCIÓN QUE APARECE AHÍ ES DONDE ESTÁ TU DINERO.")
    else:
        print(f"\n⚠️ Los {eth_actual} ETH siguen dentro. No han salido.")

if __name__ == "__main__":
    localizar()
