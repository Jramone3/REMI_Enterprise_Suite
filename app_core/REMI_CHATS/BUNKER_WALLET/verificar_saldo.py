from web3 import Web3
import os

def consultar_tokens_bsc():
    # Nodo de Binance Smart Chain
    url = 'https://bsc-dataseed.binance.org/'
    
    # Contratos comunes en BSC (USDT, USDC y Binance-Peg ETH)
    tokens = {
        'USDT (BEP20)': '0x55d398326f99059fF775485246999027B3197955',
        'USDC (BEP20)': '0x8AC76a01213606441541108074019747128c600c',
        'ETH (Binance-Peg)': '0x2170Ed0880ac9A755fd29B2688956BD959F933F8'
    }
    
    ruta_dir = "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/BUNKER_WALLET/direccion_publica.txt"
    with open(ruta_dir, "r") as f:
        address = f.read().strip()

    w3 = Web3(Web3.HTTPProvider(url))
    clean_address = w3.to_checksum_address(address)
    
    print(f"--- 🕵️‍♂️ ESCANEO DE BÓVEDA (BINANCE SMART CHAIN) ---")
    print(f"BILLETERA: {clean_address}\n")

    # Balance de BNB (Gas)
    bnb_balance = w3.from_wei(w3.eth.get_balance(clean_address), 'ether')
    print(f"⛽ BNB (Gas): {bnb_balance:.4f}")

    min_abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]

    for nombre, contrato_addr in tokens.items():
        try:
            contrato = w3.eth.contract(address=w3.to_checksum_address(contrato_addr), abi=min_abi)
            raw_balance = contrato.functions.balanceOf(clean_address).call()
            decimales = contrato.functions.decimals().call()
            balance_final = raw_balance / (10 ** decimales)
            
            if balance_final > 0:
                print(f"✅ {nombre}: {balance_final:.2f} USD/V")
            else:
                print(f"❌ {nombre}: 0.00")
        except:
            print(f"⚠️ Error en contrato {nombre}")

if __name__ == "__main__":
    consultar_tokens_bsc()
