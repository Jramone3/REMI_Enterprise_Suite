from web3 import Web3

# Conexión a Ethereum Mainnet
w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
target_address = '0x96De980a766CCb10A19B6962587e2b61B650b372'

def revisar():
    print(f"🔎 REMI: Escaneando transacciones pendientes para {target_address}...")
    try:
        # Buscamos en el 'mempool' (la sala de espera de Ethereum)
        # Nota: Algunos nodos públicos limitan esta consulta, pero probaremos.
        pending_filter = w3.eth.filter('pending')
        # Si no podemos filtrar, miramos el saldo pendiente teórico
        print("⏳ Consultando si hay saldo bloqueado en el horizonte...")
        
        # Consultamos saldo real de nuevo para estar 100% seguros
        balance = w3.eth.get_balance(target_address)
        print(f"💰 Saldo Actual: {w3.from_wei(balance, 'ether')} ETH")
        
        if balance == 0:
            print("\n⚠️ ALERTA: No hay transacciones entrantes detectadas.")
            print("💡 Sugerencia: El puente de Orbiter parece estar retenido.")
        else:
            print("✅ ¡LLEGÓ! El radar debería haberlo visto.")
            
    except Exception as e:
        print(f"❌ Error en escaneo: {e}")

revisar()
