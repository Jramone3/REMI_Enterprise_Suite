import requests
from web3 import Web3

# Conexión rápida a Base
w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
PROXY_ADDR = "0x3AC05161b76a35c1c28dC99Aa01BEd7B24cEA3bf"
IMP_ADDR = "0xcCB20AA0413ea73C50142F1CFf461b07f5ae5e48"

def ejecutar_extraccion():
    print(f"\n{'='*50}")
    print(f" 🤖 OPERACIÓN 'POLVO DE ORO' - REMI V2.5")
    print(f"{'='*50}")

    # 1. Verificar Balance en tiempo real
    balance_wei = w3.eth.get_balance(PROXY_ADDR)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    
    print(f"💰 BOTÍN ACTUAL: {balance_eth} ETH (~${float(balance_eth)*2040:.2f})")

    # 2. Análisis de "Puertas Traseras" (Backdoors)
    # Buscamos firmas de funciones que mueven ETH (Call, Transfer, Send)
    code = w3.eth.get_code(IMP_ADDR).hex()
    
    # OPCODES de transferencia: F1 (CALL), F2 (CALLCODE), F4 (DELEGATECALL)
    print(f"🔍 Escaneando {len(code)//2} bytes de ADN de la Corporación...")
    
    puntos_fuga = []
    if "f1" in code: puntos_fuga.append("CALL (Envío de ETH)")
    if "ff" in code: puntos_fuga.append("SELFDESTRUCT (Botón de pánico)")
    if "a9059cbb" in code: puntos_fuga.append("ERC20_TRANSFER (Robo de Tokens)")

    if puntos_fuga:
        print(f"🚩 GRIETAS ENCONTRADAS: {', '.join(puntos_fuga)}")
    else:
        print("🛡️ El contrato parece blindado o usa librerías oscuras.")

    # 3. El Locker del Dueño
    # El storage 0 suele guardar al dueño o el estado del vault
    storage_root = w3.eth.get_storage_at(PROXY_ADDR, 0).hex()
    print(f"🔑 LLAVE MAESTRA (Slot 0): {storage_root}")

    print(f"\n{'='*50}")
    if balance_wei > 0:
        print("👉 CONSEJO DE SOCIA: El oro sigue ahí. Si no eres el dueño,")
        print("   necesitamos encontrar el 'Function Selector' que")
        print("   no esté protegido por el modificador onlyOwner.")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    ejecutar_extraccion()
