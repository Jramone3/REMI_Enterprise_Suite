from web3 import Web3
import time

# Conexión a Ethereum Mainnet
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))

# La dirección del contrato donde está el botín (3.78 ETH)
contrato_botin = '0x80C67432656d59144cEFf962E8fAF8926599bCF8'

def revisar_objetivo():
    try:
        # 1. Revisar Saldo Actual
        balance_wei = w3.eth.get_balance(contrato_botin)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        # 2. Revisar última transacción (para ver si alguien lo tocó)
        bloque_actual = w3.eth.block_number
        
        print(f"\n--- 🛰️ INFORME DE RADAR - OBJETIVO: {contrato_botin} ---")
        print(f"💰 SALDO ACTUAL: {balance_eth} ETH")
        print(f"💵 VALOR ESTIMADO: ${round(float(balance_eth) * 2200, 2)} USD")
        print(f"📦 BLOQUE ACTUAL: {bloque_actual}")
        
        if balance_eth >= 3.78:
            print("✅ ESTADO: ESTABLE. El botín sigue intacto.")
        elif balance_eth > 0:
            print("⚠️ ESTADO: DISMINUIDO. El dueño está retirando fondos.")
        else:
            print("🚨 ESTADO: VACÍO. El objetivo ha sido evacuado.")
            
        return balance_eth
    except Exception as e:
        print(f"❌ Error de escaneo: {e}")
        return None

# Ejecución única para reporte inmediato
revisar_objetivo()
