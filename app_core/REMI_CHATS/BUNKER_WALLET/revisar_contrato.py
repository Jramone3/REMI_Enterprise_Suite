from web3 import Web3

def revisar():
    w3 = Web3(Web3.HTTPProvider('https://base.drpc.org'))
    contrato = '0xe4EdB277e4122137966EFC68615b3C5890d2979E'
    tu_wallet = '0x96De980a766CCb10A19B6962587e2b61B650b372'
    
    # 1. Saldo en el contrato
    balance_contrato = w3.eth.get_balance(contrato)
    eth_contrato = w3.from_wei(balance_contrato, 'ether')
    
    # 2. Saldo en tu billetera
    balance_wallet = w3.eth.get_balance(tu_wallet)
    eth_wallet = w3.from_wei(balance_wallet, 'ether')
    
    print(f"\n--- 🛰️ REPORTE DE ESTADO (BASE) ---")
    print(f"💰 EN EL CONTRATO (Bóveda): {eth_contrato} ETH")
    print(f"🏦 EN TU BILLETERA (Líquido): {eth_wallet} ETH")
    
    if eth_contrato > 0:
        print("\n⚠️ EL TESORO SIGUE EN EL CONTRATO. No ha salido.")
    elif eth_wallet > 2:
        print("\n✅ ¡ÉXITO! El dinero ya está en tu poder.")
    else:
        print("\n🕵️ El dinero no está en ninguno de los dos. Revisar historial de salida.")

if __name__ == "__main__":
    revisar()

